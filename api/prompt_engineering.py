# /api/prompt_engineering.py

from flask import request, jsonify
from .ai_service import call_openai_api

# 定义写作步骤
STEPS = {
    1: "确定主题",
    2: "思维导图",
    3: "结构引导",
    4: "起题目和修改"
}

def build_prompt(system_content, user_content):
    """构建prompt"""
    return [
        {"role": "system", "content": system_content},
        {"role": "user", "content": user_content}
    ]

def guided_interview_flow(user_input, state):
    """引导式写作的主控制流程"""
    current_step = state.get('current_step', 1)
    current_substep = state.get('current_substep', 1)

    if current_step == 1:
        return handle_step_1(user_input, state)
    elif current_step == 2:
        return handle_step_2(user_input, state)
    elif current_step == 3:
        return handle_step_3(user_input, state)
    elif current_step == 4:
        return handle_step_4(user_input, state)
    else:
        return {"response": "写作指导已结束，感谢您的参与。"}, state

def handle_step_1(user_input, state):
    """处理第一步：确定主题"""
    substep = state.get('current_substep', 1)
    if substep == 1:
        prompt = build_prompt(
            "你是一个写作辅导老师，正在帮助学生确定'我的心爱之物'这个主题的写作对象。",
            f"学生的回答是：{user_input}。请根据学生的回答，判断是否需要进一步引导。如果需要，请给出适当的提示。"
        )
        response = call_openai_api(prompt)
        new_state = {**state, 'current_substep': 2}
        return {"response": response, "next_question": "请说出你的心爱之物"}, new_state
    elif substep == 2:
        # 处理学生的选择和进一步引导
        pass
    # 其他子步骤...

def handle_step_2(user_input, state):
    """处理第二步：思维导图，激发灵感"""
    prompt = build_prompt(
        "你是一个写作辅导老师，正在帮助学生进行'我的心爱之物'主题的头脑风暴。",
        f"学生的心爱之物是：{state.get('chosen_object', '未知')}。请根据以下问题引导学生思考：\n1. 你的心爱之物是什么样子？\n2. 你是怎么得到它的？\n3. 它为什么成为你的心爱之物？\n\n学生的回答是：{user_input}\n请对学生的回答进行分类和总结。"
    )
    response = call_openai_api(prompt)
    new_state = {**state, 'current_step': 3, 'current_substep': 1}
    return {"response": response, "next_question": "让我们开始写作的结构引导。首先，请尝试写一个开头。"}, new_state

def handle_step_3(user_input, state):
    """处理第三步：结构引导"""
    substep = state.get('current_substep', 1)
    if substep == 1:
        # 处理开头
        prompt = build_prompt(
            "你是一个写作辅导老师，正在指导学生写'我的心爱之物'的开头。",
            f"学生的开头是：{user_input}。请评价这个开头，并给出改进建议。"
        )
        response = call_openai_api(prompt)
        new_state = {**state, 'current_substep': 2}
        return {"response": response, "next_question": "现在让我们来写中间部分。请描述一个关于你心爱之物的事件。"}, new_state
    elif substep in [2, 3, 4]:
        # 处理中间部分的三个事件
        prompt = build_prompt(
            "你是一个写作辅导老师，正在指导学生写'我的心爱之物'的中间部分。",
            f"学生描述的事件是：{user_input}。请评价这个事件描述，并引导学生加入更多细节和感受。"
        )
        response = call_openai_api(prompt)
        new_state = {**state, 'current_substep': substep + 1}
        next_question = "请继续描述下一个事件。" if substep < 4 else "最后，让我们来写一个结尾。"
        return {"response": response, "next_question": next_question}, new_state
    elif substep == 5:
        # 处理结尾
        prompt = build_prompt(
            "你是一个写作辅导老师，正在指导学生写'我的心爱之物'的结尾。",
            f"学生的结尾是：{user_input}。请评价这个结尾，并给出改进建议。"
        )
        response = call_openai_api(prompt)
        new_state = {**state, 'current_step': 4, 'current_substep': 1}
        return {"response": response, "next_question": "现在让我们为你的作文起一个好题目。"}, new_state

def handle_step_4(user_input, state):
    """处理第四步：起题目和修改作文"""
    substep = state.get('current_substep', 1)
    if substep == 1:
        # 处理题目
        prompt = build_prompt(
            "你是一个写作辅导老师，正在帮助学生为'我的心爱之物'的作文起题目。",
            f"学生提出的题目是：{user_input}。请根据简明、具体、准确、新颖、生动的标准评价这个题目，并给出改进建议。"
        )
        response = call_openai_api(prompt)
        new_state = {**state, 'current_substep': 2}
        return {"response": response, "next_question": "最后，让我们来检查和修改整篇作文。"}, new_state
    elif substep == 2:
        # 整体修改建议
        prompt = build_prompt(
            "你是一个写作辅导老师，正在对学生的'我的心爱之物'作文进行最后的修改。",
            f"请根据以下标准对作文进行评价和修改建议：\n1. 内容真实，情感真挚\n2. 用词准确，特别是动词的使用\n3. 修辞手法的恰当运用\n4. 整体结构和详略安排\n\n学生的作文内容是：{user_input}"
        )
        response = call_openai_api(prompt)
        new_state = {**state, 'current_step': 5}  # 结束写作指导
        return {"response": response, "next_question": "恭喜你完成了作文！你对最终的结果满意吗？"}, new_state

def guided_interview():
    if request.method != 'POST':
        return jsonify({"error": "Only POST method is allowed"}), 405

    try:
        body = request.json
        user_input = body.get('message')
        state = body.get('state', {'current_step': 1, 'current_substep': 1})

        if not user_input:
            return jsonify({"error": "Message is required"}), 400

        response, new_state = guided_interview_flow(user_input, state)
        return jsonify({"response": response, "state": new_state}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 这里可以添加评分函数
def evaluate_essay(essay_content):
    """评估作文"""
    prompt = build_prompt(
        "你是一个严格的写作评判老师，正在对'我的心爱之物'主题的作文进行评分。",
        f"请根据以下五星评分标准对作文进行评分：\n1.书写认真 ☆\n2.书写认真、字数达标 ☆☆\n3.书写认真、字数达标、内容真实 ☆☆☆\n4.书写认真、字数达标、内容真实、详略得当 ☆☆☆☆\n5.书写认真、字数达标、内容真实、详略得当、情感真挚 ☆☆☆☆☆\n\n作文内容：{essay_content}"
    )
    return call_openai_api(prompt)

# 注意：需要在路由中添加对 guided_interview 的调用