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
        print(f"Loaded config: {json.dumps(config, indent=2)}")
        return config
    except Exception as e:
        print(f"Error loading config: {str(e)}")
        return None

def guided_essay_flow(user_input, state):
    config = load_config()
    if not config:
        return "配置加载失败，请检查配置文件。", state

    current_step = state.get('current_step', 0)
    print(f"Current step: {current_step}")

    if current_step >= len(config['flow']):
        return "写作流程已完成。", state

    step_config = config['flow'][current_step]
    conversation = state.get('conversation', [])

    # 检查是否有用户在当前步骤作答
    user_has_answered = any(
        message['role'] == 'user' and message['content'].strip() != ''
        for message in conversation
    )

    if 'force_next_step' in state:
        # 如果用户没有作答，则返回错误提示
        if not user_has_answered:
            return "请先在当前阶段作答，然后再跳转到下一步。", state
        # 如果用户已作答，允许强制跳到下一步
        state['current_step'] = current_step + 1
        if state['current_step'] < len(config['flow']):
            return config['flow'][state['current_step']]['display_text'], state

    # 处理正常的对话流程
    conversation.append({"role": "user", "content": user_input})

    if not user_input and current_step == 0:
        return step_config['display_text'], {'current_step': 0, 'conversation': conversation}

    prompt = [
        {"role": "system", "content": step_config['system_prompt']},
        *conversation
    ]

    response = call_openai_api(prompt)
    conversation.append({"role": "assistant", "content": response})

    state['conversation'] = conversation

    if "继续下一步" in response:
        state['current_step'] = current_step + 1
        if state['current_step'] < len(config['flow']):
            return config['flow'][state['current_step']]['display_text'], state

    return response, state


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

        response, new_state = guided_essay_flow(user_input, state)

        return jsonify({"response": response, "state": new_state}), 200

    except Exception as e:
        print(f"Error in chat function: {str(e)}")
        return jsonify({"error": str(e), "response": "抱歉，出现了一个错误。请重试或联系支持。"}), 500
