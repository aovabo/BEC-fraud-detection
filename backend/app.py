import os
import json
import requests
import time
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from paymanai import Paymanai
from langchain.chat_models import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage

# Load environment variables
load_dotenv()

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PAYMAN_API_SECRET = os.getenv("PAYMAN_API_SECRET")
PAYMAN_ENVIRONMENT = os.getenv("PAYMAN_ENVIRONMENT", "sandbox")
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")

# Initialize Flask app
app = Flask(__name__)

# Initialize LangChain AI for fraud detection
llm = ChatOpenAI(model_name="gpt-4", openai_api_key=OPENAI_API_KEY)

# Initialize Payman AI Client
payman = Paymanai(
    x_payman_api_secret=PAYMAN_API_SECRET,
    environment=PAYMAN_ENVIRONMENT
)

# ------------------------------
# ✅ AI Fraud Detection (LangChain)
# ------------------------------
def analyze_email(email_text):
    """AI analyzes email text for BEC fraud risk."""
    response = llm([
        SystemMessage(content="You are an AI specializing in Business Email Compromise (BEC) fraud detection."),
        HumanMessage(content=f"Analyze this email:\n\n{email_text}\n\nReturn JSON response: {{'fraudulent': true/false, 'reason': '...'}}")
    ])

    try:
        return json.loads(response.content)
    except json.JSONDecodeError:
        return {"fraudulent": False, "reason": "AI error, unable to analyze"}

# ------------------------------
# ✅ Slack Alerts
# ------------------------------
def send_slack_alert(vendor, amount, reason):
    """Sends a Slack alert for potential fraudulent transactions."""
    if not SLACK_WEBHOOK_URL:
        print("⚠️ Slack Webhook not configured!")
        return

    message = {
        "text": f"🚨 Fraud Alert: Potential BEC Detected 🚨\nVendor: {vendor}\nAmount: ${amount}\nReason: {reason}"
    }
    requests.post(SLACK_WEBHOOK_URL, json=message)

# ------------------------------
# ✅ Process Payment Request
# ------------------------------
@app.route("/process_payment", methods=["POST"])
def process_payment():
    """Handles fraud detection and securely processes payments."""
    data = request.json
    email_text = data.get("email_text")
    payment_details = data.get("payment_details")

    # Step 1: AI Fraud Detection
    fraud_result = analyze_email(email_text)

    if fraud_result["fraudulent"]:
        send_slack_alert(payment_details["vendor"], payment_details["amount"], fraud_result["reason"])
        return jsonify({"status": "Blocked", "message": "Potential BEC detected!", "reason": fraud_result["reason"]}), 403

    # Step 2: Securely Process Payment via Payman API (with retries)
    return execute_payment_with_retries(payment_details)

# ------------------------------
# ✅ Secure Payment Execution with Retries
# ------------------------------
def execute_payment_with_retries(payment_details, retries=3):
    """Retries the payment execution if Payman API fails."""
    for attempt in range(retries):
        try:
            payment = payman.payments.send_payment(
                amount_decimal=payment_details["amount"],
                payment_destination_id=payment_details["vendor"],
                memo="Invoice payment"
            )
            return jsonify({"status": "Success", "transaction": payment}), 200
        except Exception as e:
            print(f"⚠️ Payman API failed, retrying... ({attempt + 1}/{retries})")
            time.sleep(2)  # Wait before retrying

    return jsonify({"status": "Failed", "error": "Payman API unavailable after retries."}), 500

# ------------------------------
# ✅ Create Payee Endpoint (for New Vendors)
# ------------------------------
@app.route("/create_payee", methods=["POST"])
def create_payee():
    """Creates a new payment destination before sending funds."""
    data = request.json

    try:
        payee = payman.payments.create_payee(
            type="US_ACH",
            name=data["name"],
            account_holder_name=data["account_holder_name"],
            account_number=data["account_number"],
            routing_number=data["routing_number"],
            account_type=data["account_type"],
            contact_details={
                "email": data["email"],
                "phone_number": data["phone_number"]
            }
        )
        return jsonify({"status": "Success", "payee_id": payee["id"]}), 200
    except Exception as e:
        return jsonify({"status": "Failed", "error": str(e)}), 500

# ------------------------------
# ✅ Check Balance Endpoint
# ------------------------------
@app.route("/check_balance", methods=["GET"])
def check_balance():
    """Checks the AI Agent's available balance in USD."""
    try:
        balance = payman.balances.get_spendable_balance("USD")
        return jsonify({"status": "Success", "balance": balance}), 200
    except Exception as e:
        return jsonify({"status": "Failed", "error": str(e)}), 500

# ------------------------------
# ✅ Webhook Handling (For Real-Time Payman Events)
# ------------------------------
@app.route("/webhook", methods=["POST"])
def webhook():
    """Handles real-time events from Payman AI."""
    event = request.json

    if event["eventType"] == "customer-deposit.successful":
        print(f"💰 Deposit received: ${event['details']['amount'] / 100}")
    elif event["eventType"] == "approval-request.rejected":
        send_slack_alert("Admin", "N/A", "A payment request was rejected.")
    
    return jsonify({"status": "Received"}), 200

# ------------------------------
# ✅ Run Flask Server
# ------------------------------
if __name__ == "__main__":
    app.run(debug=True)
