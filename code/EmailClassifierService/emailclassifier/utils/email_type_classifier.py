from qdrant_client import models, QdrantClient
import json
from llama_index.embeddings.gemini import GeminiEmbedding
import google.generativeai as genai

QDRANT_CLIENT = QdrantClient(":memory:")

COLLECTION_NAME = "service_tickets"
if COLLECTION_NAME not in [col.name for col in QDRANT_CLIENT.get_collections().collections]:
    QDRANT_CLIENT.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=models.VectorParams(
            size=768,  # Vector size is defined by the used model
            distance=models.Distance.COSINE,
        ),
    )

class EmailTypeClassifer:
    def __init__(self, qdrant_client):
        """Initialize the Email Classifier with Qdrant and Gemini models."""
        self.api_key = 'AIzaSyDBOqBMpQHp7tMFPhHtTl7YhtRNHseuynA'
        self.qdrant_client = qdrant_client  #Use the shared Qdrant instance

        # Configure Gemini model
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(
            model_name="gemini-2.0-flash",
            system_instruction="You are a commercial banking analyst, who classifies service tickets coming via email."
        )

        # Configure Embedding Model
        e_model_name = "models/embedding-001"
        self.embed_model = GeminiEmbedding(
            model_name=e_model_name, api_key=self.api_key
        )

    def classify_email(self,email):

        final_response_json = self.model.generate_content(
            contents="""Analyze the provided email subject, content, and attachments, extract key banking attributes, summary and classify the request into a service request type and sub-request type from the predefined classification list.

    Instructions:
    Extract relevant banking attributes (e.g., Account Number, Transaction Amount, Loan ID, Payment Due Date, Wire Transfer Reference, etc.) from the email subject, body, and attachments.

    Classify the request into a Service Request Type and Sub-Request Type based on predefined categories.

    Assign a confidence score (0.00 - 1.00) based on classification certainty.

    If the request does not fit any category, return "requestType": "Unclassified".

    Ensure the output is a valid JSON object without explanations, markdown, or extra text.

    Output Format:
    {
      "requestType": "<Determined Service Request Type>",
      "subRequestType": "<Determined Sub Request Type>",
      "confidenceScore": <Determined Score>,
      "summary": "<Determined Summary for the email>",
      "extractedAttributes": {
        "Attribute 1": "Value 1",
        "Attribute 2": "Value 2"
      }
    }
    Example 1
    Email Details:
    Subject: Urgent - Wire Transfer Delay
    Body: Our client has initiated a wire transfer of $200,000 to Account Number 987654, but it hasn’t been credited yet. Please investigate.
    Attachment: Wire transfer confirmation (PDF)

    Output:
    {
      "requestType": "Money Movement - Inbound",
      "subRequestType": "Wire Transfer - Incoming",
      "confidenceScore": 0.92,
      "summary": "Wire Transfer of $200,000 for Account Number 987654 not credited",
      "extractedAttributes": {
        "Transaction Amount": "$200,000",
        "Account Number": "987654"
      }
    }
    Example 2
    Email Details:
    Subject: Loan Payment Inquiry
    Body: The customer wants to make a $25,000 loan repayment. Please confirm the payoff amount and instructions.
    Attachment: Loan payoff statement (PDF)
    Output:
    {
      "requestType": "Loan Servicing",
      "subRequestType": "Payoff Request",
      "confidenceScore": 0.95,
      "summary": "wanted $25000 loan repayment, help with amount and instructions",
      "extractedAttributes": {
        "Transaction Amount": "$25,000"
      }
    }
    Example 3 (Unclassified Request)
    Email Details:
    Subject: Inquiry about Investment Options
    Body: A customer is asking about available investment portfolios.
    Output:
    {
      "requestType": "Unclassified",
      "subRequestType": "Unclassified",
      "confidenceScore": 1.00,
      "summary": "inquiry of available investment portfolio",
      "extractedAttributes": {}
    }""" + email["subject"] + email["Attachments"] + email["Content"]
        )
        summary_incoming_email = self.embed_model.get_text_embedding(email["Content"] + email["from"] + email["Attachments"])
        answer = final_response_json.text

        if answer.startswith("```json"):
            answer = answer.strip("```json").strip("```").strip()

        answer_json = json.loads(answer)

        isDuplicate = 0
        hits = self.qdrant_client.query_points(
            collection_name="service_tickets",
            query=summary_incoming_email,
            limit=3,
        ).points

        answer_json["isDuplicate"] = 0
        for hit in hits:
            if (hit.score > 0.8):
                answer_json["isDuplicate"] = 1
                return answer_json

        self.qdrant_client.upload_points(
            collection_name="service_tickets",
            points=[
                models.PointStruct(
                    id=1, vector=summary_incoming_email, payload=email
                )
            ],
        )
        return answer_json


    