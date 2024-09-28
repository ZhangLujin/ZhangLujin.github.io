from flask import Flask, request, jsonify, render_template
from ai_service import AIService
from prompt_engineering import PromptEngineer

app = Flask(__name__)
ai_service = AIService(
    api_key="b5afc8c2-957d-4de1-9881-fe464e2a2d0b",
    base_url="https://ark.cn-beijing.volces.com/api/v3"
)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    user_input = data['message']
    response = PromptEngineer.chat_flow(ai_service, user_input)
    return jsonify({"response": response})

@app.route('/favicon.ico')
def favicon():
    return '', 204

if __name__ == '__main__':
    app.run(debug=True)