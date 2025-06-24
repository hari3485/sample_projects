import time
import json
import os
import boto3
from botocore.exceptions import ClientError
from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs
from dotenv import load_dotenv
load_dotenv()

# Extract video ID from YouTube URL
def extract_video_id(youtube_url):
    parsed_url = urlparse(youtube_url)
    if parsed_url.hostname in ["www.youtube.com", "youtube.com"]:
        return parse_qs(parsed_url.query).get("v", [None])[0]
    elif parsed_url.hostname == "youtu.be":
        return parsed_url.path.lstrip("/")
    return None

# Extract and format English transcript as JSON
def extract_english_transcript_json(youtube_url, video_id):
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        formatted_transcript = ""
        transcript_segments = []

        for entry in transcript_list:
            start_time = int(entry['start'])
            minutes, seconds = divmod(start_time, 60)
            timestamp = f"[{minutes:02d}:{seconds:02d}]"
            formatted_transcript += f"{timestamp} {entry['text']}\n"

            transcript_segments.append({
                "timestamp": f"{minutes:02d}:{seconds:02d}",
                "start_seconds": start_time,
                "text": entry['text']
            })

        return {
            "video_id": video_id,
            "formatted_transcript": formatted_transcript,
            "transcript_segments": transcript_segments
        }

    except Exception as e:
        print("❌ Error extracting transcript:", e)
        return []

# Upload file to S3 and ingest to Bedrock knowledge base
def upload_file_to_s3(file_path, bucket_name, video_id, object_name=None, region="us-east-1"):
    s3 = boto3.client("s3", region_name=region)
    bedrock_agent_client = boto3.client("bedrock-agent", region_name=region)

    # Ensure bucket exists
    try:
        s3.head_bucket(Bucket=bucket_name)
        print(f"✅ Bucket '{bucket_name}' already exists.")
    except ClientError as e:
        error_code = int(e.response["Error"]["Code"])
        if error_code == 404:
            print(f"🪣 Bucket '{bucket_name}' not found. Creating...")
            try:
                config = {} if region == "us-east-1" else {"LocationConstraint": region}
                s3.create_bucket(Bucket=bucket_name, CreateBucketConfiguration=config)
                print(f"✅ Bucket '{bucket_name}' created successfully.")
            except ClientError as create_err:
                print("❌ Failed to create bucket:", create_err)
                return
        else:
            print("❌ Error checking bucket:", e)
            return

    # Upload the file
    try:
        object_key = f"youtube-transcript/{video_id}.json"
        s3_uri = f"s3://{bucket_name}/{object_key}"
        s3.put_object(Bucket=bucket_name, Key=object_key, Body=open(file_path, "rb"), ContentType="application/json")
        print(f"✅ File uploaded to '{s3_uri}' successfully.")

        # Start ingestion job
        response = bedrock_agent_client.start_ingestion_job(
            knowledgeBaseId=os.getenv("AWS_KNOWNLEDGE_BASE_ID"),
            dataSourceId=os.getenv("DATA_SOURCE_ID")
        )
        ingestion_job_id = response['ingestionJob']['ingestionJobId']
        print(f"Ingestion job started with ID: {ingestion_job_id}")

        # Monitor job status
        while True:
            job_status_response = bedrock_agent_client.get_ingestion_job(
                knowledgeBaseId=os.getenv("AWS_KNOWNLEDGE_BASE_ID"),
                dataSourceId=os.getenv("DATA_SOURCE_ID"),
                ingestionJobId=ingestion_job_id
            )
            status = job_status_response['ingestionJob']['status']
            print(f"Ingestion job status: {status}")
            if status in ['COMPLETE', 'FAILED', 'ABANDONED']:
                break
            time.sleep(10)

        if status == 'COMPLETE':
            print("✅ Ingestion completed successfully.")
            return s3_uri, ingestion_job_id
        else:
            print("❌ Ingestion failed or abandoned.")
            return s3_uri, None

    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return None, None
