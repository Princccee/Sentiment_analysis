from flask import Flask, request, jsonify
from transformers import pipeline

# Initialize Flask app
app = Flask(__name__)

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
        if line.startswith("[Sales Agent"):
            # Save the previous statement if it exists
            if current_speaker and current_statement:
                conversation.append((current_speaker, " ".join(current_statement)))
            # Start a new statement
            current_speaker = "Sales Agent"
            current_statement = [line.split("]")[-1].strip()]
        elif line.startswith("[Customer"):
            # Save the previous statement if it exists
            if current_speaker and current_statement:
                conversation.append((current_speaker, " ".join(current_statement)))
            # Start a new statement
            current_speaker = "Customer"
            current_statement = [line.split("]")[-1].strip()]
        else:
            # Continue building the current statement
            current_statement.append(line.strip())

    # Append the last statement
    if current_speaker and current_statement:
        conversation.append((current_speaker, " ".join(current_statement)))

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

            # Append the sentiment to the corresponding list
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

@app.route("/analyze", methods=["POST"])
def analyze():
    """API route for analyzing sentiment."""
    try:
        # Check if a file was uploaded
        if "file" not in request.files:
            return jsonify({"error": "No file uploaded"}), 400

        # Read the uploaded file
        file = request.files["file"]

        # Check if the file is empty
        if file.filename == "":
            return jsonify({"error": "Empty file"}), 400

        # Read and decode the file
        transcript = file.read().decode("utf-8").replace("\r\n", "\n")  # Normalize line breaks
        print("Received Transcript Content:", transcript)  # Debug: Log raw content

        # Parse the transcript
        conversation = preprocess_transcript(transcript)
        print("Parsed Conversation:", conversation)  # Debug: Log parsed conversation

        # Return error if parsing failed
        if not conversation:
            return jsonify({"error": "Parsing failed. Ensure the file has the correct format."}), 400

        # Analyze sentiment
        agent_sentiments, customer_sentiments = analyze_sentiment(conversation)

        # Extract sentiment lists
        sentiment_lists = extract_sentiment_lists(agent_sentiments, customer_sentiments)

        # Return the results
        return jsonify({
            "sales_agent_sentiments": agent_sentiments,
            "customer_sentiments": customer_sentiments,
            "sentiment_lists": sentiment_lists
        })

    except Exception as e:
        print(f"Error in /analyze route: {e}")  # Log the error
        return jsonify({"error": f"An unexpected error occurred: {e}"}), 500


# Direct file input analysis for testing
def analyze_from_file(file_path):
    """Analyze sentiment directly from a .txt file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            transcript = f.read()

        # Preprocess and analyze sentiment
        conversation = preprocess_transcript(transcript)
        agent_sentiments, customer_sentiments = analyze_sentiment(conversation)

        # Extract sentiment lists
        sentiment_lists = extract_sentiment_lists(agent_sentiments, customer_sentiments)

        # Print the results
        results = {
            "sales_agent_sentiments": agent_sentiments,
            "customer_sentiments": customer_sentiments,
            "sentiment_lists": sentiment_lists
        }
        print("Analysis Results:")
        print(results)
    except FileNotFoundError:
        print(f"File not found: {file_path}")
    except Exception as e:
        print(f"Error processing file: {e}")

# Run the Flask app
if __name__ == "__main__":
    # Uncomment to analyze from a file directly for testing
    analyze_from_file("transcripts/8938805598_carol.das@upgrad.com_2024-02-20-14-45-45.txt")

    app.run(debug=True)
