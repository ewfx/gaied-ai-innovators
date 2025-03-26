import os
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect
from django.http import JsonResponse
from .utils.email_content_extractor import EmailProcessorFromWeb

# Directory to store uploaded email files
UPLOAD_DIR = "uploaded_emails"
os.makedirs(UPLOAD_DIR, exist_ok=True)


def upload_email_page(request):
    message = request.GET.get('message', '')
    return render(request, "upload_email.html", {"message": message})


@csrf_exempt
def upload_email(request):
    if request.method == "POST" and request.FILES.get("email_file"):
        email_file = request.FILES["email_file"]
        file_path = os.path.join(UPLOAD_DIR, email_file.name)

        # Save the uploaded file
        with open(file_path, "wb") as destination:
            for chunk in email_file.chunks():
                destination.write(chunk)

        if request.headers.get('Accept') == 'application/json':
            return JsonResponse({"message": "Email file uploaded successfully", "file_path": file_path})
        return redirect("/emailclassifier/upload-page/?message=Email+file+uploaded+successfully!")

    if request.content_type == 'application/json':
        return JsonResponse({"error": "Invalid request or missing file"}, status=400)
    return redirect("/emailclassifier/upload-page/?message=Invalid+request+or+missing+file")


@csrf_exempt
def process_uploaded_email(request):
    """Process uploaded email, extract data, and classify it."""
    if request.method == 'POST' and request.FILES.get('email_file'):
        email_file = request.FILES['email_file']
        file_path = f"processing/{email_file.name}"

        # Save the uploaded file
        with open(file_path, 'wb') as f:
            for chunk in email_file.chunks():
                f.write(chunk)


        # Initialize and use EmailClassifier
        emailprocessorfromweb = EmailProcessorFromWeb()
        classification_result = emailprocessorfromweb.process_email_classification(file_path)
        return JsonResponse(classification_result)

    return JsonResponse({"error": "Invalid request or missing file"}, status=400)
