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

# 引导作文流程
def guided_essay_flow(user_input, state):
    config = load_config()
    if not config:
        # 如果加载配置失败，返回错误信息、状态和空结构
        return "配置加载失败，请检查配置文件。", state, []

    current_step = state.get('current_step', 0)
    max_completed_step = state.get('max_completed_step', 0)  # 新增，记录用户到达的最高步骤

    if current_step >= len(config['flow']):
        # 如果流程完成，返回完成信息、状态和步骤结构
        return "写作流程已完成。", state, config['flow']

    step_config = config['flow'][current_step]
    conversation = state.get('conversation', [])

    # 将用户输入添加到对话记录中
    if user_input:
        conversation.append({"role": "user", "content": user_input})

    # 跳转到特定步骤，只能跳到用户到过的最大步骤
    if 'jump_to_step' in state:
        new_step = state['jump_to_step']
        if new_step >= 0 and new_step <= max_completed_step:
            new_state = {
                'current_step': new_step,
                'conversation': conversation,
                'max_completed_step': max_completed_step  # 保留最高步骤记录
            }
            return config['flow'][new_step]['display_text'], new_state, config['flow']
        else:
            return "无效的阶段跳转请求。", state, config['flow']

    # 第一步时无需用户输入直接展示
    if not user_input and current_step == 0:
        return step_config['display_text'], {'current_step': 0, 'conversation': conversation, 'max_completed_step': 0}, config['flow']

    # 准备调用 AI 模型的提示内容，包括系统提示和对话记录
    prompt = [
        {"role": "system", "content": step_config['system_prompt']},
        *conversation
    ]

    # 调用 OpenAI API 获取 AI 回复
    response = call_openai_api(prompt)
    conversation.append({"role": "assistant", "content": response})

    # 更新状态，保留当前步骤和对话记录
    new_state = {
        'current_step': current_step,
        'conversation': conversation,
        'max_completed_step': max_completed_step
    }

    # 当 AI 回复中包含“继续下一步”或者用户输入有效并强制跳到下一步时
    if "继续下一步" in response or 'force_next_step' in state:
        if user_input:  # 确保用户在当前阶段提供了有效的输入
            # 更新到下一步，并更新用户已完成的最高步骤
            new_state['current_step'] = current_step + 1
            new_state['max_completed_step'] = max(new_state['max_completed_step'], new_state['current_step'])
            if new_state['current_step'] < len(config['flow']):
                return config['flow'][new_state['current_step']]['display_text'], new_state, config['flow']
            else:
                return "写作流程已完成。", new_state, config['flow']
        else:
            return "请在当前阶段提供有效的输入，才能跳到下一步。", new_state, config['flow']

    return response, new_state, config['flow']

# 处理聊天请求
def chat():
    if request.method != 'POST':
        return jsonify({"error": "Only POST method is allowed"}), 405

    try:
        body = request.json
        user_input = body.get('message', '')
        state = body.get('state', {'current_step': 0, 'conversation': [], 'max_completed_step': 0})

        # 检查是否需要跳到特定阶段
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
