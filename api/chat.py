from flask import Flask, request, jsonify
from ai_service import AIService
from prompt_engineering import PromptEngineer

app = Flask(__name__)
ai_service = AIService()

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

    response, status_code = PromptEngineer.process_chat(ai_service, user_input)
    return jsonify(response), status_code

if __name__ == '__main__':
    app.run(debug=True)