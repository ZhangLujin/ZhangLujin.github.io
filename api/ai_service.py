import os
from openai import OpenAI

class AIService:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY", "b5afc8c2-957d-4de1-9881-fe464e2a2d0b")
        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://ark.cn-beijing.volces.com/api/v3"
        )

    def create_chat_completion(self, model, messages):
        return self.client.chat.completions.create(
            model=model,
            messages=messages
        )