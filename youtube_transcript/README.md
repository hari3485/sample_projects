# 🎥 YouTube Transcript QA System with Streamlit + AWS + Bedrock KB

This project allows users to input a **YouTube video URL**, extract its **transcript**, upload it to **Amazon S3**, index it in **Amazon Bedrock Knowledge Base**, and ask context-based questions about the video using **LLM** (Large Language Model). The responses are shown with **timestamps**, and clicking on a timestamp opens the video at that exact moment.

---

## 🚀 Features

- 🔗 Input any YouTube video URL
- 📄 Extract English transcripts using **YouTube Transcript API**
- ☁️ Upload transcripts to **AWS S3**
- 📚 Send transcripts to **Bedrock Knowledge Base** and auto-index
- 🤖 Ask questions using LLM (ChatGPT via Bedrock/Flotorch)
- ⏱️ Get answers with timestamps
- 🔘 Clickable timestamps open YouTube at that point
- 🌐 Clean Streamlit UI for interaction

---

## 🗂️ Project Structure

    ├── app.py # Streamlit frontend for user input & interaction
    ├── utils.py # Helper functions: transcript extraction, S3 upload
    ├── llm.py # Handles LLM query and response retrieval
    ├── requirements.txt # Python dependencies
    └── README.md # Project documentation


---

## ⚙️ Requirements

- Python 3.8+
- streamlit
- boto3
- openai
- python-dotenv
- youtube-transcript-api
- flotorch_core


Install Python packages:
```bash
pip install -r requirements.txt
```

## 🔐 .env Configuration

To run this project, create a `.env` file in the root directory with the following content:


    AWS_ACCESS_KEY_ID=your_aws_access_key_id
    AWS_SECRET_ACCESS_KEY=your_aws_secret_access_key
    AWS_REGION=us-east-1
    AWS_KNOWNLEDGE_BASE_ID=your_kb_id_here
    DATA_SOURCE_ID=your_data_source_id_here
    API_KEY=your-flotorch-api-key
    BASE_URL=your-flotorch-endpoint.com

## Finally run this command to execute the script 

```bash
streamlit run app.py
```

![Dashboard Screenshot](https://github.com/hari3485/sample_projects/blob/main/youtube_transcript/Dashboard_screenshot_2.png?raw=true "Click to view full image")


