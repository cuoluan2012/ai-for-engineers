# -*- coding: utf-8 -*-
"""代码 6-3：标准解读提示词模板 + 输出格式检查函数
本段做什么：① 构造一个"解读标准条款"的提示词模板；② 写一个检查函数，
验证模型输出是否包含"白话解释 / 检验要点 / 易错点"三部分、内容是否非空。
用一段模拟的模型输出演示检查函数怎么拦下不合格结果。
运行前要装什么：无需额外安装（纯 Python 标准库）
"""

# ---------- 提示词模板 ----------
TEMPLATE = """【角色】你是一名机械行业标准解读专家，熟悉 GB、JB 等国家和行业标准。

【任务】请把下面的标准条款改写成三部分：
1. 白话解释：用车间工人能听懂的话解释这条规则在说什么
2. 检验要点：检查时具体要做什么、看什么、量什么
3. 易错点：执行这条规则时最容易忽略或搞错的地方

【条款】
{article}

【要求】三部分都要有；每部分不超过 3 句话；不得编造条款里没有的要求。"""


def build_prompt(article):
    """把标准条款装进模板，返回完整提示词。"""
    return TEMPLATE.format(article=article)


# ---------- 输出格式检查函数 ----------
REQUIRED_SECTIONS = ["白话解释", "检验要点", "易错点"]


def check_output(text):
    """检查模型输出是否结构完整、内容非空。返回 (是否通过, 问题列表)。"""
    problems = []
    for section in REQUIRED_SECTIONS:
        if section not in text:
            problems.append(f"缺少「{section}」部分")
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    if not lines:
        problems.append("输出为空")
    if len(text) < 20:
        problems.append("输出过短，疑似没认真回答")
    return (len(problems) == 0, problems)


# ---------- 演示 ----------
article = "示例条款（非标准原文）：焊缝外观不得有裂纹、气孔、咬边等缺陷，重要焊缝应进行无损检测。"

print("=" * 60)
print("渲染后的完整提示词：")
prompt = build_prompt(article)
print(prompt)
print()

print("=" * 60)
print("模拟模型输出 1：结构完整（应该通过检查）")
mock_ok = """白话解释：焊完之后表面不能有裂纹、气孔、咬边这类毛病，重要的焊缝还要用仪器探伤。
检验要点：先目视检查全部焊缝表面，再对重要焊缝安排无损检测并记录结果。
易错点：气孔很小容易被忽略，咬边在接头转角处最常出现。"""
passed, problems = check_output(mock_ok)
print(f"检查结果：通过={passed}，问题={problems}")
print()

print("=" * 60)
print("模拟模型输出 2：漏掉一个部分（应该被拦下）")
mock_bad = """白话解释：焊缝表面要光滑。
检验要点：目视检查。"""
passed, problems = check_output(mock_bad)
print(f"检查结果：通过={passed}，问题={problems}")
