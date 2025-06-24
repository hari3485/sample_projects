import os
import json
import streamlit as st
from tempfile import NamedTemporaryFile
from transcript_utils import extract_video_id, extract_english_transcript_json, upload_file_to_s3
from llm_query_engine import get_response

# Streamlit UI configuration
st.set_page_config(page_title="YouTube Video Q&A", layout="centered")
st.title("🎥 YouTube Video Q&A with Timestamp Linking")

# Input field for YouTube URL
url = st.text_input("📺 Enter YouTube video URL")

if url:
    video_id = extract_video_id(url)
    if not video_id:
        st.error("❌ Invalid YouTube URL!")
    else:
        st.success(f"✅ Video ID extracted: {video_id}")

        # Ingest transcript only once per session
        if f"{video_id}_ingested" not in st.session_state:
            st.info("📄 Extracting transcript...")
            transcript_data = extract_english_transcript_json(url, video_id)

            if transcript_data:
                # Save transcript to a temporary JSON file
                with NamedTemporaryFile(delete=False, suffix=".json", mode="w", encoding="utf-8") as f:
                    json.dump(transcript_data, f, indent=2, ensure_ascii=False)
                    temp_json_path = f.name

                # Upload to S3 and start ingestion into Bedrock KB
                st.info("🧠 Uploading transcript to S3 and ingesting into knowledge base...")
                s3_uri, job_id = upload_file_to_s3(temp_json_path, "transcript-s33", video_id)

                if job_id:
                    st.success("✅ Transcript successfully ingested into knowledge base!")
                    st.session_state[f"{video_id}_ingested"] = True
                else:
                    st.error("❌ Ingestion failed.")
            else:
                st.error("❌ Could not extract transcript.")

        # Question input field
        question = st.text_input("❓ Ask a question about the video")

        # On submit, generate an answer
        if st.button("🔍 Generate Answer"):
            if not question.strip():
                st.warning("Please enter a question.")
            else:
                with st.spinner("Generating answer..."):
                    try:
                        modified_question = f"Video ID : {video_id}\nQuestion: {question}"
                        metadata, answer = get_response(modified_question, video_id)
                        st.markdown(question)
                        st.markdown(answer, unsafe_allow_html=True)
                        st.json(metadata)
                    except Exception as e:
                        st.error(f"❌ Failed to generate answer: {e}")
