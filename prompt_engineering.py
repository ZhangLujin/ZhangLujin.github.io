class PromptEngineer:
    @staticmethod
    def get_attitude_check_prompt(user_input):
        return [
            {"role": "system", "content": "你是一个判断助手，帮助判断用户语言是否友好。"},
            {"role": "user", "content": f"用户语句：{user_input}。 请判断该语句是否是友好的，如果是，回答'友好'，如果不是，回答'不友好'。"}
        ]

    @staticmethod
    def get_chatbot_prompt(user_input):
        return [
            {"role": "system", "content": "你是豆包，是由字节跳动开发的 AI 人工智能助手"},
            {"role": "user", "content": user_input}
        ]

    @staticmethod
    def process_attitude_response(attitude_response):
        return attitude_response.strip().lower() == "友好"

    @staticmethod
    def get_unfriendly_response():
        return "请注意您的用词，保持文明对话。"

    @staticmethod
    def chat_flow(ai_service, user_input):
        # 态度检查
        attitude_prompt = PromptEngineer.get_attitude_check_prompt(user_input)
        attitude_response = ai_service.get_completion(attitude_prompt)
        is_friendly = PromptEngineer.process_attitude_response(attitude_response)

        if is_friendly:
            # 生成友好回复
            chat_prompt = PromptEngineer.get_chatbot_prompt(user_input)
            response = ai_service.get_completion(chat_prompt)
        else:
            # 返回不友好提醒
            response = PromptEngineer.get_unfriendly_response()

        return response
