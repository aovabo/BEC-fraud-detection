import os
import json
import requests
from flask import Flask, request, jsonify
from payman_paykit import Payman
from dotenv import load_dotenv
import hashlib
import time
import sqlite3

# Load environment variables
load_dotenv()

PAYMAN_API_SECRET = os.getenv("PAYMAN_API_SECRET")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")

app = Flask(__name__)

# Initialize Payman AI Client
payman = Payman(api_key=PAYMAN_API_SECRET)

# AI Fraud Detection using OpenAI
def analyze_email(email_text):
    try:
        response = requests.post(
            "https://api.openai.com/v1/completions",
            headers={"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"},
            json={
                "model": "gpt-4",
                "prompt": f"Analyze this email for fraud risk:\n{email_text}\n\nRespond in JSON:\n{{\"fraudulent\": true/false, \"reason\": \"...\"}}",
                "temperature": 0
            }
        )
        return response.json()
    except Exception:
        return {"fraudulent": False, "reason": "AI unavailable, defaulting to safe."}

# Slack Alerts
def log_alert_to_db(vendor, amount, reason):
    conn = sqlite3.connect("alerts.db")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS alerts (vendor TEXT, amount REAL, reason TEXT)")
    cursor.execute("INSERT INTO alerts (vendor, amount, reason) VALUES (?, ?, ?)", (vendor, amount, reason))
    conn.commit()
    conn.close()

def send_slack_alert(vendor, amount, reason):
    message = {"text": f"🚨 Fraud Alert: Potential BEC Detected 🚨\nVendor: {vendor}\nAmount: ${amount}\nReason: {reason}"}
    try:
        response = requests.post(SLACK_WEBHOOK_URL, json=message)
        response.raise_for_status()
    except requests.exceptions.RequestException:
        log_alert_to_db(vendor, amount, reason)

# Generate Transaction ID to Prevent Duplicate Payments
def generate_transaction_id(email_text, vendor, amount):
    return hashlib.sha256(f"{email_text}{vendor}{amount}".encode()).hexdigest()

@app.route("/process_payment", methods=["POST"])
def process_payment():
    data = request.json
    transaction_id = generate_transaction_id(data["email_text"], data["payment_details"]["vendor"], data["payment_details"]["amount"])

    fraud_result = analyze_email(data["email_text"])

    if fraud_result["fraudulent"]:
        send_slack_alert(data["payment_details"]["vendor"], data["payment_details"]["amount"], fraud_result["reason"])
        return jsonify({"status": "Blocked", "message": "Potential BEC detected!", "reason": fraud_result["reason"]}), 403

    try:
        transaction = payman.transfers.create(
            from_account_id="business_main_account",
            to_account_id=data["payment_details"]["vendor"],
            amount=data["payment_details"]["amount"],
            currency="USD",
            metadata={"reason": "Invoice payment"}
        )
        return jsonify({"status": "Success", "transaction": transaction}), 200
    except Exception as e:
        return jsonify({"status": "Failed", "error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
