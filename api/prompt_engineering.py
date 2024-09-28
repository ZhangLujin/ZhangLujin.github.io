# /api/prompt_engineering.py

from flask import request, jsonify
from .ai_service import call_openai_api

def build_system_prompt():
    return {"role": "system", "content": "你是一位经验丰富的小学作文教师，正在指导学生完成一篇作文。你要用友好、鼓励的语气与学生交流，引导他们完成写作过程。"}

def guided_essay_flow(user_input, state):
    """
    作文引导的主控制流程。

    :param user_input: 用户的输入
    :param state: 当前的状态，包括当前步骤等信息
    :return: 下一步的响应和更新后的状态
    """
    current_step = state.get('current_step', 'start')

    if current_step == 'start':
        return start_essay_guidance(user_input, state)
    elif current_step == 'determine_topic':
        return determine_topic(user_input, state)
    elif current_step == 'mind_mapping':
        return create_mind_map(user_input, state)
    elif current_step == 'structure_guidance':
        return provide_structure_guidance(user_input, state)
    elif current_step == 'write_content':
        return guide_content_writing(user_input, state)
    elif current_step == 'title_creation':
        return guide_title_creation(user_input, state)
    elif current_step == 'essay_review':
        return review_essay(user_input, state)
    else:
        return {"response": "作文指导已结束，谢谢你的参与！"}, state

def start_essay_guidance(user_input, state):
    prompt = [
        build_system_prompt(),
        {"role": "user", "content": "我需要写一篇作文，主题是'我的心爱之物'。"}
    ]
    response = call_openai_api(prompt)
    new_state = {'current_step': 'determine_topic', 'essay_topic': '我的心爱之物'}
    return {"response": response}, new_state

def determine_topic(user_input, state):
    prompt = [
        build_system_prompt(),
        {"role": "user", "content": f"学生回答：{user_input}"},
        {"role": "assistant", "content": "好的，让我们来确定你的心爱之物。你能直接告诉我是什么吗？如果不确定，我可以给你一些提示。"}
    ]
    response = call_openai_api(prompt)
    new_state = state.copy()
    new_state['current_step'] = 'mind_mapping'
    return {"response": response}, new_state

def create_mind_map(user_input, state):
    prompt = [
        build_system_prompt(),
        {"role": "user", "content": f"学生的心爱之物是：{user_input}"},
        {"role": "assistant", "content": "太棒了！让我们来创建一个思维导图。请告诉我：\n1. 你的心爱之物是什么样子的？\n2. 你是怎么得到它的？\n3. 为什么它成为你的心爱之物？"}
    ]
    response = call_openai_api(prompt)
    new_state = state.copy()
    new_state['current_step'] = 'structure_guidance'
    new_state['mind_map'] = user_input
    return {"response": response}, new_state

def provide_structure_guidance(user_input, state):
    prompt = [
        build_system_prompt(),
        {"role": "user", "content": f"学生的思维导图内容：{user_input}"},
        {"role": "assistant", "content": "很好！现在让我们来规划你的作文结构。我们会分为开头、中间和结尾三个部分。首先，你想怎么开始你的作文呢？"}
    ]
    response = call_openai_api(prompt)
    new_state = state.copy()
    new_state['current_step'] = 'write_content'
    new_state['structure'] = {'introduction': '', 'body': '', 'conclusion': ''}
    return {"response": response}, new_state

def guide_content_writing(user_input, state):
    current_part = state.get('current_writing_part', 'introduction')
    structure = state.get('structure', {})

    if current_part == 'introduction':
        prompt = [
            build_system_prompt(),
            {"role": "user", "content": f"学生的开头：{user_input}"},
            {"role": "assistant", "content": "很好的开头！现在让我们来写作文的主体部分。你可以描述几个关于你心爱之物的事件吗？"}
        ]
        structure['introduction'] = user_input
        new_part = 'body'
    elif current_part == 'body':
        prompt = [
            build_system_prompt(),
            {"role": "user", "content": f"学生的主体内容：{user_input}"},
            {"role": "assistant", "content": "精彩的主体部分！最后，让我们来写一个好的结尾。你可以总结一下你的心爱之物对你的意义，或者表达你的感受。"}
        ]
        structure['body'] = user_input
        new_part = 'conclusion'
    else:  # conclusion
        prompt = [
            build_system_prompt(),
            {"role": "user", "content": f"学生的结尾：{user_input}"},
            {"role": "assistant", "content": "太棒了，你已经完成了整篇作文的写作！现在让我们来为你的作文起一个好标题吧。"}
        ]
        structure['conclusion'] = user_input
        new_part = None

    response = call_openai_api(prompt)
    new_state = state.copy()
    new_state['structure'] = structure
    if new_part:
        new_state['current_writing_part'] = new_part
    else:
        new_state['current_step'] = 'title_creation'
    return {"response": response}, new_state

def guide_title_creation(user_input, state):
    prompt = [
        build_system_prompt(),
        {"role": "user", "content": f"学生的作文内容：{state.get('structure')}"},
        {"role": "assistant", "content": "根据你的作文内容，请为你的作文起一个好标题。记住，好的标题应该简明、具体、准确、新颖且生动。"}
    ]
    response = call_openai_api(prompt)
    new_state = state.copy()
    new_state['current_step'] = 'essay_review'
    new_state['title'] = user_input
    return {"response": response}, new_state

def review_essay(user_input, state):
    essay_content = f"标题：{state.get('title')}\n\n"
    essay_content += f"开头：{state['structure']['introduction']}\n\n"
    essay_content += f"主体：{state['structure']['body']}\n\n"
    essay_content += f"结尾：{state['structure']['conclusion']}"

    prompt = [
        build_system_prompt(),
        {"role": "user", "content": f"请评价以下作文：\n\n{essay_content}"},
        {"role": "assistant", "content": "我会根据以下标准评价这篇作文：1.内容真实性 2.用词准确性 3.修辞手法使用 4.整体结构 5.情感表达。然后给出五星评分和改进建议。"}
    ]
    response = call_openai_api(prompt)
    new_state = state.copy()
    new_state['current_step'] = 'finished'
    return {"response": response}, new_state

def guided_essay():
    if request.method != 'POST':
        return jsonify({"error": "Only POST method is allowed"}), 405

    try:
        body = request.json
        user_input = body.get('message')
        state = body.get('state', {})

        if not user_input and state.get('current_step') != 'start':
            return jsonify({"error": "Message is required"}), 400

        response, new_state = guided_essay_flow(user_input, state)
        return jsonify({"response": response, "state": new_state}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 注意：需要在路由中添加对 guided_essay 的调用