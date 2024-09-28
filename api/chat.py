# /api/chat.py

from flask import Flask, request, jsonify
from .prompt_engineering import chat, guided_interview  # 导入两个主要函数

app = Flask(__name__)

@app.route('/api/chat', methods=['POST'])
def chat_route():
    return chat()  # 调用 prompt_engineering 中的 chat 函数

@app.route('/api/guided_interview', methods=['POST'])
def guided_interview_route():
    return guided_interview()  # 调用 prompt_engineering 中的 guided_interview 函数

# 错误处理
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500