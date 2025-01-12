import os
from flask import Flask, request, jsonify
from transformers import pipeline

# Initialize Flask app
app = Flask(__name__)

# Directory to store uploaded files
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Create the folder if it doesn't exist
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Initialize sentiment analysis pipeline
sentiment_analyzer = pipeline("sentiment-analysis", model="cardiffnlp/twitter-roberta-base-sentiment-latest")

# Function to preprocess the transcript
def preprocess_transcript(transcript):
    """Parse the transcript into individual statements for each speaker."""
    conversation = []
    lines = transcript.replace("\r\n", "\n").strip().split("\n")  # Normalize line breaks
    current_speaker = None
    current_statement = []

    for line in lines:
        line = line.strip()  # Remove leading/trailing whitespace
        # print(f"Processing Line: '{line}'")  # Debug: Log each line being processed

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

    # print("Parsed Conversation:", conversation)  # Debug
    return conversation

# Function to analyze sentiment
def analyze_sentiment(conversation):
    """Analyze sentiment for each statement in the conversation."""
    agent_sentiments = []
    customer_sentiments = []

    for speaker, text in conversation:
        try:
            # Get sentiment result for the statement
            result = sentiment_analyzer(text)[0]
            sentiment_label = result["label"].lower()

            if speaker == "Sales Agent":
                agent_sentiments.append({"statement": text, "sentiment": sentiment_label})
            elif speaker == "Customer":
                customer_sentiments.append({"statement": text, "sentiment": sentiment_label})
        except Exception as e:
            print(f"Error analyzing sentiment for: {text[:50]}... -> {e}")

    return agent_sentiments, customer_sentiments

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
    # Assign numerical weights to each sentiment
    sentiment_weights = {"positive": 1, "neutral": 0, "negative": -1}

    # Compute scores for agent and customer
    agent_score = sum(sentiment_weights[sentiment] for sentiment in agent_sentiments)
    customer_score = sum(sentiment_weights[sentiment] for sentiment in customer_sentiments)

    # Total score
    total_score = agent_score + customer_score

    # Normalize the score (optional)
    total_statements = len(agent_sentiments) + len(customer_sentiments)
    normalized_score = total_score / total_statements if total_statements > 0 else 0

    # Determine overall sentiment based on the normalized score
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


@app.route("/analyze", methods=["POST"])
def analyze():
    """API route for analyzing sentiment."""
    # Check if a file was uploaded
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]

    # Check if the file is empty
    if file.filename == "":
        return jsonify({"error": "Empty file"}), 400

    # Save the file to the uploads folder
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
    file.save(file_path)
    # print(f"File saved to {file_path}")  # Debug: Log the file path

    # Read the saved file
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            transcript = f.read()
        # print("Transcript Content:", transcript)  # Debug: Log raw content
    except Exception as e:
        return jsonify({"error": f"Failed to read the file: {e}"}), 500

    # Parse the transcript
    conversation = preprocess_transcript(transcript)
    if not conversation:
        return jsonify({"error": "Parsing failed. Ensure the file has the correct format."}), 400

    # Analyze sentiment
    agent_sentiments, customer_sentiments = analyze_sentiment(conversation)

    # Extract sentiment lists
    sentiment_lists = extract_sentiment_lists(agent_sentiments, customer_sentiments)

    # Compute overall sentiment
    overall_sentiment = compute_overall_sentiment(
        sentiment_lists["agent"], sentiment_lists["customer"]
    )

    # Return the results
    return jsonify({
        # "sales_agent_sentiments": agent_sentiments,
        # "customer_sentiments": customer_sentiments,
        # "sentiment_lists": sentiment_lists,
        "overall_sentiment": overall_sentiment
    })

# Start the Flask app
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Use port from environment or default to 5000
    app.run(host="0.0.0.0", port=port)  # Listen on all public IPs
