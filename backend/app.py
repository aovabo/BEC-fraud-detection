import os
import json
import requests
import sqlite3
import hashlib
import time
import logging
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from paymanai import Paymanai  # Correct import
from paymanai.errors import PaymanError  # Error handling
from langchain.chat_models import ChatOpenAI
from langchain.schema import AIMessage, HumanMessage, SystemMessage
from typing import Union
from decimal import Decimal

# Load environment variables
load_dotenv()

PAYMAN_API_SECRET = os.getenv("PAYMAN_API_SECRET")
PAYMAN_ENVIRONMENT = os.getenv("PAYMAN_ENVIRONMENT", "sandbox")  # Use 'sandbox' for testing
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Initialize Flask app
app = Flask(__name__)

# Initialize Payman AI Client
payman = Paymanai(
    x_payman_api_secret=PAYMAN_API_SECRET,
    environment=PAYMAN_ENVIRONMENT
)

# Initialize LangChain AI Agent
llm = ChatOpenAI(model="gpt-4", temperature=0, openai_api_key=OPENAI_API_KEY)

# Configure logging
logging.basicConfig(level=logging.INFO)

# Ensure database exists for tracking transactions
def init_db():
    conn = sqlite3.connect("transactions.db")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS transactions (id TEXT PRIMARY KEY, vendor TEXT, amount REAL, status TEXT)")
    conn.commit()
    conn.close()

init_db()

# Generate unique transaction ID
def generate_transaction_id(email_text, vendor, amount):
    return hashlib.sha256(f"{email_text}{vendor}{amount}".encode()).hexdigest()

# AI Fraud Detection using LangChain Agent
def analyze_email(email_text):
    try:
        response = llm([SystemMessage(content="Analyze the following email for fraud risk. Respond in JSON with `fraudulent` (true/false) and `reason`."),
                        HumanMessage(content=email_text)])
        fraud_analysis = json.loads(response.content)
        return fraud_analysis
    except Exception as e:
        logging.error(f"AI Fraud Detection Error: {e}")
        return {"fraudulent": False, "reason": "AI unavailable, defaulting to safe."}

# Send Slack Alerts for Fraud Detection
def send_slack_alert(vendor, amount, reason):
    if not SLACK_WEBHOOK_URL:
        logging.warning("Slack webhook not configured. Skipping alert.")
        return
    message = {"text": f"🚨 Fraud Alert: Potential BEC Detected 🚨\nVendor: {vendor}\nAmount: ${amount}\nReason: {reason}"}
    try:
        requests.post(SLACK_WEBHOOK_URL, json=message)
    except requests.exceptions.RequestException as e:
        logging.error(f"Slack notification failed: {e}")

# Centralized Payman API Error Handling
def handle_api_error(response):
    try:
        error_data = response.json()
        error_code = error_data.get("errorCode", "unknown_error")
        error_message = error_data.get("message", "An unexpected error occurred.")
        trace_id = error_data.get("traceId", "N/A")

        logging.error(f"Payman API Error: {error_code} | {error_message} | Trace ID: {trace_id}")

        error_mapping = {
            "not_authorized": "Invalid API key. Please check your credentials.",
            "insufficient_funds": "Insufficient funds to complete the transaction.",
            "validation_error": "Invalid payment details. Please check the input fields.",
            "entity_not_found": "Requested resource was not found.",
            "not_allowed": "You do not have permission to perform this action.",
        }

        user_friendly_message = error_mapping.get(error_code, error_message)

        return jsonify({
            "status": "Failed",
            "error": user_friendly_message,
            "traceId": trace_id
        }), response.status_code

    except Exception as e:
        logging.error(f"Error parsing Payman API response: {e}")
        return jsonify({"status": "Failed", "error": "Unexpected error occurred."}), 500

# ✅ **Process Payment Using Payman AI**
@app.route("/process_payment", methods=["POST"])
def process_payment():
    data = request.json
    transaction_id = generate_transaction_id(data["email_text"], data["payment_details"]["vendor"], data["payment_details"]["amount"])

    # Prevent duplicate transactions
    conn = sqlite3.connect("transactions.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM transactions WHERE id = ?", (transaction_id,))
    if cursor.fetchone():
        conn.close()
        return jsonify({"status": "Duplicate", "message": "This transaction has already been processed."}), 409

    fraud_result = analyze_email(data["email_text"])

    if fraud_result["fraudulent"]:
        send_slack_alert(data["payment_details"]["vendor"], data["payment_details"]["amount"], fraud_result["reason"])
        conn.close()
        return jsonify({"status": "Blocked", "message": "Potential BEC detected!", "reason": fraud_result["reason"]}), 403

    # Process Payment Using Payman AI
    try:
        payment = payman.payments.send_payment(
            amount_decimal=data["payment_details"]["amount"],
            payment_destination_id=data["payment_details"]["vendor"],
            memo="Invoice Payment",
            customer_email=data["customer"]["email"],
            customer_name=data["customer"]["name"]
        )

        cursor.execute("INSERT INTO transactions (id, vendor, amount, status) VALUES (?, ?, ?, ?)",
                       (transaction_id, data["payment_details"]["vendor"], data["payment_details"]["amount"], "Success"))
        conn.commit()
        conn.close()
        return jsonify({"status": "Success", "transaction_reference": payment.reference}), 200
    except PaymanError as e:
        return jsonify({"status": "Failed", "error": e.message}), 400

# ✅ **Check AI Agent Balance**
@app.route("/check_agent_balance", methods=["GET"])
def check_agent_balance():
    currency = request.args.get("currency", "USD")

    try:
        agent_balance = payman.balances.get_spendable_balance(currency)
        return jsonify({"status": "Success", "agent_balance": float(agent_balance)}), 200
    except PaymanError as e:
        return jsonify({"status": "Failed", "error": e.message}), 400

# ✅ **Webhook Event Handler**
@app.route("/webhook", methods=["POST"])
def handle_webhook():
    event = request.json

    if "eventType" not in event or "details" not in event:
        logging.warning("Received malformed webhook event.")
        return jsonify({"status": "Failed", "error": "Malformed event"}), 400

    event_type = event["eventType"]
    event_details = event["details"]

    logging.info(f"Received webhook event: {event_type}")

    if event_type == "customer-deposit.successful":
        logging.info(f"Deposit successful for Customer {event_details.get('customerId')}")
    elif event_type == "customer-deposit.failed":
        logging.warning(f"Deposit FAILED for Customer {event_details.get('customerId')}")
    else:
        logging.warning(f"Unhandled webhook event: {event_type}")

    return jsonify({"status": "Success", "message": "Webhook event processed"}), 200

# ✅ **Run Flask App**
if __name__ == "__main__":
    app.run(debug=True)
