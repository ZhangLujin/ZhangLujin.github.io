import json
import os
from flask import request, jsonify
from .ai_service import call_openai_api

CONFIG_PATH = os.path.join(os.path.dirname(__file__), '..', 'config', 'chat_flow_config.json')

def load_config():
    try:
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config
    except Exception as e:
        print(f"Error loading config: {str(e)}")
        return None

def guided_essay_flow(user_input, state):
    config = load_config()
    if not config:
        return "配置加载失败，请检查配置文件。", state, []

    current_step = state.get('current_step', 0)
    max_completed_step = state.get('max_completed_step', 0)
    conversation = state.get('conversation', [])

    if current_step >= len(config['flow']):
        return "写作流程已完成。", state, config['flow']

    step_config = config['flow'][current_step]

    if user_input:
        conversation.append({"role": "user", "content": user_input})

    if 'jump_to_step' in state:
        new_step = state['jump_to_step']
        if new_step >= 0 and new_step <= max_completed_step:
            max_completed_step = max(max_completed_step, new_step)
            new_state = {
                'current_step': new_step,
                'conversation': conversation,
                'max_completed_step': max_completed_step
            }
            return config['flow'][new_step]['display_text'], new_state, config['flow']
        else:
            return "无效的阶段跳转请求。", state, config['flow']

    if not user_input and current_step == 0:
        return step_config['display_text'], {'current_step': 0, 'conversation': conversation, 'max_completed_step': 0}, config['flow']

    prompt = [
        {"role": "system", "content": step_config['system_prompt']},
        *conversation
    ]

    response = call_openai_api(prompt)
    conversation.append({"role": "assistant", "content": response})

    new_state = {
        'current_step': current_step,
        'conversation': conversation,
        'max_completed_step': max_completed_step
    }

    # 检查AI回复中是否包含"继续下一步"或用户是否请求强制跳到下一步
    if "继续下一步" in response or state.get('force_next_step', False):
        new_state['current_step'] = current_step + 1
        new_state['max_completed_step'] = max(new_state['max_completed_step'], new_state['current_step'])
        if new_state['current_step'] < len(config['flow']):
            return config['flow'][new_state['current_step']]['display_text'], new_state, config['flow']
        else:
            return "写作流程已完成。", new_state, config['flow']

    return response, new_state, config['flow']

def chat():
    if request.method != 'POST':
        return jsonify({"error": "Only POST method is allowed"}), 405

    try:
        body = request.json
        user_input = body.get('message', '')
        state = body.get('state', {'current_step': 0, 'conversation': [], 'max_completed_step': 0})

        jump_to_step = body.get('jump_to_step')
        if jump_to_step is not None:
            state['jump_to_step'] = jump_to_step

        force_next_step = body.get('force_next_step', False)
        if force_next_step:
            state['force_next_step'] = True

        response, new_state, structure = guided_essay_flow(user_input, state)

        return jsonify({"response": response, "state": new_state, "structure": structure}), 200

    except Exception as e:
        print(f"Error in chat function: {str(e)}")
        return jsonify({"error": str(e), "response": "抱歉，出现了一个错误。请重试或联系支持。"}), 500