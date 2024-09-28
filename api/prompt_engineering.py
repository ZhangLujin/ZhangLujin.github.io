class PromptEngineer:
    @staticmethod
    def get_attitude_check_prompt(user_input):
        return [
            {"role": "system", "content": "你是一个判断助手，帮助判断用户语言是否友好。"},
            {"role": "user", "content": f"用户语句：{user_input}。请判断该语句是否是友好的，如果是，回答'友好'，如果不是，回答'不友好'。"}
        ]

    @staticmethod
    def get_chatbot_prompt(user_input):
        return [
            {"role": "system", "content": "你是豆包，是由字节跳动开发的 AI 人工智能助手"},
            {"role": "user", "content": user_input}
        ]

    @staticmethod
    def process_chat(ai_service, user_input):
        try:
            # 调用 OpenAI 模型进行判断语气
            attitude_check = ai_service.create_chat_completion(
                model="ep-20240924191053-2c9zd",
                messages=PromptEngineer.get_attitude_check_prompt(user_input)
            )
            attitude_result = attitude_check.choices[0].message.content.strip()

            # 根据用户的语气判断，生成不同的回复
            if attitude_result == "友好":
                completion = ai_service.create_chat_completion(
                    model="ep-20240924191053-2c9zd",
                    messages=PromptEngineer.get_chatbot_prompt(user_input)
                )
                response = {"response": completion.choices[0].message.content}
            else:
                response = {"response": "请注意您的用词，保持文明对话。"}

            return response
        except Exception as e:
            return {"error": str(e)}