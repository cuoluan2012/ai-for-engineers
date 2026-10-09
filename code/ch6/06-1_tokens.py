# -*- coding: utf-8 -*-
"""代码 6-1：Token 切分演示
本段做什么：用 OpenAI 的 tiktoken 工具演示"大语言模型怎么把文字切成最小单位 Token"，
并对比同一句话用中文和英文写，各消耗多少 Token（直接关系到费用和上下文窗口占用）。
运行前要装什么：pip install tiktoken
"""
import tiktoken

# 用 GPT-3.5/GPT-4 系列的编码方式（cl100k_base）
enc = tiktoken.get_encoding("cl100k_base")

print("=" * 60)
print("示例 1：一句混合了中文、英文和数字的设备检修记录")
text = "设备转速1450rpm，轴承温度62.5°C，建议立即停机检修。The bearing temperature is high."
tokens = enc.encode(text)
print(f"原文：{text}")
print(f"Token 数量：{len(tokens)}")
print(f"Token 编号（前 20 个）：{tokens[:20]}")
print(f"还原文本（应和原文一致）：{enc.decode(tokens)}")
print()

print("=" * 60)
print("示例 2：同一句话，中文写 vs 英文写，Token 消耗差多少")
text_cn = "设备转速1450转每分钟，轴承温度62.5摄氏度，建议立即停机检修。"
text_en = "The spindle speed is 1450 rpm and the bearing temperature is 62.5 degrees Celsius. Stop the machine for inspection."

n_cn = len(enc.encode(text_cn))
n_en = len(enc.encode(text_en))
print(f"中文版（{len(text_cn)} 个字符）：{n_cn} 个 Token")
print(f"英文版（{len(text_en)} 个字符）：{n_en} 个 Token")
print(f"中文版 Token 数是英文版的 {n_cn / n_en:.1f} 倍")
print()

print("=" * 60)
print("示例 3：逐 Token 拆开看（用英文演示，Token 更接近完整单词）")
demo_en = "Spindle speed 1450 rpm."
for i, t in enumerate(enc.encode(demo_en)[:12]):
    print(f"  Token[{i:2d}] = {t:5d}  ->  {enc.decode([t])!r}")
