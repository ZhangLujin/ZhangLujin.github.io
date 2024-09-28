# /api/chat.py

from flask import Flask, request, jsonify
from .prompt_engineering import guided_essay  # 使用相对导入方式，导入新的 guided_essay 函数

app = Flask(__name__)

@app.route('/api/chat', methods=['POST'])
def chat_route():
    try:
        # 获取请求数据
        data = request.json
        user_input = data.get('message')
        state = data.get('state', {})

        # 调用 guided_essay 函数
        response, new_state = guided_essay(user_input, state)

        # 返回响应
        return jsonify({"response": response, "state": new_state}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Vercel 需要一个 handler 函数作为入口点
def handler(request):
    with app.request_context(request):
        return app.dispatch_request()