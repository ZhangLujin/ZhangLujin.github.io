# /api/chat.py

from http.server import BaseHTTPRequestHandler
from .prompt_engineering import guided_essay
import json

def handler(request, response):
    if request.method == 'POST':
        try:
            # 解析请求体
            body = json.loads(request.body)

            # 调用 guided_essay 函数
            essay_response, status_code = guided_essay()

            # 设置响应
            response.status_code = status_code
            response.headers['Content-Type'] = 'application/json'
            return response.json(essay_response)

        except json.JSONDecodeError:
            response.status_code = 400
            return response.json({"error": "Invalid JSON"})

        except Exception as e:
            response.status_code = 500
            return response.json({"error": str(e)})
    else:
        response.status_code = 405
        return response.json({"error": "Method not allowed"})