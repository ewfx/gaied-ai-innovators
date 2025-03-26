import os
import watchdog.events
import watchdog.observers
import time
import shutil
from emailclassifier.utils.email_content_extractor import EmailContentExtractor

UPLOAD_DIR = "uploaded_emails"

def move_file_to_processing(file_path):
    """Move a file from its current location to the processing folder."""

    processing_folder = "processing"

    # Ensure processing folder exists
    os.makedirs(processing_folder, exist_ok=True)

    # Extract the file name from the full path
    file_name = os.path.basename(file_path)

    # Define the destination path
    destination_path = os.path.join(processing_folder, file_name)

    try:
        # Move the file
        shutil.move(file_path, destination_path)
        print(f"File moved to: {destination_path}")
        return destination_path
    except FileNotFoundError:
        print(f"Error: {file_path} not found")
    except Exception as e:
        print(f"Error moving file: {str(e)}")
    return destination_path


def initiate_email_classification(event_path):
    new_file_path = move_file_to_processing(event_path)
    emailcontentextractor = EmailContentExtractor()
    emailcontentextractor.processemailClassification(new_file_path)

def wait_for_file_stability(file_path, wait_time=2, check_interval=0.5):
    """Waits until the file size remains unchanged for a given period."""
    prev_size = -1
    while wait_time > 0:
        try:
            current_size = os.path.getsize(file_path)
            if current_size == prev_size:
                return True  # File size is stable
            prev_size = current_size
        except FileNotFoundError:
            return False  # File was moved or deleted
        time.sleep(check_interval)
        wait_time -= check_interval
    return False

class EmailFileHandler(watchdog.events.PatternMatchingEventHandler):
    """Watch for new .msg files and extract content."""
    def __init__(self):
        watchdog.events.PatternMatchingEventHandler.__init__(self, patterns=["*.msg"], ignore_directories=True)

    def on_created(self, event):
        print(f"New email detected: {event.src_path}")
        # time.sleep(2)  # Delay to ensure file is fully written
        if wait_for_file_stability(event.src_path):
            initiate_email_classification(event.src_path)

    def on_modified(self, event):
        print("Watchdog received modified event % s." % event.src_path)
        # Event is modified, you can process it now

def start_email_watcher():
    """Start the watchdog observer to watch the upload directory."""
    observer = watchdog.observers.Observer()
    event_handler = EmailFileHandler()
    observer.schedule(event_handler, path=UPLOAD_DIR, recursive=False)
    observer.start()
    print("Email watcher started.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
