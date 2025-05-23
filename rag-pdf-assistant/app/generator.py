import os
from dotenv import load_dotenv
from flotorch_core.inferencer.gateway_inferencer import GatewayInferencer
from app.retriever import get_retrieved_context

# Load API keys from .env file
load_dotenv()

def generate_response(user_query, path):
    """
    Generates a grounded response to the user's question based on a document.

    Args:
        user_query (str): The user's question.
        path (str): The path to the input document.

    Returns:
        str: Generated response from the model.
    """
    # Retrieve relevant chunks from the document
    context_list = get_retrieved_context(path, user_query)

    # Merge chunks into a single formatted context string
    context_str = "\n".join(f"--- Context {i+1} ---\n{ctx}" for i, ctx in enumerate(context_list))
    context = [{'text': context_str}]

    # System prompt with strict grounding rules
    prompts = {
        "system_prompt": (
            "You are a helpful and knowledgeable assistant designed to answer questions strictly based on the context provided from a PDF document. "
            "Do not use any external knowledge or make assumptions beyond the given information. "
            "If the answer to a question is not clearly present in the provided context, respond with \"I don't know.\" "
            "However, if the user asks for a summary of the PDF, you are allowed to summarize the provided context accurately and concisely. "
            "Your responses must always remain grounded in the supplied context, whether you are answering questions or summarizing, "
            "without adding external facts or unsupported interpretation. "
            "Handle user input in a case-insensitive manner."
        )
    }

    # Instantiate Claude-based GatewayInferencer with your API and base URL
    inferencer = GatewayInferencer(
        model_id="anthro/claude-3-haiku-20240307",
        api_key=os.getenv("API_KEY"),
        base_url=os.getenv("BASE_URL"),
        n_shot_prompt_guide_obj=prompts
    )

    # Generate response from model
    _, answer = inferencer.generate_text(user_query, context)
    return answer
