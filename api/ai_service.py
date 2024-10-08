# /api/ai_service.py

import os
from openai import OpenAI

# 从环境变量中读取 API 密钥
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "b5afc8c2-957d-4de1-9881-fe464e2a2d0b")

# 初始化 OpenAI 客户端
client = OpenAI(
    api_key=OPENAI_API_KEY,
    base_url="https://ark.cn-beijing.volces.com/api/v3"
)

def call_openai_api(messages, model="ep-20240924191053-2c9zd"):
    """
    调用 OpenAI 模型并返回结果。

    :param messages: 构建好的消息列表
    :param model: 使用的模型 ID
    :return: 模型生成的回复内容
    """
    response = client.chat.completions.create(
        model=model,
        messages=messages
    )
    return response.choices[0].message.content.strip()
