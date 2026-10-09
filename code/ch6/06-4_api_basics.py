# -*- coding: utf-8 -*-
"""代码 6-4：LLM API 调用完整示例（OpenAI 兼容格式）
本段做什么：演示"程序怎么调用大模型 API"——构造请求、发送、拿到响应。
安全要点：API Key 从环境变量读取，绝不写进代码。
两种模式：
  有 Key（设置了环境变量 LLM_API_KEY）：真实调用接口；
  无 Key：mock 模式，打印完整请求结构 + 模拟响应，用于本地验证代码本身没问题。
运行前要装什么：pip install requests python-dotenv
"""
import json
import os
import requests
from dotenv import load_dotenv

load_dotenv()  # 从 .env 文件读环境变量（可选）

API_KEY = os.environ.get("LLM_API_KEY", "")
BASE_URL = os.environ.get("LLM_BASE_URL", "https://api.openai.com/v1")
MODEL = os.environ.get("LLM_MODEL", "gpt-4o-mini")


def build_messages(prompt, system="你是一名机械工程师助理。"):
    """构造对话消息：系统角色 + 用户提问。"""
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": prompt},
    ]


def build_payload(messages, temperature=0.3, max_tokens=500):
    """构造请求体：消息、随机性参数、输出长度上限。"""
    return {
        "model": MODEL,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }


def mock_response(payload):
    """无 Key 时的模拟响应：展示真实的响应结构长什么样。"""
    return {
        "id": "chatcmpl-mock-0001",
        "object": "chat.completion",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": "【模拟输出】主轴转速 1450rpm、温度 62.5°C 属正常范围。"
                    "若温度持续超过 75°C，应停机检查轴承润滑。",
                },
                "finish_reason": "stop",
            }
        ],
        "usage": {"prompt_tokens": 210, "completion_tokens": 42, "total_tokens": 252},
    }


def call_llm(prompt):
    """调用大模型 API，返回 (是否真实调用, 文本输出)。"""
    messages = build_messages(prompt)
    payload = build_payload(messages)

    if not API_KEY:
        # mock 模式：打印请求结构，返回模拟响应
        print("（未设置 LLM_API_KEY，进入 mock 模式，不发起真实请求）")
        print(f"请求地址：POST {BASE_URL}/chat/completions")
        print(f"请求头：Authorization: Bearer <你的API_KEY>（脱敏显示）")
        print(f"请求体：{json.dumps(payload, ensure_ascii=False, indent=2)}")
        resp = mock_response(payload)
        print(f"响应体：{json.dumps(resp, ensure_ascii=False, indent=2)}")
        return False, resp["choices"][0]["message"]["content"]

    # 真实模式
    resp = requests.post(
        f"{BASE_URL}/chat/completions",
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
        },
        json=payload,
        timeout=60,
    )
    resp.raise_for_status()
    data = resp.json()
    return True, data["choices"][0]["message"]["content"]


if __name__ == "__main__":
    prompt = "主轴转速1450rpm，轴承温度62.5°C。请问这个状态正常吗？需要注意什么？"
    real, answer = call_llm(prompt)
    print()
    print("=" * 60)
    print(f"调用方式：{'真实 API 调用' if real else 'mock 模式（未真实调用）'}")
    print(f"模型返回：{answer}")
