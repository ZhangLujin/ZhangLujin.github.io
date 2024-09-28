# /api/prompt_engineering.py

from flask import request, jsonify
from .ai_service import call_openai_api

def build_system_prompt(mode="writing"):
    if mode == "writing":
        return {"role": "system", "content": "你是一位经验丰富的小学作文教师，正在指导学生完成一篇'我的心爱之物'主题的作文。用友好、鼓励的语气主动引导学生完成写作过程。仔细评估学生的回答，只有在回答满足要求时才继续下一步。"}
    elif mode == "qa":
        return {"role": "system", "content": "你是一位友善的答疑老师，刚刚指导学生完成了一篇'我的心爱之物'主题的作文。现在你要回答学生关于这篇作文的任何问题，帮助他们更好地理解写作技巧和改进方法。"}

def guided_essay_flow(user_input, state):
    current_step = state.get('current_step', 0)

    steps = [
        start_guidance,
        determine_topic,
        create_mind_map,
        guide_introduction,
        guide_body,
        guide_conclusion,
        create_title,
        review_essay,
        start_qa_mode
    ]

    if current_step < len(steps):
        response, new_state = steps[current_step](user_input, state)
        # 确保 response 是字符串
        if isinstance(response, dict) and 'response' in response:
            response = response['response']
        return response, new_state
    else:
        return qa_mode(user_input, state)

def start_guidance(user_input, state):
    if not user_input:
        return "你好！我们今天要写一篇'我的心爱之物'的作文。让我们开始吧！首先，请告诉我，你最心爱的东西是什么？", state

    prompt = [
        build_system_prompt(),
        {"role": "assistant", "content": "你好！我们今天要写一篇'我的心爱之物'的作文。让我们开始吧！首先，请告诉我，你最心爱的东西是什么？"},
        {"role": "user", "content": user_input},
        {"role": "assistant", "content": "你是一位经验丰富的小学作文教师，正在指导学生完成一篇'我的心爱之物'主题的作文。用友好、鼓励的语气主动引导学生完成写作过程,注意对学生的要求不要太高，稍微满意即可。请评估学生的回答是否充分说明了他们最心爱的东西。如果回答满意，请继续下一步；如果不满意，请给出建议并要求学生重新回答。"}
    ]
    response = call_openai_api(prompt)
    new_state = state.copy()
    if "继续下一步" in response:
        new_state['current_step'] = 1
        new_state['topic'] = user_input
    return response, new_state

def determine_topic(user_input, state):
    prompt = [
        build_system_prompt(),
        {"role": "user", "content": f"我最心爱的东西是{state.get('topic', '未指定')}。{user_input}"},
        {"role": "assistant", "content": "你是一位经验丰富的小学作文教师，正在指导学生完成一篇'我的心爱之物'主题的作文。用友好、鼓励的语气主动引导学生完成写作过程,注意对学生的要求不要太高，稍微满意即可。请评估学生的回答。如果回答不够详细或不够具体，继续引导学生提供更多信息。如果回答已经足够详细，请继续下一步。无论如何，都要给出回应。"}
    ]
    response = call_openai_api(prompt)
    new_state = state.copy()
    if "继续下一步" in response:
        new_state['current_step'] = 2
        new_state['topic_reason'] = user_input
    else:
        new_state['current_step'] = 1  # 保持在当前步骤
    return response, new_state

def create_mind_map(user_input, state):
    prompt = [
        build_system_prompt(),
        {"role": "user", "content": user_input},
        {"role": "assistant", "content": "你是一位经验丰富的小学作文教师，正在指导学生完成一篇'我的心爱之物'主题的作文。用友好、鼓励的语气主动引导学生完成写作过程,注意对学生的要求不要太高，稍微满意即可。请根据学生的回答创建一个思维导图。如果信息不足，请继续引导学生提供更多细节。如果信息充足，总结主要点并继续下一步。"}
    ]
    response = call_openai_api(prompt)
    new_state = state.copy()
    if "继续下一步" in response:
        new_state['current_step'] = 3
        new_state['mind_map'] = user_input
    return response, new_state

def guide_introduction(user_input, state):
    prompt = [
        build_system_prompt(),
        {"role": "user", "content": user_input},
        {"role": "assistant", "content": "你是一位经验丰富的小学作文教师，正在指导学生完成一篇'我的心爱之物'主题的作文。用友好、鼓励的语气主动引导学生完成写作过程,注意对学生的要求不要太高，稍微满意即可。请评估学生的开头段落。如果开头吸引人且与主题相关，继续下一步。否则，提供具体建议并要求学生修改。"}
    ]
    response = call_openai_api(prompt)
    new_state = state.copy()
    if "继续下一步" in response:
        new_state['current_step'] = 4
        new_state['introduction'] = user_input
    return response, new_state

def guide_body(user_input, state):
    prompt = [
        build_system_prompt(),
        {"role": "user", "content": user_input},
        {"role": "assistant", "content": "你是一位经验丰富的小学作文教师，正在指导学生完成一篇'我的心爱之物'主题的作文。用友好、鼓励的语气主动引导学生完成写作过程,注意对学生的要求不要太高，稍微满意即可。请评估学生的主体段落。确保内容丰富、结构清晰、细节充实。如果满意，继续下一步；否则，提供改进建议。"}
    ]
    response = call_openai_api(prompt)
    new_state = state.copy()
    if "继续下一步" in response:
        new_state['current_step'] = 5
        new_state['body'] = user_input
    return response, new_state

def guide_conclusion(user_input, state):
    prompt = [
        build_system_prompt(),
        {"role": "user", "content": user_input},
        {"role": "assistant", "content": "你是一位经验丰富的小学作文教师，正在指导学生完成一篇'我的心爱之物'主题的作文。用友好、鼓励的语气主动引导学生完成写作过程,注意对学生的要求不要太高，稍微满意即可。请评估学生的结尾段落。确保结尾总结了主要观点并给出了深刻的感悟。如果满意，继续下一步；否则，提供修改建议。"}
    ]
    response = call_openai_api(prompt)
    new_state = state.copy()
    if "继续下一步" in response:
        new_state['current_step'] = 6
        new_state['conclusion'] = user_input
    return response, new_state

def create_title(user_input, state):
    prompt = [
        build_system_prompt(),
        {"role": "user", "content": user_input},
        {"role": "assistant", "content": "你是一位经验丰富的小学作文教师，正在指导学生完成一篇'我的心爱之物'主题的作文。用友好、鼓励的语气主动引导学生完成写作过程,注意对学生的要求不要太高，稍微满意即可。请评估学生提供的标题。确保标题简洁、吸引人且反映文章主题。如果满意，继续下一步；否则，提供改进建议。"}
    ]
    response = call_openai_api(prompt)
    new_state = state.copy()
    if "继续下一步" in response:
        new_state['current_step'] = 7
        new_state['title'] = user_input
    return response, new_state

def review_essay(user_input, state):
    full_essay = f"""
    题目：{state.get('title', '未命名')}
    
    开头：{state.get('introduction', '')}
    
    主体：{state.get('body', '')}
    
    结尾：{state.get('conclusion', '')}
    """
    prompt = [
        build_system_prompt(),
        {"role": "user", "content": f"这是我完成的作文：\n\n{full_essay}"},
        {"role": "assistant", "content": "你是一位经验丰富的小学作文教师，正在指导学生完成一篇'我的心爱之物'主题的作文。用友好、鼓励的语气主动引导学生完成写作过程,注意对学生的要求不要太高，稍微满意即可。请全面评估这篇作文，给出具体的评价和改进建议。评估后，引导学生进入答疑环节。"}
    ]
    response = call_openai_api(prompt)
    new_state = state.copy()
    new_state['current_step'] = 8
    new_state['final_essay'] = full_essay
    return response, new_state

def start_qa_mode(user_input, state):
    prompt = [
        build_system_prompt(mode="qa"),
        {"role": "assistant", "content": "太好了！你已经完成了作文，并且通过了评估。现在，如果你有任何关于这篇作文的问题，或者想了解更多关于写作技巧的内容，都可以问我。我会很乐意为你解答！"}
    ]
    response = call_openai_api(prompt)
    new_state = state.copy()
    new_state['current_step'] = 9
    new_state['mode'] = "qa"
    return response, new_state

def qa_mode(user_input, state):
    prompt = [
        build_system_prompt(mode="qa"),
        {"role": "user", "content": user_input},
        {"role": "assistant", "content": "我会根据你的问题，结合你刚刚完成的作文，给出详细的解答和建议。"}
    ]
    response = call_openai_api(prompt)
    return response, state

def chat():
    if request.method != 'POST':
        return jsonify({"error": "Only POST method is allowed"}), 405

    try:
        body = request.json
        user_input = body.get('message', '')
        state = body.get('state', {'current_step': 0})

        response, new_state = guided_essay_flow(user_input, state)
        return jsonify({"response": response, "state": new_state}), 200

    except Exception as e:
        print(f"Error in chat function: {str(e)}")  # 添加服务器端日志
        return jsonify({"error": str(e), "response": "抱歉，出现了一个错误。请重试或联系支持。"}), 500