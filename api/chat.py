# /api/chat.py

from flask import Flask
from .prompt_engineering import chat  # 使用相对导入方式，确保模块在同目录下正确引用

app = Flask(__name__)

@app.route('/api/chat', methods=['POST'])
def chat_route():
    return chat()  # 调用 prompt_engineering 中的 chat 函数
