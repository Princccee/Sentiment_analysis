# Sentiment Analysis on Phone Call Transcripts

This project is a web-based application that performs sentiment analysis on uploaded call transcripts. Users can upload text files through a Streamlit-based UI, and the backend, powered by Flask, processes the files and returns sentiment analysis results.

The app uses a pre-trained Hugging Face Transformer model to classify sentiments into Positive, Negative, or Neutral, along with corresponding sentiment scores.

![Sentiment Analysis](home.png)

## Project Structure

```
sentiment-analysis/
├── backend
│   └── app.py
|   └── demo.py    # to ananlyse the file locally on terminal
├── frontend
│   └── streamlit_app.py
├── readme.md
├── requirements.txt
├── .gitignore
└── readme.md               
```

## Getting Started

### Prerequisites

- Python 3.11.11
- Required Python packages (listed in `requirements.txt`)

### Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/Princccee/Sentiment_analysis.git
    ```
2. Create a virtual environment:
    ```sh
    python3 -m venv .venv
    source .venv/bin/activate
    ```    
3. Navigate to the project directory:
    ```sh
    cd sentiment-analysis
    ```
4. Install the required packages:
    ```sh
    pip install -r requirements.txt
    ```
5. Run the backend server:
    ```sh
    python backend/app.py
    ```
6. Run the streamlit app in browser:
    ```sh
    streamlit run frontend/streamlit_app.py
    ```    
