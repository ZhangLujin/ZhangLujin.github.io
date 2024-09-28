# /api/chat.py

from flask import Flask, request, jsonify
from .prompt_engineering import guided_interview  # 只导入 guided_interview 函数

app = Flask(__name__)

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

# 如果仍然需要 /api/chat 路由，可以这样实现：
@app.route('/api/chat', methods=['POST'])
def chat_route():
    return jsonify({"error": "This endpoint is not available. Please use /api/guided_interview for the guided writing process."}), 400