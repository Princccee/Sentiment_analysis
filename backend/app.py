from flask import Flask, request, jsonify
from transformers import pipeline

"""
This module implements a Flask web application for sentiment analysis using the Hugging Face Transformers library.
Routes:
    /analyze (POST): Analyzes the sentiment of the text content in the uploaded file.
Functions:
    analyze_sentiment(): Handles the sentiment analysis of the uploaded file content.
Usage:
    Run this script to start the Flask web server. Use the /analyze endpoint to upload a text file and get the sentiment analysis result.
Dependencies:
    - Flask
    - transformers
Example:
    To run the application, execute the script and send a POST request to the /analyze endpoint with a text file.
"""


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
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
