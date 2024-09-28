import json
import os
from flask import request, jsonify
from .ai_service import call_openai_api

CONFIG_PATH = os.path.join(os.path.dirname(__file__), '..', 'config', 'chat_flow_config.json')

def load_config():
    try:
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            config = json.load(f)
        print(f"Loaded config: {json.dumps(config, indent=2)}")
        return config
    except Exception as e:
        print(f"Error loading config: {str(e)}")
        return None

def build_system_prompt(mode="writing"):
    config = load_config()
    if config and 'system_prompt' in config:
        return {"role": "system", "content": config['system_prompt']}
    else:
        print("Error: system_prompt not found in config")
        return {"role": "system", "content": "You are a helpful assistant."}

def guided_essay_flow(user_input, state):
    config = load_config()
    if not config:
        return "配置加载失败，请检查配置文件。", state

    current_step = state.get('current_step', 'start_guidance')
    print(f"Current step: {current_step}")

    step_config = next((step for step in config['flow'] if step['step'] == current_step), None)
    if not step_config:
        print(f"Step '{current_step}' not found in config")
        step_config = config['flow'][0]
        current_step = step_config['step']
        print(f"Falling back to first step: {current_step}")

    if not user_input and current_step == 'start_guidance':
        return step_config['prompt'], {'current_step': 0}

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
            new_state['current_step'] = current_index + 1
        else:
            new_state['current_step'] = len(config['flow'])  # 最后一步

    return response, new_state

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
        print(f"Error in chat function: {str(e)}")
        return jsonify({"error": str(e), "response": "抱歉，出现了一个错误。请重试或联系支持。"}), 500