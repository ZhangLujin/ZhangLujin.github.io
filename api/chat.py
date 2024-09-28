from flask import Flask, request, jsonify
from ai_service import AIService
from prompt_engineering import PromptEngineer

app = Flask(__name__)
ai_service = AIService()

@app.route('/api/chat', methods=['POST'])
def chat():
    if request.method != 'POST':
        return jsonify({"error": "Only POST method is allowed"}), 405

    try:
        body = request.json
        user_input = body.get('message')
        if not user_input:
            return jsonify({"error": "Message is required"}), 400
    except Exception as e:
        return jsonify({"error": "Invalid request format"}), 400

    try:
        # 态度检查
        attitude_prompt = PromptEngineer.get_attitude_check_prompt(user_input)
        attitude_response = ai_service.get_completion(attitude_prompt)
        is_friendly = PromptEngineer.process_attitude_response(attitude_response)

        if is_friendly:
            # 生成友好回复
            chat_prompt = PromptEngineer.get_chatbot_prompt(user_input)
            response = ai_service.get_completion(chat_prompt)
        else:
            # 返回不友好提醒
            response = PromptEngineer.get_unfriendly_response()

        return jsonify({"response": response}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)