# SafeWire AI - AI-Powered BEC Fraud Prevention

## **Use Case & Problem Statement**
### **Understanding the Threat: Business Email Compromise (BEC)**
**Business Email Compromise (BEC)** is a sophisticated cyber scam where attackers impersonate executives, vendors, or trusted parties to deceive businesses into making fraudulent financial transactions. 

### **Why is BEC a Critical Problem?**
- The **FBI’s Internet Crime Complaint Center (IC3) reports that between October 2013 and December 2023, there were 305,033 BEC incidents**, leading to a **total exposed dollar loss of $55.5 billion**.
- In the U.S. alone, there were **158,436 victims** with **$20.08 billion in losses**, while **non-U.S. victims suffered $1.64 billion in losses**.
- **BEC scams are increasing**: Between December 2022 and December 2023, identified global exposed losses increased by **9%**.
- Attackers are now **using custodial accounts at financial institutions, peer-to-peer payment platforms, and cryptocurrency exchanges** to rapidly move stolen funds, making recovery difficult.
- The most common intermediary locations for fraudulent BEC funds in 2023 were **the United Kingdom, Hong Kong, China, Mexico, and the UAE**.

### **Current Solutions & Their Limitations**
1. **Email Security Tools (Proofpoint, Mimecast, Microsoft Defender)**
   - Detect phishing and email anomalies but **cannot stop payments**.
   - No integration with financial transaction systems.

2. **Manual Verification (Phone Calls, Double-Checks)**
   - Time-consuming and prone to human error.
   - Attackers exploit urgency and deception to bypass checks.

3. **Financial Controls (Spend Limits, Payment Delays)**
   - Effective but **inflexible and inconvenient** for businesses needing real-time transactions.
   - Cannot detect fraudulent intent in the request.

### **Why SafeWire AI?**
SafeWire AI bridges the **gap between AI-driven fraud detection and financial transaction security** by:
- **Using AI to analyze payment requests for fraud indicators before execution.**  
- **Integrating with Payman AI to enforce security measures on financial transactions.**  
- **Providing real-time alerts via Slack & Microsoft Teams, enabling instant human intervention.**  
- **Blocking payments to suspicious recipients until manually reviewed and approved.**  
- **Maintaining full audit logs for forensic tracking and compliance.**

For further details, refer to the official FBI IC3 report: [IC3 BEC PSA 2024](https://www.ic3.gov/PSA/2024/PSA240911)

---

## **How SafeWire AI Works with Payman AI**
### **What is Payman AI?**
Payman AI is an **infrastructure provider for AI-driven financial transactions**, similar to Stripe but built for AI agents. SafeWire AI integrates with Payman AI to:
- **Process payments securely** via USD financial rails.
- **Provide virtual financial accounts** for businesses without requiring direct Payman interaction.
- **Enforce spending limits, compliance, and audit logging** for all transactions.

### **How SafeWire AI Prevents BEC Fraud**
SafeWire AI does **not** require businesses (our customers) to create Payman AI accounts directly. Instead, the workflow operates as follows:

1. **A business signs up for SafeWire AI and links its bank account** (via Payman AI infrastructure).
   - The business is assigned a **virtual financial account** inside Payman.
   - This allows **AI-controlled transactions without customers directly using Payman**.

2. **SafeWire AI Fraud Detection Scans Payment Requests**
   - Analyzes emails for fraud risk (spoofed vendors, unusual requests, etc.).
   - Classifies transactions as **low-risk, medium-risk, or high-risk**.

3. **Transaction Decision Based on Risk Level**
   - **Low-risk transactions** → Approved automatically and processed via Payman.
   - **Medium-risk transactions** → Held for manual approval via Slack/Microsoft Teams.
   - **High-risk transactions** → **Blocked before reaching Payman AI**.

4. **Real-Time Slack/Microsoft Teams Alerts**
   - If a transaction is flagged, an alert is sent with **Approve/Reject** options.
   - Finance teams can **approve directly within Slack/Teams**, and Payman AI executes or cancels the payment accordingly.

5. **Execution or Blocking via Payman AI**
   - Approved transactions are **executed through Payman’s financial infrastructure**.
   - If rejected, the payment is **halted before any money moves**.
   - All transactions are **logged for compliance and auditing**.

### **Who Controls the Money?**
- **Businesses still own their funds**—SafeWire AI does not hold any money.
- SafeWire AI **only facilitates secure transactions** using AI fraud detection and Payman AI’s infrastructure.

---

## **Key Features**
- **AI-Powered Fraud Analysis** → Detects fraudulent payment requests before execution.
- **Automated Risk-Based Payment Processing** → Low-risk = auto-approved, high-risk = blocked.
- **Payman AI Virtual Accounts** → Securely holds customer funds without them directly managing Payman.
- **Slack & Microsoft Teams Integration** → Allows instant approvals or rejections by finance teams.
- **Full Audit Logging** → Ensures compliance and forensic tracking of all payment activities.

---

## **Example: Stopping a CEO Fraud Attempt**
### **Scenario:** An accounts payable employee receives an urgent email from their "CEO" requesting a **$50,000 wire transfer** to a new vendor.

1. **AI detects the email as a potential BEC fraud attempt.**
2. **AI halts the transaction before it reaches Payman AI.**
3. **A Slack alert is sent to the finance team:**

   **ALERT: Potential BEC Fraud Detected**  
   - **Vendor:** Fake Business Inc.  
   - **Amount:** $50,000  
   - **Reason:** Unverified payee, urgent request from spoofed CEO email.  

   **✅ Approve | ❌ Reject**  

4. **The finance team clicks Reject, and the transaction is permanently blocked.**
5. **The fraud attempt is logged in Payman AI’s compliance records.**

---

## **Edge Cases & Security Considerations**
- **Handling False Positives** – Provide an override option for finance teams.
- **Preventing Insider Fraud** – Log **who approved payments** in the system.
- **Multi-Layer Authentication** – Enforce **MFA for all high-risk payments**.
- **Preventing System Downtime** – Implement retries & failover handling for API failures.

---

# Payman AI Payment Processing & Fraud Detection API Features

## Overview
This project provides a **secure payment processing API** powered by **Payman AI**, integrating fraud detection with **OpenAI**, transaction monitoring, Slack notifications, and LangChain AI integration for automated decision-making. The API supports:

- **Secure Payment Processing** via Payman AI
- **Fraud Detection & Prevention** using OpenAI
- **Real-time Webhooks for Events** (Deposits, Approvals, Low Balances, etc.)
- **Slack Notifications for Alerts** (Fraud, Payment Failures, etc.)
- **Search & Manage Payees**
- **Create Customer Deposit Links**
- **Check AI Agent & Customer Balances**
- **Production & Sandbox Mode Support**

---

## Tech Stack

| Technology | Purpose |
|------------|---------|
| **Python** | Main backend language |
| **Flask** | API framework |
| **Payman AI SDK** | Payment processing & AI agent integration |
| **OpenAI API** | Fraud detection and email analysis |
| **SQLite** | Local transaction tracking |
| **Slack Webhooks** | Alert notifications |
| **LangChain** | AI-powered automation & agent integration |
| **dotenv** | Environment variable management |

---

## Features & Endpoints

### **1. Secure Payment Processing**
#### Endpoint: `/send_payment` (POST)
- Sends a payment using **Payman AI**.
- Supports **existing payees** and **new destinations**.

#### Request Body:
```json
{
  "paymentDestinationId": "dest_123",
  "amountDecimal": 50.00,
  "memo": "Service payment"
}
```

#### Response:
```json
{
  "status": "Success",
  "payment_reference": "pay_abc123"
}
```

#### Error Handling:
- **Insufficient Funds** → 400
- **Invalid Destination** → 400
- **Unauthorized API Key** → 401
- **Server Issues** → 500

---

### **2. Payee Management**
#### Endpoint: `/create_payee` (POST)
- Creates a **US ACH**, **crypto**, or **Payman AI agent payee**.

#### Request Body:
```json
{
  "type": "US_ACH",
  "name": "John Doe",
  "account_holder_name": "John Doe",
  "account_number": "1234567890",
  "routing_number": "011000138",
  "account_type": "checking",
  "contact_details": { "email": "john@example.com" },
  "tags": ["primary"]
}
```

#### Response:
```json
{
  "status": "Success",
  "payee_id": "dest_123abc"
}
```

---

### **3. Search Payees**
#### Endpoint: `/search_payees` (GET)
- Find existing payees by **name**, **email**, or **type**.

#### Request Example:
```bash
curl -X GET "http://localhost:5000/search_payees?name=John"
```

#### Response:
```json
{
  "status": "Success",
  "payees": [{ "id": "dest_123abc", "name": "John Doe" }]
}
```

---

### **4. Customer Deposits**
#### Endpoint: `/create_deposit` (POST)
- Generates a **checkout link** for customers to deposit funds.

#### Request Body:
```json
{
  "amountDecimal": 100.00,
  "customer_id": "cust_123",
  "customer_email": "customer@example.com"
}
```

#### Response:
```json
{
  "status": "Success",
  "checkout_url": "https://payman.ai/checkout/cust_123"
}
```

---

### **5. Check Balances**
#### Endpoint: `/check_agent_balance` (GET)
- Retrieves AI agent’s available balance.

#### Request:
```bash
curl -X GET "http://localhost:5000/check_agent_balance?currency=USD"
```

#### Response:
```json
{
  "status": "Success",
  "agent_balance": 150.00
}
```

#### Endpoint: `/check_customer_balance` (GET)
- Retrieves a **customer’s** balance.

#### Request:
```bash
curl -X GET "http://localhost:5000/check_customer_balance?customer_id=cust_123"
```

#### Response:
```json
{
  "status": "Success",
  "customer_balance": 50.00
}
```

---

### **6. Webhooks**
#### Endpoint: `/webhook` (POST)
- Listens for real-time **events** (Deposits, Approvals, Failures, etc.).

#### Example Webhook Event:
```json
{
  "eventType": "customer-deposit.successful",
  "details": {
    "customerId": "user_123",
    "amount": 10000,
    "currency": "USD"
  }
}
```

---

## **Setup & Installation**

### **1. Clone the Repository**
```bash
git clone https://github.com/aovabo/safewire-ai.git
cd safewire-ai
```

### **2. Install Dependencies**
```bash
pip install -r requirements.txt
```

### **3. Set Up Environment Variables**
Create a `.env` file:
```
PAYMAN_API_SECRET=your_api_key
PAYMAN_ENVIRONMENT=sandbox  # Change to 'production' for live mode
SLACK_WEBHOOK_URL=your_slack_webhook
```

### **4. Run the Application**
```bash
python app.py
```

The API will be accessible at `http://localhost:5000`.

---

## **Hosting & Deployment**
### **Option 1: Docker**
#### **Run with Docker**
```bash
docker build -t payman-api .
docker run -p 5000:5000 --env-file .env payman-api
```

### **Option 2: Deploy to AWS/GCP/Vercel**
Use **Gunicorn** for production:
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

---

## **Using Sandbox vs. Production Mode**
| Mode | API URL | API Key |
|------|--------|---------|
| **Sandbox** | `https://agent-sandbox.payman.ai/api` | `sk_test_...` |
| **Production** | `https://agent.payman.ai/api` | `sk_live_...` |

To switch **environments**, change `PAYMAN_ENVIRONMENT` in `.env`:
```
PAYMAN_ENVIRONMENT=production  # Use 'sandbox' for testing
```

---

## **Security Best Practices**
- **Do NOT expose API keys in public repositories**.
- **Use environment variables for configuration**.
- **Enable Slack alerts for fraud detection**.
- **Use Payman AI’s Webhooks to track payments.**

---

## **Contributing**
1. Fork the repository
2. Create a feature branch
3. Submit a pull request

---

## **License**
This project is licensed under the MIT License.



