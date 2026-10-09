"""
10-1 工业数据清洗最小演示：缺失、重复、异常值
================================================

配套《从工程师到 AI 工程师》第 10 章 10.1 节。

问题背景
--------
老张想给厂里做 AI 项目，第一步不是选模型，而是看清数据。
他从设备日志导出一份"运行记录"（CSV），发现里面什么都有：
缺温度、重复行、还有离谱的振动值。数据这么脏，模型再强也没用。

本演示做三件事（真实运行，零第三方依赖，纯标准库）：
  1. 读 CSV，看数据长什么样、有多脏；
  2. 三种清洗动作：缺失值处理（删除/填充）、重复行删除、异常值识别（3σ 法则）；
  3. 清洗前后对比，得出结论：数据干净了多少、哪些"异常"要人工再看一眼。

运行方式：离线真实运行，零第三方依赖。
"""

import csv
import math
import io
from statistics import mean, stdev

# ---------- 1. 一份"脏"的演示数据（模拟设备运行记录 CSV） ----------

RAW_CSV = """时间戳,温度℃,振动mm/s,电流A,状态
2026-09-01 08:00,45.2,1.1,12.4,运行
2026-09-01 08:05,45.8,1.2,12.6,运行
2026-09-01 08:10,,1.3,12.5,运行
2026-09-01 08:15,46.1,1.1,12.4,运行
2026-09-01 08:20,45.9,1.2,12.5,运行
2026-09-01 08:20,45.9,1.2,12.5,运行
2026-09-01 08:30,46.4,1.4,12.8,运行
2026-09-01 08:35,47.2,1.2,12.7,运行
2026-09-01 08:40,46.8,1.3,12.6,运行
2026-09-01 08:45,46.5,1.2,12.6,运行
2026-09-01 08:50,47.0,88.5,12.9,运行
2026-09-01 08:55,46.9,1.5,12.8,运行
2026-09-01 09:00,47.3,1.4,12.7,运行
2026-09-01 09:05,,1.3,12.6,运行
2026-09-01 09:10,47.8,1.5,12.9,运行
2026-09-01 09:15,48.0,1.6,13.1,运行
2026-09-01 09:20,48.3,1.5,13.0,运行
2026-09-01 09:25,48.5,1.6,13.2,运行
2026-09-01 09:30,48.2,1.5,13.1,运行
2026-09-01 09:35,48.8,1.7,13.3,运行
2026-09-01 09:40,48.6,1.6,13.2,运行
2026-09-01 09:45,49.0,1.7,13.4,运行
2026-09-01 09:50,49.2,1.8,13.5,运行
2026-09-01 09:55,49.5,1.7,13.4,运行
2026-09-01 10:00,49.8,1.8,13.6,运行
2026-09-01 10:05,50.1,1.9,13.8,运行
2026-09-01 10:10,50.4,1.8,13.7,运行
2026-09-01 10:15,50.8,2.0,14.0,运行
2026-09-01 10:20,51.0,1.9,14.1,运行
2026-09-01 10:25,51.3,2.1,14.3,运行
2026-09-01 10:30,51.5,2.0,14.2,运行
2026-09-01 10:35,52.0,2.2,14.5,运行
2026-09-01 10:40,52.3,2.1,14.4,运行
2026-09-01 10:45,52.6,2.3,14.6,运行
2026-09-01 10:50,52.9,2.2,14.5,运行
2026-09-01 10:55,53.2,2.4,14.8,运行
2026-09-01 11:00,53.5,2.3,14.7,运行
"""


def load_rows(text):
    """CSV 文本 → 行列表（每行 dict）。"""
    return list(csv.DictReader(io.StringIO(text)))


def col_values(rows, col):
    """取出某列全部值，None 表示缺失。"""
    return [None if (r[col] == "" or r[col].strip() == "") else float(r[col])
            for r in rows]


def fill_missing(rows, col):
    """缺失值填充：用该列均值填充，返回均值。"""
    vals = [v for v in col_values(rows, col) if v is not None]
    avg = mean(vals)
    for r in rows:
        if r[col] == "" or r[col].strip() == "":
            r[col] = f"{avg:.2f}"
    return avg


def remove_duplicates(rows):
    """删除完全重复的行，返回删除数。"""
    seen, keep, dup = set(), [], 0
    for r in rows:
        key = tuple(r.values())
        if key in seen:
            dup += 1
        else:
            seen.add(key)
            keep.append(r)
    return keep, dup


def flag_outliers(rows, col, k=3):
    """3σ 法则标异常：|x - μ| > kσ。返回 (标注行数, 上下界)。"""
    vals = [v for v in col_values(rows, col) if v is not None]
    mu, sigma = mean(vals), stdev(vals)
    lo, hi = mu - k * sigma, mu + k * sigma
    flagged = 0
    for r in rows:
        v = col_values([r], col)[0]
        if v is not None and (v < lo or v > hi):
            flagged += 1
    return flagged, (lo, hi)


# ---------- 2. 清洗流程 ----------

print("=" * 70)
print("一、原始数据：先看有多脏")
print("=" * 70)
rows = load_rows(RAW_CSV)
print(f"    共 {len(rows)} 行，字段：时间戳 / 温度 / 振动 / 电流 / 状态")

missing_temp = sum(1 for v in col_values(rows, "温度℃") if v is None)
missing_vib = sum(1 for v in col_values(rows, "振动mm/s") if v is None)
print(f"    缺失：温度 {missing_temp} 处、振动 {missing_vib} 处")
_, dup0 = remove_duplicates([dict(r) for r in rows])
print(f"    重复：{dup0} 行（08:20 那条被系统重复写入了两遍）")
flag0, _ = flag_outliers(rows, "振动mm/s")
print(f"    异常候选：振动列 3σ 检出 {flag0} 处（08:50 那条 88.5 明显是传感器毛刺）")

print()
print("=" * 70)
print("二、清洗动作")
print("=" * 70)

# 动作 1：缺失值填充（温度列均值填充）
avg_temp = fill_missing(rows, "温度℃")
print(f"    ① 缺失值：温度列均值填充为 {avg_temp:.1f}℃（共填 {missing_temp} 处）")

# 动作 2：删除重复
rows, dup = remove_duplicates(rows)
print(f"    ② 重复行：删除 {dup} 行（保留首次出现）")

# 动作 3：异常值识别（标出，交人工复核，不自动删）
flag1, (lo, hi) = flag_outliers(rows, "振动mm/s")
print(f"    ③ 异常值：振动列 3σ 边界 [{lo:.1f}, {hi:.1f}]，标出 {flag1} 处")
print("       → 工程做法：异常值先标出来人工复核，不急着删")
print("          （88.5 可能是传感器毛刺，也可能是真故障前兆）")

print()
print("=" * 70)
print("三、清洗前后对比")
print("=" * 70)
print(f"    行数：{len(load_rows(RAW_CSV))} → {len(rows)}（去重 {dup} 行）")
print(f"    缺失：{missing_temp + missing_vib} 处 → 0 处（填充）")
print(f"    异常：{flag0} 处 → 已标注待人工复核（未自动删除）")
print()
print("结论：")
print("  · 数据清洗 = 缺失/重复/异常三道关，每道关都有标准动作；")
print("  · '异常值'不要自动删——标注出来交人工复核，")
print("    它可能是脏数据，也可能是设备要出事的信号；")
print("  · 数据质量决定模型上限：脏数据进去，再好的模型也出不来。")
