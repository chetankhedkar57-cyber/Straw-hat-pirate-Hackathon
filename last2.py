from flask import Flask, request, render_template_string
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB

app = Flask(__name__)

# ------------------ AI TRAINING DATA ------------------

training_messages = [
    "Payment successful",
    "Money credited to your account",
    "You received 500 rupees",
    "Transaction completed",
    "Approve collect request",
    "Enter UPI PIN to receive reward",
    "Urgent request approve now",
    "You won prize claim now",
    "Click link to get cashback",
    "Verify your account immediately"
]

training_labels = [
    0, 0, 0, 0,   # Safe
    1, 1, 1, 1, 1, 1  # Scam
]

vectorizer = CountVectorizer()
X_train = vectorizer.fit_transform(training_messages)

model = MultinomialNB()
model.fit(X_train, training_labels)

# ------------------ AI DETECTION FUNCTION ------------------

def ai_detect_scam(message):
    X_test = vectorizer.transform([message])
    prediction = model.predict(X_test)[0]
    probability = model.predict_proba(X_test)[0][1]
    return prediction, int(probability * 100)

# ------------------ FLASK ROUTE ------------------

@app.route("/", methods=["GET", "POST"])
def home():
    risk = 0
    reasons = []
    warning = None
    color = "green"

    if request.method == "POST":
        sender = request.form["sender"]
        upi_id = request.form["upi_id"]
        txn_type = request.form["txn_type"]
        amount = request.form["amount"]
        message = request.form["message"]

        prediction, ai_risk = ai_detect_scam(message)
        risk = ai_risk

        if prediction == 1:
            reasons.append("AI detected scam-like message pattern")

        if txn_type == "Request":
            risk += 15
            reasons.append("Money Request transaction")

        if float(amount) > 5000:
            risk += 15
            reasons.append("High transaction amount")

        if risk >= 60:
            warning = "🚨 AI ALERT: High Fraud Risk!"
            color = "red"
        elif risk >= 30:
            color = "orange"
        else:
            color = "green"

        if risk > 100:
            risk = 100

    return render_template_string("""
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>AI UPI Protection</title>
<style>
body {margin:0;font-family:Arial;background:#f2f2f2;}
.header {background:#1e272e;color:white;padding:18px;text-align:center;font-size:20px;}
.container {padding:20px;}
.card {background:white;padding:20px;border-radius:15px;box-shadow:0 5px 15px rgba(0,0,0,0.1);}
input, select, textarea {
    width:100%;padding:12px;margin-top:6px;margin-bottom:15px;
    border-radius:8px;border:1px solid #ccc;
}
button {
    width:100%;padding:14px;background:#0fbcf9;color:white;
    border:none;border-radius:10px;font-weight:bold;
}
.risk-bar {height:18px;border-radius:8px;margin-top:10px;}
.warning {
    background:red;color:white;padding:18px;
    border-radius:10px;margin-top:20px;font-weight:bold;text-align:center;
}
</style>
</head>
<body>

<div class="header">
🛡 AI Powered UPI Scam Detection
</div>

<div class="container">
<div class="card">

<form method="post">
<label>Sender Name / Number</label>
<input name="sender" required>

<label>UPI ID</label>
<input name="upi_id" placeholder="example@upi" required>

<label>Transaction Type</label>
<select name="txn_type">
    <option>Send</option>
    <option>Receive</option>
    <option>Request</option>
</select>

<label>Amount (₹)</label>
<input name="amount" type="number" required>

<label>Notification Message</label>
<textarea name="message" rows="3" required></textarea>

<button type="submit">Analyze Transaction</button>
</form>

{% if risk > 0 %}
<div style="margin-top:20px;">
Risk Score: {{risk}}%
<div class="risk-bar" style="width:{{risk}}%; background: {{color}};"></div>
</div>

<h4>Indicators:</h4>
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
{% endif %}

</div>
</div>

</body>
</html>
""", risk=risk, warning=warning, color=color, reasons=reasons)

if __name__ == "__main__":
    app.run(debug=True)