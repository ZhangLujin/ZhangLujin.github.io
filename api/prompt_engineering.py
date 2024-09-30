import json
import os
from flask import request, jsonify
from .ai_service import call_openai_api

# 配置文件的路径，指向上级目录中的 config 文件夹里的 chat_flow_config.json 文件
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

def guided_essay_flow(user_input, state):
    config = load_config()
    if not config:
        # 如果加载配置失败，返回错误信息、状态和空结构
        return "配置加载失败，请检查配置文件。", state, []

    current_step = state.get('current_step', 0)

    if current_step >= len(config['flow']):
        # 如果流程完成，返回完成信息、状态和步骤结构
        return "写作流程已完成。", state, config['flow']

    step_config = config['flow'][current_step]
    conversation = state.get('conversation', [])
    conversation.append({"role": "user", "content": user_input})

    if 'jump_to_step' in state:
        new_step = state['jump_to_step']
        if new_step >= 0 and new_step < len(config['flow']):
            new_state = {
                'current_step': new_step,
                'conversation': conversation
            }
            return config['flow'][new_step]['display_text'], new_state, config['flow']
        else:
            return "无效的阶段跳转请求。", state, config['flow']

    if not user_input and current_step == 0:
        return step_config['display_text'], {'current_step': 0, 'conversation': conversation}, config['flow']

    prompt = [
        {"role": "system", "content": step_config['system_prompt']},
        *conversation
    ]

    response = call_openai_api(prompt)
    conversation.append({"role": "assistant", "content": response})

    new_state = {
        'current_step': current_step,
        'conversation': conversation
    }

    if "继续下一步" in response or 'force_next_step' in state:
        new_state['current_step'] = current_step + 1
        if new_state['current_step'] < len(config['flow']):
            return config['flow'][new_state['current_step']]['display_text'], new_state, config['flow']

    return response, new_state, config['flow']

def chat():
    if request.method != 'POST':
        return jsonify({"error": "Only POST method is allowed"}), 405

    try:
        body = request.json
        user_input = body.get('message', '')
        state = body.get('state', {'current_step': 0, 'conversation': []})

        jump_to_step = body.get('jump_to_step', None)
        if jump_to_step is not None:
            state['jump_to_step'] = jump_to_step

        force_next_step = body.get('force_next_step', False)
        if force_next_step:
            state['force_next_step'] = True

        # 始终解包三个值，确保不会出现 unpack 错误
        response, new_state, structure = guided_essay_flow(user_input, state)

        return jsonify({"response": response, "state": new_state, "structure": structure}), 200

    except Exception as e:
        print(f"Error in chat function: {str(e)}")
        return jsonify({"error": str(e), "response": "抱歉，出现了一个错误。请重试或联系支持。"}), 500
