import base64
import os
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

class GatewayEngine:
    DEFAULT_SYSTEM_PROMPT = "You are a helpful, creative, and smart assistant."

    def __init__(self, model_string="gpt-4o", base_url=None, system_prompt=None):
        self.model_string = model_string
        self.system_prompt = system_prompt or self.DEFAULT_SYSTEM_PROMPT

        self.client = OpenAI(
            api_key=os.getenv("API_KEY"),
            base_url=os.getenv("BASE_URL") or base_url
        )

    def __call__(self, input_data):
        try:
            # Multimodal: [text_prompt, image_bytes]
            if isinstance(input_data, list) and len(input_data) == 2:
                prompt, image_bytes = input_data
                # Validate input types
                if not isinstance(prompt, str) or not isinstance(image_bytes, bytes):
                    return "Error: Multimodal input must be [str, bytes]."

                base64_image = base64.b64encode(image_bytes).decode('utf-8')

                messages = [
                    {
                        "role": "system",
                        "content": self.system_prompt # Use the user-provided prompt as system content if needed
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{base64_image}"
                                }
                            },
                            {
                                "type": "text",
                                "text": prompt
                            }
                        ]
                    }
                ]

                print("Prompt: ",prompt)
                print("Model Name: ",self.model_string)
                response = self.client.chat.completions.create(
                    model=self.model_string,
                    messages=messages,
                    temperature=0.7,
                )
                metadata=self._extract_metadata(response)
                return metadata,response.choices[0].message.content.strip()

            else:
                return "Error: Invalid input format. Use a string or [text, image_bytes]."

        except Exception as e:
            return f"Error generating response: {str(e)}"
    
    def _extract_metadata(self, response):
        return {
            "inputTokens": str(response.usage.prompt_tokens),
            "outputTokens": str(response.usage.completion_tokens),
            "totalTokens": str(response.usage.total_tokens),
            "latencyMs": "0"
        }
