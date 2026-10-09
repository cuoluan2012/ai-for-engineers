#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
代码 11-1：ROI 计算器 —— 说服企业前，先把账算清楚
第 11 章 11.1（从学到做：企业试点与个人成长）

零依赖，仅用标准库。演示"老张的视觉质检试点"的完整算账过程：
  收益三笔账：省人力、提效率、降损失（每年）
  成本四块：  数据、开发、部署（首年一次性）+ 维护（每年）
输出：
  年化总收益、首年投入、年化净收益、ROI、回本周期（月）

用法：
  python3 11-1_roi_calculator.py                 # 跑内置演示案例
  python3 11-1_roi_calculator.py --auto 0        # 交互模式（自己填数字）
"""

import argparse

# 收益三笔账（每年，单位：万元）—— 每一项都要写明"这笔钱怎么来的"
BENEFIT_LABELS = [
    ("省人力", "省下的人工成本：人数 × 年薪 × 节省比例"),
    ("提效率", "效率提升带来的产值/收益增量"),
    ("降损失", "次品率/停机/索赔损失的降低"),
]

# 成本四块（单位：万元）—— 前三年是首年一次性投入，维护是每年发生
COST_LABELS = [
    ("数据", "数据采集、清洗、标注（首年一次性）"),
    ("开发", "模型训练、评估、调试（首年一次性）"),
    ("部署", "硬件、服务器、产线集成（首年一次性）"),
    ("维护", "模型监控、定期重训、人工值守（每年）"),
]


def run_case(benefits: dict, costs: dict) -> dict:
    """按三笔收益账 + 四块成本，算 ROI 与回本周期。"""
    yearly_benefit = sum(benefits.values())          # 年化总收益
    first_year_cost = costs["数据"] + costs["开发"] + costs["部署"]  # 首年一次性投入
    yearly_maintain = costs["维护"]                   # 每年维护成本
    net_yearly = yearly_benefit - yearly_maintain     # 年化净收益
    if first_year_cost <= 0 or net_yearly <= 0:
        raise ValueError("投入或净收益必须为正，才能计算 ROI / 回本周期")
    roi = net_yearly / first_year_cost               # 首年 ROI（口径：净收益/首年投入）
    payback_months = first_year_cost / net_yearly * 12  # 回本周期（月）
    return {
        "yearly_benefit": yearly_benefit,
        "first_year_cost": first_year_cost,
        "yearly_maintain": yearly_maintain,
        "net_yearly": net_yearly,
        "roi": roi,
        "payback_months": payback_months,
    }


def print_report(title: str, benefits: dict, costs: dict, result: dict) -> None:
    """把账目与结果打印成一张清晰的报表。"""
    line = "-" * 58
    print(line)
    print(f"项目：{title}")
    print(line)
    print("一、收益三笔账（每年，万元）")
    for key, desc in BENEFIT_LABELS:
        print(f"  {key}（{desc.split('：')[0]}）：{benefits[key]:.1f}")
    print(f"  → 年化总收益：{result['yearly_benefit']:.1f} 万元")
    print(line)
    print("二、成本四块（万元）")
    for key, desc in COST_LABELS:
        print(f"  {key}（{'首年一次性' if key != '维护' else '每年'}）：{costs[key]:.1f}")
    print(f"  → 首年一次性投入：{result['first_year_cost']:.1f} 万元")
    print(f"  → 每年维护成本：{result['yearly_maintain']:.1f} 万元")
    print(line)
    print("三、结论")
    print(f"  年化净收益 = 年化总收益 - 维护成本 = {result['net_yearly']:.1f} 万元")
    print(f"  首年 ROI = 年化净收益 / 首年投入 = {result['roi'] * 100:.1f}%")
    print(f"  回本周期 = 首年投入 / 年化净收益 × 12 ≈ {result['payback_months']:.1f} 个月")
    print(line)
    print("说明：ROI 只是立项的第一关，还要配合 11.2 的止损线与验收标准。")


def demo() -> None:
    """内置演示：老张的视觉质检试点。"""
    benefits = {"省人力": 16.0, "提效率": 5.0, "降损失": 10.0}  # 每年 31 万
    costs = {"数据": 3.0, "开发": 8.0, "部署": 4.0, "维护": 3.0}  # 首年 15 万 + 维护 3 万/年
    result = run_case(benefits, costs)
    print_report("视觉质检试点（演示案例：数字为虚构）", benefits, costs, result)


def interactive() -> None:
    """交互模式：自己填数字，算自己场景的账。"""
    benefits, costs = {}, {}
    print("=== 交互模式：请依次输入数字（万元，可带小数）===")
    for key, desc in BENEFIT_LABELS:
        while True:
            try:
                benefits[key] = float(input(f"  收益 · {key}（{desc.split('：')[1]}）：").strip() or "0")
                break
            except ValueError:
                print("    输入无效，请输入数字（如 5.5）")
    for key, desc in COST_LABELS:
        while True:
            try:
                costs[key] = float(input(f"  成本 · {key}（{desc.split('：')[1]}）：").strip() or "0")
                break
            except ValueError:
                print("    输入无效，请输入数字（如 5.5）")
    result = run_case(benefits, costs)
    print_report("我的试点项目", benefits, costs, result)


def main() -> None:
    parser = argparse.ArgumentParser(description="ROI 计算器：说服企业前先把账算清楚")
    parser.add_argument("--auto", type=int, default=1,
                        help="1=跑演示案例（默认）；0=交互模式自己填数字")
    args = parser.parse_args()
    if args.auto == 1:
        demo()
    else:
        interactive()


if __name__ == "__main__":
    main()
