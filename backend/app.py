import os
import json
import requests
import sqlite3
import hashlib
import time
from flask import Flask, request, jsonify
from payman_paykit import Payman
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

PAYMAN_API_SECRET = os.getenv("PAYMAN_API_SECRET")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")

app = Flask(__name__)

# Initialize Payman AI Client
payman = Payman(api_key=PAYMAN_API_SECRET)

# Ensure database exists
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
def send_slack_alert(vendor, amount, reason):
    message = {"text": f"🚨 Fraud Alert: Potential BEC Detected 🚨\nVendor: {vendor}\nAmount: ${amount}\nReason: {reason}"}
    try:
        requests.post(SLACK_WEBHOOK_URL, json=message)
    except requests.exceptions.RequestException:
        print("Slack notification failed.")

# API: Process Payment
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

    # Process transaction with Payman
    try:
        transaction = payman.transfers.create(
            from_account_id="business_main_account",
            to_account_id=data["payment_details"]["vendor"],
            amount=data["payment_details"]["amount"],
            currency="USD",
            metadata={"reason": "Invoice payment"}
        )
        cursor.execute("INSERT INTO transactions (id, vendor, amount, status) VALUES (?, ?, ?, ?)",
                       (transaction_id, data["payment_details"]["vendor"], data["payment_details"]["amount"], "Success"))
        conn.commit()
        conn.close()
        return jsonify({"status": "Success", "transaction": transaction}), 200
    except Exception as e:
        return jsonify({"status": "Failed", "error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
