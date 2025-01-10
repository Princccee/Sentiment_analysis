import streamlit as st
import requests

st.title("Sentiment Analysis on Call Transcripts")

# File uploader
uploaded_file = st.file_uploader("Upload Call Transcript", type=["txt"])
if uploaded_file is not None:
    transcript = uploaded_file.read().decode("utf-8")
    st.text_area("Transcript Content", transcript, height=300)

    # Send to backend for analysis
    if st.button("Analyze Sentiment"):
        response = requests.post(
            "http://127.0.0.1:5000/analyze", 
            files={"file": uploaded_file}
        )
        if response.status_code == 200:
            st.write("Sentiment Analysis Result:")
            st.json(response.json())
        else:
            st.error("Error in sentiment analysis.")
