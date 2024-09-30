import json
import os
from flask import request, jsonify
from .ai_service import call_openai_api

# 配置文件的路径，指向上级目录中的 config 文件夹里的 chat_flow_config.json 文件
CONFIG_PATH = os.path.join(os.path.dirname(__file__), '..', 'config', 'chat_flow_config.json')

# 加载配置文件函数
def load_config():
    try:
        # 打开配置文件并以 JSON 格式读取
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            config = json.load(f)
        # 打印加载的配置信息，格式化为缩进的 JSON 字符串
        print(f"Loaded config: {json.dumps(config, indent=2)}")
        return config
    except Exception as e:
        # 如果加载配置出错，打印错误信息并返回 None
        print(f"Error loading config: {str(e)}")
        return None

# 引导式写作流程函数，处理用户输入和当前状态
def guided_essay_flow(user_input, state):
    # 加载配置文件
    config = load_config()
    if not config:
        return "配置加载失败，请检查配置文件。", state

    # 获取当前步骤
    current_step = state.get('current_step', 0)
    step_config = config['flow'][current_step]

    # 获取对话记录，默认为空列表
    conversation = state.get('conversation', [])

    # 确保用户输入不为空
    if not user_input.strip():
        return "请提供学生的回答呀，没有回答我没法进行评估呢。", state

    # 将用户输入添加到对话记录中
    conversation.append({"role": "user", "content": user_input})

    # 生成提示内容，准备调用 AI 模型
    prompt = [
        {"role": "system", "content": step_config['system_prompt']},
        *conversation
    ]

    # 调用 AI 模型
    response = call_openai_api(prompt)

    # 将 AI 回复添加到对话记录中
    conversation.append({"role": "assistant", "content": response})

    # 更新状态
    new_state = {
        'current_step': current_step,
        'conversation': conversation
    }

    # 如果 AI 模型认为可以继续下一步，更新步骤
    if "继续下一步" in response:
        new_state['current_step'] = current_step + 1
        if new_state['current_step'] < len(config['flow']):
            return config['flow'][new_state['current_step']]['display_text'], new_state

    return response, new_state


# 处理聊天请求的 Flask 路由函数
def chat():
    # 仅允许 POST 请求
    if request.method != 'POST':
        return jsonify({"error": "Only POST method is allowed"}), 405

    try:
        # 获取请求体中的 JSON 数据
        body = request.json
        # 获取用户输入和状态，状态默认为初始状态
        user_input = body.get('message', '')
        state = body.get('state', {'current_step': 0, 'conversation': []})

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
        # 捕获异常并返回错误信息
        print(f"Error in chat function: {str(e)}")
        return jsonify({"error": str(e), "response": "抱歉，出现了一个错误。请重试或联系支持。"}), 500
