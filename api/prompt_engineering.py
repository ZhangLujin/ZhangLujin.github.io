# 导入必要的模块
import json
import os
from flask import request, jsonify
from .ai_service import call_openai_api

# 配置文件的路径
CONFIG_PATH = os.path.join(os.path.dirname(__file__), '..', 'config', 'chat_flow_config.json')

# 加载配置文件函数
def load_config():
    try:
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config
    except Exception as e:
        print(f"Error loading config: {str(e)}")
        return None

# 评估学生回答是否达到要求
def evaluate_student_answer(student_answer, step_config):
    if not student_answer.strip():
        return False  # 如果用户输入为空，则无法跳转到下一步

    evaluation_prompt = f"""
你是一名小学作文老师，请根据以下评估标准判断学生的回答是否达到了要求。

评估标准：
{step_config.get('evaluation_criteria', '')}

学生的回答：
{student_answer}

如果达到了要求，请回答"是"。如果未达到要求，请回答"否"。

请注意，只需回答"是"或"否"，不要提供多余的内容。
"""

    # 调用 OpenAI API
    evaluation_response = call_openai_api([{"role": "system", "content": evaluation_prompt}])

    # 检查回复是否包含“是”或“否”
    response_text = evaluation_response.strip()
    proceed = '是' in response_text

    return proceed

# 引导作文流程
def guided_essay_flow(user_input, state):
    config = load_config()
    if not config:
        return ("配置加载失败，请检查配置文件。", state, [])
    current_step = state.get('current_step', 0)
    max_completed_step = state.get('max_completed_step', 0)
    conversation = state.get('conversation', [])

    if current_step >= len(config['flow']):
        return ("写作流程已完成。", state, config['flow'])

    step_config = config['flow'][current_step]

    if user_input:
        conversation.append({"role": "user", "content": user_input})

    assistant_prompt = [
        {"role": "system", "content": step_config['system_prompt']},
        *conversation
    ]

    assistant_response = call_openai_api(assistant_prompt)
    conversation.append({"role": "assistant", "content": assistant_response})

    # 检查是否需要跳转到指定步骤
    if 'jump_to_step' in state:
        new_step = state['jump_to_step']
        if 0 <= new_step <= max_completed_step:
            new_state = {
                'current_step': new_step,
                'conversation': conversation,
                'max_completed_step': max_completed_step
            }
            return (config['flow'][new_step]['display_text'], new_state, config['flow'])
        else:
            return ("无效的阶段跳转请求。", state, config['flow'])

    proceed = False
    if 'force_next_step' in state:
        proceed = True
    else:
        # 使用评估函数判断是否可以进入下一步
        proceed = evaluate_student_answer(user_input, step_config)

    new_state = {
        'current_step': current_step,
        'conversation': conversation,
        'max_completed_step': max_completed_step
    }

    if proceed:
        new_state['current_step'] = current_step + 1
        new_state['max_completed_step'] = max(new_state['max_completed_step'], new_state['current_step'])
        if new_state['current_step'] < len(config['flow']):
            next_step_config = config['flow'][new_state['current_step']]
            return (next_step_config['display_text'], new_state, config['flow'])
        else:
            return ("写作流程已完成。", new_state, config['flow'])
    else:
        return (assistant_response, new_state, config['flow'])

# 处理聊天请求
def chat():
    if request.method != 'POST':
        return jsonify({"error": "Only POST method is allowed"}), 405
    try:
        body = request.json
        user_input = body.get('message', '')
        state = body.get('state', {'current_step': 0, 'conversation': [], 'max_completed_step': 0})
        # 检查是否需要跳转到特定阶段
        jump_to_step = body.get('jump_to_step', None)
        if jump_to_step is not None:
            state['jump_to_step'] = jump_to_step
        # 检查是否需要强制跳到下一步
        force_next_step = body.get('force_next_step', False)
        if force_next_step:
            state['force_next_step'] = True
        # 获取回复、更新的状态和结构信息
        response, new_state, structure = guided_essay_flow(user_input, state)
        # 返回回复和状态给前端
        return jsonify({"response": response, "state": new_state, "structure": structure}), 200
    except Exception as e:
        print(f"Error in chat function: {str(e)}")
        return jsonify({"error": str(e), "response": "抱歉，出现了一个错误。请重试或联系支持。"}), 500