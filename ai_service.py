from openai import OpenAI

class AIService:
    def __init__(self, api_key, base_url):
        self.client = OpenAI(api_key=api_key, base_url=base_url)

    def get_completion(self, messages):
        response = self.client.chat.completions.create(
            model="ep-20240924191053-2c9zd",
            messages=messages
        )
        return response.choices[0].message.content