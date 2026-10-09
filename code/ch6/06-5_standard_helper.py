# -*- coding: utf-8 -*-
"""代码 6-5：标准解读小助手（第 6 章配套项目，约 100 行）
本段做什么：输入一段标准条款，输出"白话解释 + 检验要点 + 易错点"，
并对输出做结构检查（缺部分就提示），防止把模型"编的内容"直接当结论用。
运行前要装什么：pip install requests python-dotenv
    （可选）设置环境变量 LLM_API_KEY 后为真实调用；未设置则用 mock 输出演示全流程。
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.environ.get("LLM_API_KEY", "")
BASE_URL = os.environ.get("LLM_BASE_URL", "https://api.openai.com/v1")
MODEL = os.environ.get("LLM_MODEL", "gpt-4o-mini")

TEMPLATE = """【角色】你是一名机械行业标准解读专家。

【任务】把下面条款改写成三部分：
1. 白话解释：用车间工人能听懂的话解释
2. 检验要点：检查时具体做什么
3. 易错点：最容易忽略或搞错的地方

【条款】
{article}

【要求】三部分都要有；每部分不超过 3 句话；不得编造条款里没有的要求。"""

REQUIRED_SECTIONS = ["白话解释", "检验要点", "易错点"]


def build_prompt(article):
    return TEMPLATE.format(article=article)


def call_llm(prompt):
    """调用大模型；无 Key 时返回一段标注清楚的模拟输出。"""
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "你是一名机械行业标准解读专家。"},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.2,
        "max_tokens": 600,
    }
    if not API_KEY:
        return "【mock 输出，非真实模型结果】\n" + "白话解释：条款要求焊缝表面不得有裂纹、气孔、咬边等缺陷，重要焊缝还需无损检测。\n检验要点：目视检查全部焊缝表面，重要焊缝安排无损检测并留记录。\n易错点：气孔小易漏检；咬边在转角处最常出现。"
    resp = requests.post(
        f"{BASE_URL}/chat/completions",
        headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
        json=payload,
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]


def check_output(text):
    """结果检查清单：结构是否完整、内容是否非空。返回 (通过, 问题列表)。"""
    problems = []
    for section in REQUIRED_SECTIONS:
        if section not in text:
            problems.append(f"缺少「{section}」部分")
    if len(text) < 30:
        problems.append("输出过短")
    if "mock" in text:
        problems.append("当前为 mock 输出，配置 API Key 后才是真实结果")
    return (len(problems) == 0, problems)


def main():
    print("标准解读小助手 v0.1（第 6 章配套项目）")
    print("-" * 60)
    article = input("请粘贴一条标准条款（回车使用示例条款）：\n").strip()
    if not article:
        article = "示例条款（非标准原文）：焊缝外观不得有裂纹、气孔、咬边等缺陷，重要焊缝应进行无损检测。"
        print(f"使用示例条款：{article}")

    prompt = build_prompt(article)
    print("\n[1/3] 提示词已构造（%d 字符）" % len(prompt))

    answer = call_llm(prompt)
    print("\n[2/3] 模型输出：\n" + answer)

    passed, problems = check_output(answer)
    print("\n[3/3] 检查清单：" + ("通过 ✔" if passed else "发现问题 ✘"))
    for p in problems:
        print("  - " + p)
    if not passed:
        print("提示：不要把上面的输出直接当结论，先修正问题或人工复核。")


if __name__ == "__main__":
    main()
