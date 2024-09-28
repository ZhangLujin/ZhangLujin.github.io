from flask import Flask, request, jsonify
import os
from openai import OpenAI
from prompt_engineering import PromptEngineer

# 从环境变量中读取 API 密钥
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "b5afc8c2-957d-4de1-9881-fe464e2a2d0b")

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

    response = PromptEngineer.process_chat(client, user_input)

    if "error" in response:
        return jsonify(response), 500
    else:
        return jsonify(response), 200

if __name__ == '__main__':
    app.run(debug=True)