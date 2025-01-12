import streamlit as st
import requests

st.title("Sentiment Analysis on Call Transcripts")

# File uploader
uploaded_file = st.file_uploader("Upload Call Transcript", type=["txt"])
if uploaded_file is not None:
    transcript = uploaded_file.read().decode("utf-8")  # Explicitly decode the content
    st.text_area("Transcript Content", transcript, height=300)

    # Reset the file pointer to the beginning for sending
    uploaded_file.seek(0) 
    

    if st.button("Analyze Sentiment"):
        try:
            # Send the file to the backend
            response = requests.post(
                "https://flask-backend-rxff.onrender.com/analyze",  # deployed Flask backend URL
                files={"file": ("transcript.txt", uploaded_file, "text/plain")}
            )

            if response.status_code == 200:
                st.write("Sentiment Analysis Result:")
                st.json(response.json())
            else:
                st.error("Error in sentiment analysis.")
                st.write("Debug: Backend Response:")
                st.json(response.json())
        except requests.exceptions.RequestException as e:
            st.error("Failed to connect to the backend. Please ensure the server is running.")
            st.write(f"Debug: {e}")
