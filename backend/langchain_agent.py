import os
import json
import requests
from langchain.chat_models import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
from paymanai import Paymanai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PAYMAN_API_SECRET = os.getenv("PAYMAN_API_SECRET")
PAYMAN_ENVIRONMENT = os.getenv("PAYMAN_ENVIRONMENT", "sandbox")

# Initialize LangChain AI Agent
llm = ChatOpenAI(model_name="gpt-4", openai_api_key=OPENAI_API_KEY)

# Initialize Payman AI Client
payman = Paymanai(
    x_payman_api_secret=PAYMAN_API_SECRET,
    environment=PAYMAN_ENVIRONMENT
)

def analyze_email(email_text):
    """AI analyzes email text for BEC fraud risk."""
    response = llm([
        SystemMessage(content="You are an AI specialized in detecting Business Email Compromise (BEC) fraud."),
        HumanMessage(content=f"Analyze this email:\n\n{email_text}\n\nReturn JSON response: {{'fraudulent': true/false, 'reason': '...'}}")
    ])

    try:
        return json.loads(response.content)
    except json.JSONDecodeError:
        return {"fraudulent": False, "reason": "AI error, unable to analyze"}

def process_payment_request(email_text, payment_details):
    """Handles fraud detection and processes payments securely."""
    fraud_result = analyze_email(email_text)

    if fraud_result["fraudulent"]:
        return {"status": "Blocked", "message": "Potential BEC detected!", "reason": fraud_result["reason"]}, 403

    try:
        payment = payman.payments.send_payment(
            amount_decimal=payment_details["amount"],
            payment_destination_id=payment_details["vendor"],
            memo="Invoice payment"
        )
        return {"status": "Success", "transaction": payment}, 200
    except Exception as e:
        return {"status": "Failed", "error": str(e)}, 500
