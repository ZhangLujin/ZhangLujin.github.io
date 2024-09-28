# /api/prompt_engineering.py

from flask import request, jsonify
from .ai_service import call_openai_api

def build_system_prompt():
    return {"role": "system", "content": "你是一位经验丰富的小学作文教师，正在指导学生完成一篇'我的心爱之物'主题的作文。用友好、鼓励的语气与学生交流，引导他们完成写作过程。"}

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

def guided_interview_flow(user_input, state):
    """
    作文引导的主控制流程。

    :param user_input: 用户的输入
    :param state: 当前的状态，包括当前步骤等信息
    :return: 下一步的响应和更新后的状态
    """
    current_step = state.get('current_step', 1)

    if current_step == 1:
        return handle_question_1(user_input, state)
    elif current_step == 2:
        return handle_question_2(user_input, state)
    elif current_step == 3:
        return handle_question_3(user_input, state)
    elif current_step == 4:
        return handle_question_4(user_input, state)
    elif current_step == 5:
        return handle_question_5(user_input, state)
    else:
        return {"response": "作文指导已结束，谢谢你的参与！"}, state

def handle_question_1(user_input, state):
    """确定写作主体"""
    prompt = [
        build_system_prompt(),
        {"role": "user", "content": "我要写'我的心爱之物'的作文。"},
        {"role": "assistant", "content": "太好了！让我们开始写作吧。首先，请告诉我你的心爱之物是什么？如果你还不确定，可以说出几个你很喜欢的东西。"}
    ]
    if user_input:
        prompt.append({"role": "user", "content": user_input})
        prompt.append({"role": "assistant", "content": "非常好！你能再具体说说为什么这个东西是你的心爱之物吗？"})

    response = call_openai_api(prompt)
    new_state = state.copy()
    new_state['current_step'] = 2
    new_state['topic'] = user_input
    return {"response": response}, new_state

def handle_question_2(user_input, state):
    """思维导图，激发灵感"""
    prompt = [
        build_system_prompt(),
        {"role": "user", "content": f"我的心爱之物是{state.get('topic')}。{user_input}"},
        {"role": "assistant", "content": "太棒了！让我们继续深入思考。请回答以下问题来丰富你的思路：\n1. 你的心爱之物是什么样子的？\n2. 你是怎么得到它的？\n3. 它为什么成为你的心爱之物？\n想到的越多越好，我会帮你整理这些想法。"}
    ]
    response = call_openai_api(prompt)
    new_state = state.copy()
    new_state['current_step'] = 3
    new_state['mind_map'] = user_input
    return {"response": response}, new_state

def handle_question_3(user_input, state):
    """结构引导：开头"""
    prompt = [
        build_system_prompt(),
        {"role": "user", "content": f"关于我的心爱之物{state.get('topic')}，我的想法是：{user_input}"},
        {"role": "assistant", "content": "你的想法很丰富！现在让我们来写作文的开头。你可以选择以下方式之一：\n1. 直接点出主题\n2. 用生动的描述引出主题\n3. 讲述一个小故事来引入主题\n请选择一种方式，然后写出你的开头段落。"}
    ]
    response = call_openai_api(prompt)
    new_state = state.copy()
    new_state['current_step'] = 4
    new_state['introduction'] = user_input
    return {"response": response}, new_state

def handle_question_4(user_input, state):
    """结构引导：主体"""
    prompt = [
        build_system_prompt(),
        {"role": "user", "content": f"我的作文开头是：{user_input}"},
        {"role": "assistant", "content": "精彩的开头！现在让我们来写作文的主体部分。请你描述2-3个关于你心爱之物的事件或特点。每个事件或特点可以包括：\n1. 具体的描述\n2. 相关的细节\n3. 你的感受或想法\n4. 这个事件或特点的影响\n请开始写作主体部分。"}
    ]
    response = call_openai_api(prompt)
    new_state = state.copy()
    new_state['current_step'] = 5
    new_state['body'] = user_input
    return {"response": response}, new_state

def handle_question_5(user_input, state):
    """结构引导：结尾和标题"""
    prompt = [
        build_system_prompt(),
        {"role": "user", "content": f"我的作文主体是：{user_input}"},
        {"role": "assistant", "content": "你的主体写得很精彩！现在让我们来完成最后的部分。\n1. 请写一个总结性的结尾，可以表达你对这个心爱之物的感情，或者说说它对你的意义。\n2. 然后，请为你的作文起一个吸引人的标题。记住，好的标题应该简明、具体、新颖。\n请写出你的结尾和标题。"}
    ]
    response = call_openai_api(prompt)
    new_state = state.copy()
    new_state['current_step'] = 6
    new_state['conclusion'] = user_input
    return {"response": response}, new_state

def evaluate_answer(question, answer):
    """
    评估用户的作文内容
    """
    full_essay = f"""
    题目：{answer.get('title', '未命名')}
    
    开头：{answer.get('introduction', '')}
    
    主体：{answer.get('body', '')}
    
    结尾：{answer.get('conclusion', '')}
    """

    prompt = [
        build_system_prompt(),
        {"role": "user", "content": f"请评价以下作文：\n\n{full_essay}"},
        {"role": "assistant", "content": "我会根据以下标准评价这篇作文：\n1. 内容真实性\n2. 用词准确性\n3. 修辞手法使用\n4. 整体结构\n5. 情感表达\n然后给出五星评分和改进建议。"}
    ]
    response = call_openai_api(prompt)
    return response

def guided_interview():
    if request.method != 'POST':
        return jsonify({"error": "Only POST method is allowed"}), 405

    try:
        body = request.json
        user_input = body.get('message')
        state = body.get('state', {})

        if not user_input and state.get('current_step', 1) != 1:
            return jsonify({"error": "Message is required"}), 400

        response, new_state = guided_interview_flow(user_input, state)

        if new_state['current_step'] > 5:
            evaluation = evaluate_answer(None, new_state)
            response["evaluation"] = evaluation

        return jsonify({"response": response, "state": new_state}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500