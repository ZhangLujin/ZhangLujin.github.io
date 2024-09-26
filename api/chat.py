from flask import Flask, request, jsonify
import os
from openai import OpenAI

# 从环境变量中读取 API 密钥
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your-api-key-here")

# 初始化 OpenAI 客户端
client = OpenAI(
    api_key=OPENAI_API_KEY,
    base_url="https://ark.cn-beijing.volces.com/api/v3"
)

# 创建 Flask 应用实例
app = Flask(__name__)

@app.route('/api/chat', methods=['POST'])
def chat():
    # 确保只允许 POST 请求
    if request.method != 'POST':
        return jsonify({"error": "Only POST method is allowed"}), 405

    # 尝试解析请求体
    try:
        body = request.json
        user_input = body.get('message')
        if not user_input:
            return jsonify({"error": "Message is required"}), 400
    except Exception as e:
        return jsonify({"error": "Invalid request format"}), 400

    try:
        # 调用 OpenAI 模型进行判断语气
        attitude_check = client.chat.completions.create(
            model="ep-20240924191053-2c9zd",  # 你的模型 ID
            messages=[
                {"role": "system", "content": "你是一个判断助手，帮助判断用户语言是否友好。"},
                {"role": "user", "content": f"用户语句：{user_input}。请判断该语句是否是友好的，如果是，回答'友好'，如果不是，回答'不友好'。"}
            ]
        )
        attitude_result = attitude_check.choices[0].message.content.strip()

        # 根据用户的语气判断，生成不同的回复
        if attitude_result == "友好":
            completion = client.chat.completions.create(
                model="ep-20240924191053-2c9zd",  # 你的 AI 模型 ID
                messages=[
                    {"role": "system", "content": "你是豆包，是由字节跳动开发的 AI 人工智能助手"},
                    {"role": "user", "content": user_input}
                ]
            )
            response = {"response": completion.choices[0].message.content}
        else:
            response = {"response": "请注意您的用词，保持文明对话。"}
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify(response), 200
