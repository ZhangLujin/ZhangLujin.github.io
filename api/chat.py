import json
from openai import OpenAI

# 初始化 OpenAI 客户端
client = OpenAI(
    api_key="b5afc8c2-957d-4de1-9881-fe464e2a2d0b",  # 你在代码中提到的 API 密钥
    base_url="https://ark.cn-beijing.volces.com/api/v3"  # 使用正确的 API URL
)

def handler(request):
    # 确保只允许 POST 请求
    if request.method != 'POST':
        return json.dumps({"error": "Only POST method is allowed"}), 405

    # 尝试解析请求体
    try:
        body = json.loads(request.body)
        user_input = body.get('message')
        if not user_input:
            return json.dumps({"error": "Message is required"}), 400
    except Exception as e:
        return json.dumps({"error": "Invalid request format"}), 400

    # 模拟调用 OpenAI 模型进行判断语气
    attitude_check = client.chat.completions.create(
        model="ep-20240924191053-2c9zd",  # 你的模型 ID
        messages=[
            {"role": "system", "content": "你是一个判断助手，帮助判断用户语言是否友好。"},
            {"role": "user", "content": f"用户语句：{user_input}。请判断该语句是否是友好的，如果是，回答'友好'，如果不是，回答'不友好'。"}
        ]
    )
    attitude_result = attitude_check.choices[0].message.content.strip()

    # 根据用户的语气判断，生成不同的回复
    if attitude_result == "友好":
        # 如果语气友好，生成正常回答
        completion = client.chat.completions.create(
            model="ep-20240924191053-2c9zd",  # 你的 AI 模型 ID
            messages=[
                {"role": "system", "content": "你是豆包，是由字节跳动开发的 AI 人工智能助手"},
                {"role": "user", "content": user_input}
            ]
        )
        response = {"response": completion.choices[0].message.content}
    else:
        # 如果语气不友好，提醒用户
        response = {"response": "请注意您的用词，保持文明对话。"}

    # 返回生成的 AI 回复
    return json.dumps(response), 200, {'Content-Type': 'application/json'}
