import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
# Load environment variables from .env file
load_dotenv()


# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Directory to store uploaded files
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Create the folder if it doesn't exist
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Hugging Face API URL and authentication
API_URL = "https://api-inference.huggingface.co/models/cardiffnlp/twitter-roberta-base-sentiment-latest"
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY") # Get the API key from environment variables
if not HUGGINGFACE_API_KEY:
    raise ValueError("HUGGINGFACE_API_KEY not found in environment variables")
headers = {
    "Authorization": f"Bearer {HUGGINGFACE_API_KEY}"
}

# Function to preprocess the transcript
def preprocess_transcript(transcript):
    """Parse the transcript into individual statements for each speaker."""
    conversation = []
    lines = transcript.replace("\r\n", "\n").strip().split("\n")  # Normalize line breaks
    current_speaker = None
    current_statement = []

    for line in lines:
        line = line.strip()  # Remove leading/trailing whitespace

        if line.startswith("[Sales Agent"):
            if current_speaker and current_statement:
                conversation.append((current_speaker, " ".join(current_statement)))
            current_speaker = "Sales Agent"
            current_statement = [line.split("]")[-1].strip()]
        elif line.startswith("[Customer"):
            if current_speaker and current_statement:
                conversation.append((current_speaker, " ".join(current_statement)))
            current_speaker = "Customer"
            current_statement = [line.split("]")[-1].strip()]
        else:
            if current_statement is not None:
                current_statement.append(line.strip())

    if current_speaker and current_statement:
        conversation.append((current_speaker, " ".join(current_statement)))

    return conversation

# Function to analyze sentiment using the Hugging Face API
def analyze_sentiment_via_api(text):
    response = requests.post(API_URL, headers=headers, json={"inputs": text})
    if response.status_code == 200:
        return response.json()  # Get sentiment result from the API response
    else:
        raise Exception(f"API request failed with status code {response.status_code}")

# Function to extract sentiment lists
def extract_sentiment_lists(agent_sentiments, customer_sentiments):
    """Return a list of sentiment labels for each individual."""
    agent_sentiment_list = [entry["sentiment"] for entry in agent_sentiments]
    customer_sentiment_list = [entry["sentiment"] for entry in customer_sentiments]

    return {
        "agent": agent_sentiment_list,
        "customer": customer_sentiment_list
    }

# Function to compute overall sentiment
def compute_overall_sentiment(agent_sentiments, customer_sentiments):
    """Compute the overall sentiment score for the conversation."""
    sentiment_weights = {"positive": 1, "neutral": 0, "negative": -1}

    agent_score = sum(sentiment_weights[sentiment] for sentiment in agent_sentiments)
    customer_score = sum(sentiment_weights[sentiment] for sentiment in customer_sentiments)

    total_score = agent_score + customer_score
    total_statements = len(agent_sentiments) + len(customer_sentiments)
    normalized_score = total_score / total_statements if total_statements > 0 else 0

    if normalized_score > 0:
        overall_sentiment = "positive"
    elif normalized_score < 0:
        overall_sentiment = "negative"
    else:
        overall_sentiment = "neutral"

    return {
        "total_score": total_score,
        "normalized_score": normalized_score,
        "overall_sentiment": overall_sentiment
    }

# API route to analyze sentiment
@app.route("/analyze", methods=["POST"])
def analyze():
    """API route for analyzing sentiment."""
    # Check if a file was uploaded
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "Empty file"}), 400

    # Save the file to the uploads folder
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
    file.save(file_path)

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            transcript = f.read()
    except Exception as e:
        return jsonify({"error": f"Failed to read the file: {e}"}), 500

    # Parse the transcript
    conversation = preprocess_transcript(transcript)
    if not conversation:
        return jsonify({"error": "Parsing failed. Ensure the file has the correct format."}), 400

    agent_sentiments = []
    customer_sentiments = []

    for speaker, text in conversation:
        try:
            # Use external API to analyze sentiment
            result = analyze_sentiment_via_api(text)
            sentiment_label = result[0]["label"].lower()

            if speaker == "Sales Agent":
                agent_sentiments.append({"statement": text, "sentiment": sentiment_label})
            elif speaker == "Customer":
                customer_sentiments.append({"statement": text, "sentiment": sentiment_label})
        except Exception as e:
            print(f"Error analyzing sentiment for: {text[:50]}... -> {e}")

    sentiment_lists = extract_sentiment_lists(agent_sentiments, customer_sentiments)
    overall_sentiment = compute_overall_sentiment(sentiment_lists["agent"], sentiment_lists["customer"])

    return jsonify({"overall_sentiment": overall_sentiment})

# Start the Flask app
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Use port from environment or default to 5000
    app.run(host="0.0.0.0", port=port)  # Listen on all public IPs
