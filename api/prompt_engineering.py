import json
import os
from flask import request, jsonify
from .ai_service import call_openai_api

CONFIG_PATH = os.path.join(os.path.dirname(__file__), '..', 'config', 'chat_flow_config.json')

def load_config():
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def build_system_prompt(mode="writing"):
    config = load_config()
    return {"role": "system", "content": config['system_prompt']}

def guided_essay_flow(user_input, state):
    config = load_config()
    current_step = state.get('current_step', 'start_guidance')

    step_config = next((step for step in config['flow'] if step['step'] == current_step), None)
    if not step_config:
        return "对不起，我无法继续指导。", state

    if not user_input and current_step == 'start_guidance':
        return step_config['prompt'], state

    prompt = [
        build_system_prompt(),
        {"role": "assistant", "content": step_config['prompt']},
        {"role": "user", "content": user_input},
        {"role": "assistant", "content": step_config['evaluation']}
    ]

    response = call_openai_api(prompt)
    new_state = state.copy()

    if "继续下一步" in response:
        current_index = config['flow'].index(step_config)
        if current_index + 1 < len(config['flow']):
            new_state['current_step'] = config['flow'][current_index + 1]['step']

    return response, new_state

def chat():
    if request.method != 'POST':
        return jsonify({"error": "Only POST method is allowed"}), 405

    try:
        body = request.json
        user_input = body.get('message', '')
        state = body.get('state', {'current_step': 'start_guidance'})

        response, new_state = guided_essay_flow(user_input, state)
        return jsonify({"response": response, "state": new_state}), 200

    except Exception as e:
        print(f"Error in chat function: {str(e)}")  # 添加服务器端日志
        return jsonify({"error": str(e), "response": "抱歉，出现了一个错误。请重试或联系支持。"}), 500