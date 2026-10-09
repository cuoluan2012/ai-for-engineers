"""
09-4 配套项目：私有化部署"设计规范助手"最小演示
=================================================

配套《从工程师到 AI 工程师》第 9 章 9.8 节。

做什么
------
把"设计规范助手"装成企业内网里一个**常驻服务**：
  - 服务端：用 Python 标准库 http.server 起一个本地服务（相当于内网服务器），
    收到问题后查"设计规范演示库"，返回按厂规口径的回答；
  - 客户端：像第 6 章调用云端 API 一样发 HTTP 请求（这次服务是你自己的）。

为什么这么做
------------
大模型私有化部署 = 把"推理服务"装进内网。本演示把**服务骨架**讲透：
请求长什么样、服务怎么响应、日志怎么留。真实模型接入点已标注——
把你的 mock_answer() 换成调用 vLLM/Ollama 的代码，骨架不用动。

运行方式：离线真实运行，零第三方依赖（只用标准库），无需联网。
"""

import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib import request

PORT = 8765

# ---------- 1. "设计规范演示库"（企业语料的最小形态） ----------

# 厂里的设计规范，只放了几条演示数据。真实场景里这里是：
# 企业知识库 + 微调后的模型，见 9.4 / 9.6 节。
RULE_BOOK = {
    "表面粗糙度": "45 钢轴配合面表面粗糙度默认 Ra1.6（厂规 9-2-3）",
    "倒角": "轴端倒角默认 C1（厂规 9-2-4）",
    "热处理": "45 钢轴调质处理，硬度 217~255 HB（厂规 9-2-5）",
}


def mock_answer(question: str) -> str:
    """
    演示版"推理"：在规则库里按关键词找答案。
    真实部署时，把这里替换成调用微调后模型的代码（vLLM / Ollama），
    例如：requests.post("http://内网模型服务/v1/chat/completions", ...)
    """
    for key, ans in RULE_BOOK.items():
        if key in question:
            return ans
    return "演示库未收录这个问题（真实部署时由模型回答，此处仅示意）"


# ---------- 2. 服务端 ----------

class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length) or b"{}")
        question = body.get("question", "")

        answer = mock_answer(question)

        # 留痕：记录请求与回答（呼应 9.7 审计）
        log = {"q": question, "a": answer, "mode": "mock"}
        print(f"    [服务端日志] {json.dumps(log, ensure_ascii=False)}")

        resp = json.dumps({"answer": answer, "source": "设计规范-演示库",
                           "mode": "mock"}, ensure_ascii=False).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(resp)))
        self.end_headers()
        self.wfile.write(resp)

    def log_message(self, fmt, *args):
        pass  # 关掉 http.server 自带的访问日志，只留上面的业务日志


def ask(question: str) -> dict:
    """客户端：像第 6 章调用云端 API 一样，向"自己家的服务"发请求。"""
    req = request.Request(
        f"http://127.0.0.1:{PORT}/answer",
        data=json.dumps({"question": question}).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    with request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))


# ---------- 3. 跑起来：起服务 → 发三次请求 → 关服务 ----------

print("=" * 66)
print("私有化部署演示：把'设计规范助手'装进内网（本机模拟）")
print("=" * 66)

server = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
thread = threading.Thread(target=server.serve_forever, daemon=True)
thread.start()
print(f"    服务已启动：http://127.0.0.1:{PORT}/answer（相当于内网服务器）")
print()

questions = [
    "45钢轴表面粗糙度默认值是多少？",
    "轴端倒角按什么标准？",
    "请算一下这根轴的疲劳强度。",
]
for q in questions:
    print(f"    [客户端请求] {q}")
    r = ask(q)
    print(f"    [客户端收到] {r['answer']}")
    print()

server.shutdown()
print("    服务已关闭。")
print()
print("小结：")
print("  · 服务端 = 常驻进程 + 规则库（真实场景里换成微调模型 + 知识库）；")
print("  · 客户端 = 和调用云端 API 一模一样，只是地址变成了内网地址；")
print("  · 日志留痕 = 9.7 数据审计的最小形态。")
print("  · 接入真实模型：把 mock_answer() 换成调用 vLLM/Ollama 的代码即可。")
