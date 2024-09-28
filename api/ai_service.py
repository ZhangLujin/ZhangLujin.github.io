import os
from openai import OpenAI

class AIService:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY", "b5afc8c2-957d-4de1-9881-fe464e2a2d0b")
        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://ark.cn-beijing.volces.com/api/v3"
        )

    def get_completion(self, messages, model="ep-20240924191053-2c9zd"):
        response = self.client.chat.completions.create(
            model=model,
            messages=messages
        )
        return response.choices[0].message.content
