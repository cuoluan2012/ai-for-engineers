"""
09-3 量化原理演示：用精度换资源，省多少、亏多少
================================================

配套《从工程师到 AI 工程师》第 9 章 9.5 节。

问题背景
--------
一个 70 亿参数的模型，用 float32（每个数占 4 字节）存储要占 28GB 显存，
普通企业显卡根本装不下。量化就是把模型里的数字从"高精度"换成"低精度"，
例如 float16（2 字节）或 int8（1 字节）——显存立刻减半、再减半，
代价是数值精度损失，回答质量可能打折扣。

本演示做两件事：
  1. 拿几个典型数值，看 float32 → float16 → int8 之后误差有多大；
  2. 给一张"参数量 × 精度"的显存估算表，算算省多少。

运行方式：离线真实运行，零第三方依赖，纯标准库。
"""

import struct
import math

# ---------- 1. 三种精度的"存回再读回" ----------

def to_float16(v):
    """float32 → float16 → float32（用标准库 struct 的 'e' 半精度格式）。"""
    return struct.unpack("e", struct.pack("e", v))[0]


def to_int8(v, scale):
    """对称量化：v → 整数刻度 → 反量化回近似值。"""
    q = round(v / scale)
    q = max(-127, min(127, q))     # int8 范围 -127~127
    return q * scale, q


# 一组典型权重值：大数、小数、π、循环小数……
values = [0.1, 0.125, 3.14159, 0.333333, 123.456, 1.0, 0.001]

print("=" * 72)
print("一、数值精度损失对比")
print("=" * 72)
print(f"{'原值':>10} {'float32':>10} {'float16':>10} {'16位误差':>10} "
      f"{'int8存回':>10} {'8位误差':>10}")
print("-" * 72)

max_abs = max(abs(v) for v in values)
scale8 = max_abs / 127.0

for v in values:
    f32 = struct.unpack("f", struct.pack("f", v))[0]
    f16 = to_float16(v)
    i8, _ = to_int8(v, scale8)
    print(f"{v:>10.4f} {f32:>10.6f} {f16:>10.6f} {abs(v-f16):>10.6f} "
          f"{i8:>10.6f} {abs(v-i8):>10.6f}")

print("-" * 72)
print("解读：float16 对大多数数误差在 1e-4 量级（几乎无损）；")
print("      int8 整张表共用一个刻度 scale（由最大值 123.456 决定），")
print("      小数（0.1、0.3333、π）被大刻度'吞掉'，失真严重；")
print("      而最大值本身恰好落在刻度上，反而精确。")
print("      → 动态范围越大的张量，int8 量化伤害越大——")
print("        这正是量化要'分组/归一化'的原因，也是量化不能当没损失用的原因。")

# ---------- 2. 显存估算表 ----------

print()
print("=" * 72)
print("二、显存估算表（模型权重部分）")
print("=" * 72)

# 参数量（十亿） × 每参数字节数 = 权重显存（GB）
models = [("7B 模型", 7e9), ("13B 模型", 13e9), ("70B 模型", 70e9)]
precisions = [("float32", 4), ("float16", 2), ("int8", 1), ("int4", 0.5)]

print(f"{'模型':>10} {'float32':>10} {'float16':>10} {'int8':>10} {'int4':>10}  备注")
print("-" * 72)
for name, n in models:
    row = []
    for _, b in precisions:
        row.append(f"{n * b / 1e9:>9.1f}GB")
    print(f"{name:>10} {'  '.join(row)}   int8 省 75%")

print("-" * 72)
print("备注：")
print("  · 这是'权重'本身的显存；推理时还要加激活值、中间缓存、KV Cache，")
print("    工程估算通常再乘 1.2~1.5。")
print("  · 一块企业级 GPU（如 A100 80GB）装 float16 的 13B 模型没问题，")
print("    装 float16 的 70B 模型就要 2 块卡或先量化到 int8。")
print()
print("结论：量化 = 用精度换资源。省不省、亏不亏，")
print("      先看这张表，再看你的任务吃不吃得下精度损失。")
