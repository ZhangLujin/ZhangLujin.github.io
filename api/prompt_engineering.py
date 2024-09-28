# /api/prompt_engineering.py

from flask import request, jsonify
from .ai_service import call_openai_api

def build_response_prompt(user_input):
    """
    构建用于生成回复的提示词。

    :param user_input: 用户输入的消息
    :return: 构建好的消息列表
    """
    return [
        {"role": "system", "content": "你是豆包，是由字节跳动开发的 AI 人工智能助手"},
        {"role": "user", "content": user_input}
    ]

def chat():
    if request.method != 'POST':
        return jsonify({"error": "Only POST method is allowed"}), 405

    try:
        body = request.json
        user_input = body.get('message')
        if not user_input:
            return jsonify({"error": "Message is required"}), 400

        response_messages = build_response_prompt(user_input)
        ai_reply = call_openai_api(response_messages)
        response = {"response": ai_reply}
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify(response), 200

# 引导式面试相关函数

def guided_interview_flow(user_input, state):
    """
    引导式面试的主控制流程。

    :param user_input: 用户的输入
    :param state: 当前的状态，包括当前问题编号等信息
    :return: 下一步的响应和更新后的状态
    """
    current_question = state.get('current_question', 1)

    if current_question == 1:
        return handle_question_1(user_input, state)
    elif current_question == 2:
        return handle_question_2(user_input, state)
    elif current_question == 3:
        return handle_question_3(user_input, state)
    elif current_question == 4:
        return handle_question_4(user_input, state)
    elif current_question == 5:
        return handle_question_5(user_input, state)
    else:
        return {"response": "面试已结束，感谢您的参与。"}, state

def handle_question_1(user_input, state):
    """
    处理第一个问题的逻辑
    """
    # TODO: 实现问题1的具体逻辑
    pass

def handle_question_2(user_input, state):
    """
    处理第二个问题的逻辑
    """
    # TODO: 实现问题2的具体逻辑
    pass

def handle_question_3(user_input, state):
    """
    处理第三个问题的逻辑
    """
    # TODO: 实现问题3的具体逻辑
    pass

def handle_question_4(user_input, state):
    """
    处理第四个问题的逻辑
    """
    # TODO: 实现问题4的具体逻辑
    pass

def handle_question_5(user_input, state):
    """
    处理第五个问题的逻辑
    """
    # TODO: 实现问题5的具体逻辑
    pass

def evaluate_answer(question, answer):
    """
    评估用户对特定问题的回答

    :param question: 问题编号或标识符
    :param answer: 用户的回答
    :return: 评估结果和反馈
    """
    # TODO: 实现答案评估逻辑
    pass

def guided_interview():
    if request.method != 'POST':
        return jsonify({"error": "Only POST method is allowed"}), 405

    try:
        body = request.json
        user_input = body.get('message')
        state = body.get('state', {})  # 获取当前状态，如果没有则使用空字典

        if not user_input:
            return jsonify({"error": "Message is required"}), 400

        response, new_state = guided_interview_flow(user_input, state)
        return jsonify({"response": response, "state": new_state}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 注意：需要在路由中添加对 guided_interview 的调用