import os
import re
from dotenv import load_dotenv
from flotorch_core.storage.db.vector.vector_storage_factory import VectorStorageFactory
from flotorch_core.chunking.chunking import Chunk
from flotorch_core.inferencer.gateway_inferencer import GatewayInferencer
from openai import OpenAI

load_dotenv()
client = OpenAI()

# Query the KB and generate answer with timestamp
def get_response(query, video_id):
    # Search the knowledge base
    vector_store = VectorStorageFactory.create_vector_storage(
        knowledge_base=True,
        use_bedrock_kb=True,
        knowledge_base_id=os.getenv("AWS_KNOWNLEDGE_BASE_ID"),
        embedding=None,
        aws_region="us-east-1"
    )

    query_chunk = Chunk(data=query)
    search_results = vector_store.search(query_chunk, 5)
    docs = search_results.to_json().get("result")

    formatted_transcript = "\n".join(data.get("text", "") for data in docs if "text" in data)

    # Extract first relevant timestamp
    def find_first_matching_timestamp(response, transcript_text):
        for line in transcript_text.split('\n'):
            match = re.match(r'\[(\d{2}):(\d{2})\]', line)
            if match:
                _, content = line.split(']', 1)
                if any(phrase.lower() in content.lower() for phrase in response.lower().split()):
                    minutes = int(match.group(1))
                    seconds = int(match.group(2))
                    total_seconds = minutes * 60 + seconds
                    return f"[{minutes:02d}:{seconds:02d}](https://www.youtube.com/watch?v={video_id}&t={total_seconds}s)"
        return None

    # Prompt configuration
    prompts = {
        "system_prompt": (
            "You are an intelligent assistant that answers questions strictly based on the provided YouTube video transcript.\n\n"
            "- Use only the information from the transcript.\n"
            "- If the answer is not found, say: \"I don't know\".\n"
            "- Format timestamp: [mm:ss ▶️](https://www.youtube.com/watch?v=<VIDEO_ID>&t=SECONDSs)\n"
            "- Replace <VIDEO_ID> and convert mm:ss → seconds."
        ),
        "examples": [
            {
                "question": "Video ID: abcd1234\nQuestion: What is a mixed model ANOVA?",
                "answer": "Answer: A mixed model ANOVA is ...\nTimestamp: [00:17](https://www.youtube.com/watch?v=abcd1234&t=17s)"
            },
            {
                "question": "Video ID: xyz9876\nQuestion: Who is the author?",
                "answer": "I don't know"
            }
        ]
    }

    inferencer = GatewayInferencer(
        model_id="openai/gpt-4.1",
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv("BASE_URL"),
        n_shot_prompt_guide_obj=prompts,
        n_shot_prompts=2
    )

    metadata, answer = inferencer.generate_text(query, [{"text": formatted_transcript}])
    timestamp_link = find_first_matching_timestamp(answer, formatted_transcript)
    if timestamp_link:
        answer += f"\n\nTimestamp: {timestamp_link}"
    return metadata, answer
