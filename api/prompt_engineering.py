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
    step_answered = state.get('step_answered', {})  # 新增：用于存储每个阶段是否已经作答

    # 如果没有用户输入，并且用户尝试跳到下一步，则检查是否已经作答
    if 'force_next_step' in state:
        if step_answered.get(current_step):
            # 如果当前步骤已经作答，允许跳到下一步
            new_state = {
                'current_step': current_step + 1,
                'conversation': conversation,
                'step_answered': step_answered
            }
            if new_state['current_step'] < len(config['flow']):
                return config['flow'][new_state['current_step']]['display_text'], new_state
            else:
                return "写作流程已完成。", new_state
        else:
            # 如果用户没有作答，提示用户先作答
            return "请先在当前阶段作答，然后再尝试跳转到下一步。", state

    # 检查用户是否选择跳转到特定阶段
    if 'jump_to_step' in state:
        new_step = state['jump_to_step']
        if new_step >= 0 and new_step < len(config['flow']):
            new_state = {
                'current_step': new_step,
                'conversation': conversation,
                'step_answered': step_answered
            }
            return config['flow'][new_step]['display_text'], new_state
        else:
            return "无效的阶段跳转请求。", state

    # 如果用户输入为空且在第 0 步，返回当前步骤的提示文本
    if not user_input and current_step == 0:
        return step_config['display_text'], {'current_step': 0, 'conversation': conversation, 'step_answered': step_answered}

    # 准备调用 AI 模型的提示内容，包括系统提示和对话记录
    prompt = [
        {"role": "system", "content": step_config['system_prompt']},
        *conversation
    ]

    # 调用 OpenAI API 获取 AI 回复
    response = call_openai_api(prompt)
    conversation.append({"role": "assistant", "content": response})

    # 更新状态，标记当前步骤已作答
    step_answered[current_step] = True  # 当前步骤已作答

    new_state = {
        'current_step': current_step,
        'conversation': conversation,
        'step_answered': step_answered
    }

    # 如果 AI 回复中包含"继续下一步"，更新步骤并返回下一步的提示文本
    if "继续下一步" in response:
        new_state['current_step'] = current_step + 1
        if new_state['current_step'] < len(config['flow']):
            return config['flow'][new_state['current_step']]['display_text'], new_state

    return response, new_state

def chat():
    if request.method != 'POST':
        return jsonify({"error": "Only POST method is allowed"}), 405

    try:
        body = request.json
        user_input = body.get('message', '')
        state = body.get('state', {'current_step': 0, 'conversation': [], 'step_answered': {}})

        # 检查是否有跳转阶段的请求
        jump_to_step = body.get('jump_to_step', None)
        if jump_to_step is not None:
            state['jump_to_step'] = jump_to_step

        # 检查是否有强制跳到下一步的请求
        force_next_step = body.get('force_next_step', False)
        if force_next_step:
            state['force_next_step'] = True

        # 调用引导式写作流程，获取回复和新的状态
        response, new_state = guided_essay_flow(user_input, state)

        # 返回回复和新的状态
        return jsonify({"response": response, "state": new_state}), 200

    except Exception as e:
        print(f"Error in chat function: {str(e)}")
        return jsonify({"error": str(e), "response": "抱歉，出现了一个错误。请重试或联系支持。"}), 500
