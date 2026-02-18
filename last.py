from flask import Flask, request, render_template_string
import re

app = Flask(__name__)

# ---------------- FRAUD DETECTION ENGINE ----------------

def detect_scam(message, amount, sender):
    risk_score = 0
    reasons = []

    keywords = ["request", "collect", "upi pin", "approve", "claim reward", "receive money"]

    for word in keywords:
        if word.lower() in message.lower():
            risk_score += 20
            reasons.append(f"Suspicious keyword detected: '{word}'")

    if amount and float(amount) > 5000:
        risk_score += 20
        reasons.append("High transaction amount")

    if re.search(r"\d{10}", sender):
        risk_score += 10
        reasons.append("Unknown sender phone number")

    if "request" in message.lower() and "pin" in message.lower():
        risk_score += 40
        reasons.append("UPI PIN entry for payment request detected")

    return risk_score, reasons


@app.route("/", methods=["GET", "POST"])
def home():
    warning = None
    risk = 0
    reasons = []
    color = "green"

    if request.method == "POST":
        sender = request.form["sender"]
        amount = request.form["amount"]
        message = request.form["message"]

        risk, reasons = detect_scam(message, amount, sender)

        if risk >= 60:
            warning = "🚨 STOP! You are SENDING money, not receiving it!"
            color = "red"
        elif risk >= 30:
            color = "orange"
        else:
            color = "green"

    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Anti-Scam UPI Protection</title>
        <style>
            body {
                font-family: Arial;
                background: linear-gradient(to right, #eef2f3, #8e9eab);
                padding: 40px;
            }
            .container {
                background: white;
                padding: 30px;
                border-radius: 12px;
                max-width: 650px;
                margin: auto;
                box-shadow: 0 10px 25px rgba(0,0,0,0.2);
            }
            h1 {
                text-align: center;
            }
            .top-img {
                display: block;
                margin: auto;
                width: 120px;
            }
            input, textarea {
                width: 100%;
                padding: 10px;
                margin-top: 5px;
                margin-bottom: 15px;
                border-radius: 6px;
                border: 1px solid #ccc;
            }
            button {
                width: 100%;
                padding: 12px;
                background: #007bff;
                color: white;
                font-size: 16px;
                border: none;
                border-radius: 6px;
                cursor: pointer;
            }
            button:hover {
                background: #0056b3;
            }
            .risk-box {
                padding: 15px;
                margin-top: 20px;
                border-radius: 8px;
                color: white;
                font-weight: bold;
                text-align: center;
            }
            .warning {
                background: red;
                color: white;
                padding: 20px;
                font-size: 22px;
                font-weight: bold;
                text-align: center;
                border-radius: 10px;
                margin-top: 20px;
                animation: blink 1s infinite;
            }
            @keyframes blink {
                50% { opacity: 0.6; }
            }
            .footer-img {
                width: 100%;
                margin-top: 20px;
                border-radius: 10px;
            }
        </style>
    </head>
    <body>

    <div class="container">

        <img class="top-img" src="https://cdn-icons-png.flaticon.com/512/3064/3064197.png">

        <h1>🛡 Anti-Scam UPI Protection</h1>
        <p style="text-align:center;">Protecting Senior Citizens from Digital Payment Fraud</p>

        <form method="post">
            <label>Sender Name / Number</label>
            <input name="sender" required>

            <label>Amount (₹)</label>
            <input name="amount" type="number" required>

            <label>Notification Message</label>
            <textarea name="message" rows="4" required></textarea>

            <button type="submit">Analyze Transaction</button>
        </form>

        {% if risk > 0 %}
            <div class="risk-box" style="background: {{color}};">
                Risk Score: {{risk}}%
            </div>

            <h3>Analysis:</h3>
            <ul>
                {% for r in reasons %}
                    <li>{{r}}</li>
                {% endfor %}
            </ul>
        {% endif %}

        {% if warning %}
            <div class="warning">
                {{warning}}
            </div>
            <img class="footer-img" src="https://cdn-icons-png.flaticon.com/512/564/564619.png">
        {% endif %}

    </div>

    </body>
    </html>
    """, risk=risk, reasons=reasons, warning=warning, color=color)


if __name__ == "__main__":
    app.run(debug=True)