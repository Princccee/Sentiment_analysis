from flask import Flask, request, jsonify
from transformers import pipeline

app = Flask(__name__)
sentiment_analyzer = pipeline("sentiment-analysis")

@app.route("/analyze", methods=["POST"])
def analyze_sentiment():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files["file"]
    content = file.read().decode("utf-8")
    
    # Perform sentiment analysis
    result = sentiment_analyzer(content)
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)
