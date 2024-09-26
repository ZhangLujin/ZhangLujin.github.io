# 从 Flask 框架中导入 Flask、request、jsonify、render_template 等模块
from flask import Flask, request, jsonify, render_template
import os  # 导入 os 模块，用于访问操作系统功能，例如读取环境变量
from openai import OpenAI  # 从 openai 库中导入 OpenAI 类，用于连接 OpenAI API

# 创建 Flask 应用实例
app = Flask(__name__)

# 创建 OpenAI 客户端，用于连接到特定的 API
client = OpenAI(
    # 通常情况下，API 密钥应从环境变量中读取，确保安全性
    # api_key = os.environ.get("ARK_API_KEY"),
    api_key = "b5afc8c2-957d-4de1-9881-fe464e2a2d0b",  # 这里 API 密钥被硬编码，不推荐，最好使用环境变量
    base_url = "https://ark.cn-beijing.volces.com/api/v3",  # 指定 API 的基础 URL，可能是不同区域的服务器
)

# 定义首页路由，当用户访问根路径时，将渲染首页模板
@app.route('/')
def index():
    # 使用 Flask 的 render_template 函数渲染 index.html 模板
    return render_template('index.html')

# 定义一个处理聊天请求的 API 路由，使用 POST 方法
@app.route('/api/chat', methods=['POST'])
def chat():
    # 从客户端的 HTTP 请求中提取 JSON 数据
    data = request.json
    # 获取用户发送的消息，保存在 user_input 变量中
    user_input = data['message']

    # 第一步：调用 OpenAI 模型，判断用户语气是否友好
    attitude_check = client.chat.completions.create(
        model="ep-20240924191053-2c9zd",  # 选择使用的模型
        messages=[
            {"role": "system", "content": "你是一个判断助手，帮助判断用户语言是否友好。"},
            {"role": "user", "content": f"用户语句：{user_input}。 请判断该语句是否是友好的，如果是，回答'友好'，如果不是，回答'不友好'。"}
        ],
    )

    # 获取判断结果
    attitude_result = attitude_check.choices[0].message.content.strip()

    # 第二步：根据判断结果决定如何回应用户
    if attitude_result == "友好":
        # 如果用户语气友好，正常生成回答
        completion = client.chat.completions.create(
            model="ep-20240924191053-2c9zd",  # 指定使用的 AI 模型
            messages=[
                {"role": "system", "content": "你是豆包，是由字节跳动开发的 AI 人工智能助手"},
                {"role": "user", "content": user_input}  # 用户的输入消息，来自客户端请求的 message 字段
            ],
        )
        # 将 AI 生成的第一个回复以 JSON 格式返回给客户端
        return jsonify({"response": completion.choices[0].message.content})
    else:
        # 如果用户语气不友好，返回提醒信息
        return jsonify({"response": "请注意您的用词，保持文明对话。"})

# 处理 favicon 请求的路由，浏览器会自动请求 favicon.ico
# 如果没有设置网站图标，这里返回 HTTP 204 响应（无内容）
@app.route('/favicon.ico')
def favicon():
    return '', 204

# 该部分用于启动 Flask 应用
# 当这个文件是主程序运行时，启动 Flask 开发服务器
if __name__ == '__main__':
    # 以调试模式运行 Flask 应用，调试模式会自动重新加载代码，并显示详细错误信息
    app.run(debug=True)
