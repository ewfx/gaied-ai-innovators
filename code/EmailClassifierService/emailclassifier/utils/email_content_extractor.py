import json
import pytesseract
import os
import extract_msg
import re
from pypdf import PdfReader
import watchdog.events
import watchdog.observers
import time
import uuid
import shutil
from pdf2image import convert_from_path
from emailclassifier.utils.email_type_classifier import EmailTypeClassifer,QDRANT_CLIENT

UPLOAD_DIR = "uploaded_emails"

def get_attachment_text(attachment_file):
    """Extract text from PDFs or use OCR for scanned PDFs."""
    print('PdfContentToExtract:'+attachment_file)
    reader = PdfReader(attachment_file)
    attachment_text = ''

    for page in reader.pages:
        text = page.extract_text()
        if text:
            attachment_text += text + " "
        else:
            # Convert scanned PDF page to image and apply OCR
            images = convert_from_path(attachment_file)
            for img in images:
                ocr_text = pytesseract.image_to_string(img)
                attachment_text += ocr_text + " "

    return attachment_text

def delete_attachment(attachment_file):
    try:
        os.remove(attachment_file)
    except Exception as e:
        print("Failed to delete attachment file: " + attachment_file)

def extract_email_content(msg_mail_path):
    """Extract email details from .msg files and return JSON."""
    if not msg_mail_path.endswith('.msg'):
        return json.dumps({"error": "Invalid file format"})

    msg = extract_msg.Message(msg_mail_path)
    subject = str(msg.subject)
    fromemail = str(msg.sender)
    received_date = str(msg.date)
    message_body = re.sub(r"[\n\r]+", " ", str(msg.body))

    output_folder_attachments = "tempextract"
    os.makedirs(output_folder_attachments, exist_ok=True)
    finalattachmenttext = ''
    attachment_paths = []
    # Extract attachments and read their text
    for attachment in msg.attachments:
        if attachment.longFilename:
            unique_id = str(uuid.uuid4())[:4]
            attachmentfilename = attachment.longFilename
            msg.saveAttachments(customPath=output_folder_attachments, customFilename=attachmentfilename)
            attachmentpath = output_folder_attachments + '/' + attachmentfilename
            attachment_paths.append(attachmentpath)

    msg.close()

    for path in attachment_paths:
        extracted_text = get_attachment_text(path)
        finalattachmenttext = finalattachmenttext + extracted_text

    attachmentastext = re.sub(r"[\n\r]+", " ", finalattachmenttext)
    email_data = {
        "subject": subject,
        "from": fromemail,
        "received_date": received_date,
        "Content": message_body,
        "Attachments": attachmentastext
    }
    print(email_data)

    for path in attachment_paths:
        delete_attachment(path)
    # Delete .msg file after processing
    try:
        os.remove(msg_mail_path)
    except Exception as e:
        email_data["error"] = f"Failed to delete .msg file: {str(e)}"
    return email_data


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


def write_response_toKafka(classification_result, email_data):
    # As this POC instead of kafka writing it locally
    unique_id = str(uuid.uuid4())[:4]
    # Clean subject (remove special characters and spaces)
    clean_subject = re.sub(r'[^A-Za-z0-9]', '', email_data["subject"])
    # Get received date
    received_date = email_data.get("received_date", "UnknownDate").replace(" ", "_")
    clean_subject_recdate = re.sub(r'[^A-Za-z0-9\-]', '', received_date)
    # Generate filename
    filename = f"{clean_subject}_{clean_subject_recdate}_{unique_id}.json"
    # Save to JSON file
    output_dir = 'output-files'
    os.makedirs(output_dir, exist_ok=True)  # Ensure directory exists
    file_path = os.path.join(output_dir, filename)

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(classification_result, f, indent=4)


def initiate_email_classification(event_path):
    new_file_path = move_file_to_processing(event_path)
    email_data = extract_email_content(new_file_path)
    emailtypeclassifer = EmailTypeClassifer(qdrant_client=QDRANT_CLIENT)
    classification_result = emailtypeclassifer.classify_email(email_data)
    print(classification_result)
    write_response_toKafka(classification_result,email_data)

class EmailProcessorFromWeb:
    def process_email_classification(new_file_path):
        email_data = extract_email_content(new_file_path)
        emailtypeclassifer = EmailTypeClassifer(qdrant_client=QDRANT_CLIENT)
        classification_result = emailtypeclassifer.classify_email(email_data)
        return classification_result

class EmailFileHandler(watchdog.events.PatternMatchingEventHandler):
    """Watch for new .msg files and extract content."""
    def __init__(self):
        watchdog.events.PatternMatchingEventHandler.__init__(self, patterns=["*.msg"], ignore_directories=True)

    def on_created(self, event):
        print(f"New email detected: {event.src_path}")
        time.sleep(2)  # Delay to ensure file is fully written
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
