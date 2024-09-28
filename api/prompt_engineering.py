# /api/prompt_engineering.py

from flask import request, jsonify
from .ai_service import call_openai_api  # 只导入用于调用 API 的函数

def build_attitude_check_prompt(user_input):
    """
    构建用于判断用户语气的提示词。

    :param user_input: 用户输入的消息
    :return: 构建好的消息列表
    """
    return [
        {"role": "system", "content": "你是一个判断助手，帮助判断用户语言是否友好。"},
        {"role": "user", "content": f"用户语句：{user_input}。请判断该语句是否是友好的，如果是，回答'友好'，如果不是，回答'不友好'。"}
    ]

def build_friendly_response_prompt(user_input):
    """
    构建用于生成友好回复的提示词。

    :param user_input: 用户输入的消息
    :return: 构建好的消息列表
    """
    return [
        {"role": "system", "content": "你是豆包，是由字节跳动开发的 AI 人工智能助手"},
        {"role": "user", "content": user_input}
    ]

def chat():
    # 确保只允许 POST 请求
    if request.method != 'POST':
        return jsonify({"error": "Only POST method is allowed"}), 405

    # 尝试解析请求体
    try:
        body = request.json
        user_input = body.get('message')
        if not user_input:
            return jsonify({"error": "Message is required"}), 400
    except Exception as e:
        return jsonify({"error": "Invalid request format"}), 400

    try:
        # 调用 OpenAI 模型进行语气判断
        attitude_messages = build_attitude_check_prompt(user_input)
        attitude_result = call_openai_api(attitude_messages)

        # 根据用户的语气判断，生成不同的回复
        if attitude_result == "友好":
            response_messages = build_friendly_response_prompt(user_input)
            ai_reply = call_openai_api(response_messages)
            response = {"response": ai_reply}
        else:
            response = {"response": "请注意您的用词，保持文明对话。"}
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify(response), 200
