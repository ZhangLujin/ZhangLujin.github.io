# /api/chat.py

from flask import Flask, request, jsonify
from .prompt_engineering import guided_essay  # 只导入 guided_essay 函数

app = Flask(__name__)

@app.route('/api/essay-guidance', methods=['POST'])
def essay_guidance_route():
    return guided_essay()  # 调用作文引导函数

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

# 如果需要保留 /api/chat 路由以保持向后兼容性，可以添加以下代码
@app.route('/api/chat', methods=['POST'])
def chat_route():
    return jsonify({"message": "This endpoint has been deprecated. Please use /api/essay-guidance for the new essay guidance feature."}), 301