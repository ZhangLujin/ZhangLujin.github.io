# chat.py

from flask import Flask
from prompt_engineering import chat

app = Flask(__name__)

@app.route('/api/chat', methods=['POST'])
def chat_route():
    return chat()
