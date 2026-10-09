# -*- coding: utf-8 -*-
"""代码 6-2：提示词四要素模板（角色 / 上下文 / 示例 / 约束）
本段做什么：用 Python 字符串模板演示"怎么把提示词工程化"——
把角色、上下文、示例、约束四个要素拼装成一段完整提示词，方便批量复用、统一管理。
运行前要装什么：无需额外安装（纯 Python 标准库）
"""


def build_prompt(role, context, example, constraint):
    """把提示词四要素拼装成一段完整提示词。"""
    parts = []
    if role:
        parts.append(f"【角色】{role}")
    if context:
        parts.append(f"【背景】{context}")
    if example:
        parts.append(f"【示例】{example}")
    if constraint:
        parts.append(f"【要求】{constraint}")
    return "\n\n".join(parts)


print("=" * 60)
print("场景 A：翻译图纸说明（英文 → 中文，术语保真）")
prompt_a = build_prompt(
    role="你是一名有 20 年经验的机械工程师，精通英文图纸和技术手册翻译。",
    context="下面是一段设备图纸上的英文说明，请翻译成中文，保留所有尺寸和单位，术语使用国内机械行业通用叫法。",
    example="原文：The spindle shall be dynamically balanced to G2.5 grade. 译文：主轴应进行动平衡，等级达到 G2.5 级。",
    constraint="只输出译文，不要解释；尺寸、公差、单位必须原样保留。",
)
print(prompt_a)
print()

print("=" * 60)
print("场景 B：把会议记录整理成工单（表格输出）")
prompt_b = build_prompt(
    role="你是设备科的助理工程师，负责把会议记录整理成可执行工单。",
    context="下面是今天设备科会议的口语记录，请整理成表格：任务、负责人、完成期限三列。",
    example="记录：小王说下周要换 3 号机的轴承。整理后：| 任务 | 负责人 | 期限 | | 更换 3 号机轴承 | 小王 | 下周 |",
    constraint="表格用 Markdown 格式；没提到负责人的写'待定'；不要添加记录里没有的内容。",
)
print(prompt_b)
print()

print("=" * 60)
print("技巧：把模板固化成函数，参数一换就能复用")
article = "检验规则：每批抽取 5 件，按 GB/T 2828.1 判定。"
prompt_c = build_prompt(
    role="你是机械产品检验工程师。",
    context=f"请把下面这条检验规则改写成'白话解释 + 检验要点 + 易错点'三部分。\n规则原文：{article}",
    example="规则：外观不得有划伤。白话解释：表面不能有肉眼可见的划痕。检验要点：目视检查全部表面。易错点：忽略端面倒角处。",
    constraint="三部分都要有，每部分不超过 3 句话。",
)
print(prompt_c)
