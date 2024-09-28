# /api/chat.py

from http.server import BaseHTTPRequestHandler
from .prompt_engineering import guided_essay
import json

def handle_request(request):
    # 读取请求体
    content_length = int(request.headers.get('Content-Length', 0))
    body = request.rfile.read(content_length).decode('utf-8')

    try:
        # 解析 JSON 数据
        data = json.loads(body)

        # 调用 guided_essay 函数
        response, status_code = guided_essay()

        # 将响应转换为 JSON 字符串
        response_body = json.dumps(response)

        # 设置响应头
        request.send_response(status_code)
        request.send_header('Content-Type', 'application/json')
        request.end_headers()

        # 发送响应体
        request.wfile.write(response_body.encode('utf-8'))

    except json.JSONDecodeError:
        request.send_response(400)
        request.send_header('Content-Type', 'application/json')
        request.end_headers()
        request.wfile.write(json.dumps({"error": "Invalid JSON"}).encode('utf-8'))

    except Exception as e:
        request.send_response(500)
        request.send_header('Content-Type', 'application/json')
        request.end_headers()
        request.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))

class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        handle_request(self)

def handler(event, context):
    return Handler.handler(event, context)