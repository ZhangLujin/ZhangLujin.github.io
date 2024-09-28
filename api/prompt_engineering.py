# /api/prompt_engineering.py

from flask import request, jsonify
from .ai_service import call_openai_api

def build_system_prompt():
    return {"role": "system", "content": "你是一位经验丰富的小学作文教师，正在指导学生完成一篇'我的心爱之物'主题的作文。用友好、鼓励的语气主动引导学生完成写作过程的每一步。"}

def guided_essay_flow(user_input, state):
    """
    作文引导的主控制流程。

    :param user_input: 用户的输入（可能为空）
    :param state: 当前的状态，包括当前步骤等信息
    :return: 下一步的响应和更新后的状态
    """
    current_step = state.get('current_step', 0)

    steps = [
        start_guidance,
        determine_topic,
        create_mind_map,
        guide_introduction,
        guide_body,
        guide_conclusion,
        create_title,
        review_essay
    ]

    if current_step < len(steps):
        return steps[current_step](user_input, state)
    else:
        return {"response": "作文指导已结束，谢谢你的参与！"}, state

def start_guidance(user_input, state):
    prompt = [
        build_system_prompt(),
        {"role": "assistant", "content": "你好！我们今天要写一篇'我的心爱之物'的作文。让我们开始吧！首先，请告诉我，你最心爱的东西是什么？"}
    ]
    response = call_openai_api(prompt)
    new_state = state.copy()
    new_state['current_step'] = 1
    return {"response": response}, new_state

def determine_topic(user_input, state):
    prompt = [
        build_system_prompt(),
        {"role": "user", "content": user_input},
        {"role": "assistant", "content": "太好了！你能告诉我为什么这个东西是你的心爱之物吗？它对你有什么特别的意义？"}
    ]
    response = call_openai_api(prompt)
    new_state = state.copy()
    new_state['current_step'] = 2
    new_state['topic'] = user_input
    return {"response": response}, new_state

def create_mind_map(user_input, state):
    prompt = [
        build_system_prompt(),
        {"role": "user", "content": user_input},
        {"role": "assistant", "content": "你的想法很有趣！让我们来做一个思维导图，帮助你组织思路。请回答以下问题：\n1. 你的心爱之物长什么样子？\n2. 你是怎么得到它的？\n3. 它让你感觉如何？\n4. 有什么特别的回忆和它有关吗？\n请尽可能详细地回答这些问题。"}
    ]
    response = call_openai_api(prompt)
    new_state = state.copy()
    new_state['current_step'] = 3
    new_state['mind_map'] = user_input
    return {"response": response}, new_state

def guide_introduction(user_input, state):
    prompt = [
        build_system_prompt(),
        {"role": "user", "content": user_input},
        {"role": "assistant", "content": "你的想法很丰富！现在让我们开始写作文的开头。开头可以用以下方式之一：\n1. 直接介绍你的心爱之物\n2. 描述第一次看到它的场景\n3. 用一个有趣的问题引出主题\n选择一种方式，写出你的开头段落吧。"}
    ]
    response = call_openai_api(prompt)
    new_state = state.copy()
    new_state['current_step'] = 4
    new_state['introduction'] = user_input
    return {"response": response}, new_state

def guide_body(user_input, state):
    prompt = [
        build_system_prompt(),
        {"role": "user", "content": user_input},
        {"role": "assistant", "content": "好的开头！接下来我们来写作文的主体部分。请描述2-3个关于你心爱之物的事件或特点。每个部分可以包括：\n1. 具体的描述\n2. 相关的细节\n3. 你的感受或想法\n4. 这个事件或特点的影响\n请开始写作主体部分，写完一个部分就告诉我，我们一起来完善。"}
    ]
    response = call_openai_api(prompt)
    new_state = state.copy()
    new_state['current_step'] = 5
    new_state['body'] = user_input
    return {"response": response}, new_state

def guide_conclusion(user_input, state):
    prompt = [
        build_system_prompt(),
        {"role": "user", "content": user_input},
        {"role": "assistant", "content": "主体部分写得很精彩！现在让我们来写结尾。在结尾中，你可以：\n1. 总结这个心爱之物对你的意义\n2. 表达你对它的感情\n3. 说说它给你的生活带来了什么变化\n请写出你的结尾段落。"}
    ]
    response = call_openai_api(prompt)
    new_state = state.copy()
    new_state['current_step'] = 6
    new_state['conclusion'] = user_input
    return {"response": response}, new_state

def create_title(user_input, state):
    prompt = [
        build_system_prompt(),
        {"role": "user", "content": user_input},
        {"role": "assistant", "content": "太棒了，你的作文主体已经完成！现在让我们为你的作文起一个吸引人的标题。好的标题应该简明、具体、新颖。想一想，什么标题能最好地概括你的心爱之物和你对它的感情？请提供2-3个标题的想法。"}
    ]
    response = call_openai_api(prompt)
    new_state = state.copy()
    new_state['current_step'] = 7
    new_state['title_ideas'] = user_input
    return {"response": response}, new_state

def review_essay(user_input, state):
    full_essay = f"""
    题目：{user_input}
    
    开头：{state.get('introduction', '')}
    
    主体：{state.get('body', '')}
    
    结尾：{state.get('conclusion', '')}
    """
    prompt = [
        build_system_prompt(),
        {"role": "user", "content": f"这是我完成的作文：\n\n{full_essay}"},
        {"role": "assistant", "content": "恭喜你完成了作文！我来给你一些反馈。我会从以下几个方面评价你的作文：\n1. 内容的真实性和丰富程度\n2. 语言的准确性和生动性\n3. 结构的完整性和逻辑性\n4. 情感的真挚度\n5. 整体的创新性\n我会给出具体的评价和改进建议，以及一个总体的五星评分。"}
    ]
    response = call_openai_api(prompt)
    new_state = state.copy()
    new_state['current_step'] = 8
    new_state['final_essay'] = full_essay
    return {"response": response}, new_state

def guided_essay():
    if request.method != 'POST':
        return jsonify({"error": "Only POST method is allowed"}), 405

    try:
        body = request.json
        user_input = body.get('message', '')
        state = body.get('state', {'current_step': 0})

        response, new_state = guided_essay_flow(user_input, state)
        return jsonify({"response": response, "state": new_state}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 保留原有的 chat 函数，以保持兼容性
def chat():
    if request.method != 'POST':
        return jsonify({"error": "Only POST method is allowed"}), 405

    try:
        body = request.json
        user_input = body.get('message', '')
        state = body.get('state', {'current_step': 0})

        # 调用 guided_essay_flow 来处理请求
        response, new_state = guided_essay_flow(user_input, state)

        # 构造与原有 chat 函数兼容的响应格式
        chat_response = {
            "response": response.get("response", ""),
            "state": new_state
        }

        return jsonify(chat_response), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500