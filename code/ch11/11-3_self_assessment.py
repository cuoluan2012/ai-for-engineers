#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
代码 11-3：能力自评打分器 —— 对照全书，定位你现在在哪
第 11 章 11.7（从学到做：企业试点与个人成长）

零依赖，仅用标准库。全书按 L0~L5 六层组织（对应第 1~11 章）：
  L0 认知与动机（第 1 章）
  L1 通识与编程（第 2、3 章）
  L2 机器学习 / 深度学习（第 4、5 章）
  L3 应用工程化（第 6、7、8、9 章）
  L4 工业数据与落地（第 10 章）
  L5 成长生态（第 11 章）
每一层有若干能力项，逐项自评 0~5 分（0=没接触，5=能独立完成）。
输出：
  分层平均分、总分、短板层、"下一步建议"（对照章节回炉或进入下一层）

用法：
  python3 11-3_self_assessment.py               # 跑内置演示（老张的自评）
  python3 11-3_self_assessment.py --interactive  # 逐项打分，算自己的自评
"""

import argparse

# L0~L5 六层能力清单：层名、对应章节、能力项（逐项 0~5 分）
LEVELS = [
    ("L0 认知与动机", "第 1 章",
     [("AI 能做什么", "能说清 AI 的典型能力与边界，判断哪些场景适合 AI"),
      ("行业机会判断", "能结合自己行业列出 3 个 AI 应用机会")]),
    ("L1 通识与编程", "第 2、3 章",
     [("计算机通识", "懂命令行、软硬件、前端后端、数据库、部署等基本概念"),
      ("Python 基础", "能写脚本处理数据、调用函数、读写文件"),
      ("数据分析工具", "会用 DataFrame 做清洗、统计、可视化")]),
    ("L2 机器学习 / 深度学习", "第 4、5 章",
     [("机器学习概念", "理解监督/无监督、训练/评估、过拟合等核心概念"),
      ("模型实战", "能完成一个分类或回归小项目并评估指标"),
      ("深度学习基础", "理解神经网络/CNN 的机制，能跑通图像分类示例")]),
    ("L3 应用工程化", "第 6、7、8、9 章",
     [("大模型与提示词", "能用提示词完成文档处理/标准解读类任务"),
      ("RAG 知识库", "能把企业文档变成可问答的知识库"),
      ("智能体搭建", "能让智能体调工具、执行多步任务"),
      ("微调与部署", "能微调小模型并私有化部署成服务")]),
    ("L4 工业数据与落地", "第 10 章",
     [("数据工程", "能清洗真实数据、识别缺失/异常/口径问题"),
      ("场景评估", "能用收益×难度×风险给场景打分排序"),
      ("合规意识", "知道数据分类分级与出域红线，会过五步检查"),
      ("试点方法论", "能定验收标准、设止损线、规划 POC→产线")]),
    ("L5 成长生态", "第 11 章",
     [("作品集", "能把项目整理成'问题→方案→数字结果'的公开作品集"),
      ("开源参与", "能提 Issue、修文档或开源自己的小项目"),
      ("路径规划", "能说清产品经理/解决方案工程师/行业专家三条路径"),
      ("持续学习", "有信息源清单与'学做教'循环的实践")]),
]

# 分数 → 状态描述
def score_label(score: float) -> str:
    if score >= 4.5:
        return "熟练（可独立带项目）"
    if score >= 3.5:
        return "上手（能独立完成常见任务）"
    if score >= 2.5:
        return "会一点（能跟着示例做）"
    if score >= 1.5:
        return "接触过（知道概念，没实践）"
    return "空白（还没接触）"


def evaluate(scores_by_level: dict) -> dict:
    """输入 {层名: [各项分数]}，返回分层平均分、短板层与建议。"""
    level_avg = {name: sum(s) / len(s) for name, s in scores_by_level.items()}
    weakest = min(level_avg, key=level_avg.get)
    advice = []
    # 短板层 → 回炉对应章节
    ch_map = {name: ch for name, ch, _ in LEVELS}
    if level_avg[weakest] < 2.5:
        advice.append(f"当前短板在【{weakest}】（{ch_map[weakest]}）：先回炉对应章节，"
                      f"把这一层补到 3 分以上再往前走。")
    # 若 L1/L2 都过关而 L4/L5 偏低 → 补落地与展示
    if level_avg["L1 通识与编程"] >= 3.5 and level_avg["L2 机器学习 / 深度学习"] >= 3.5:
        if level_avg["L4 工业数据与落地"] < 3.5:
            advice.append("技术层已过关，下一步建议：用第 10 章的方法给自己企业"
                          "选一个真实场景，把数据工程与试点方法论做一遍。")
        if level_avg["L5 成长生态"] < 3.5:
            advice.append("落地能力已具备，下一步建议：按第 11 章把项目整理成作品集，"
                          "并迈出开源第一步（提一个 Issue 或修一处文档）。")
    if not advice:
        advice.append("各层都比较均衡：把短板层再补一轮，然后用'学做教'循环持续迭代。")
    return {"level_avg": level_avg, "weakest": weakest, "advice": advice}


def print_report(scores_by_level: dict) -> None:
    result = evaluate(scores_by_level)
    line = "-" * 58
    print(line)
    print("能力自评报告（对照《从工程师到 AI 工程师》全书 L0~L5）")
    print(line)
    total, count = 0.0, 0
    for name, ch, items in LEVELS:
        avg = result["level_avg"][name]
        total += avg * len(items)
        count += len(items)
        print(f"  {name}（{ch}）平均 {avg:.1f} —— {score_label(avg)}")
        for label, desc in items:
            print(f"    · {label}：{desc}（自评 {scores_by_level[name][items.index((label, desc))]:.1f} 分）")
    print(line)
    print(f"  综合均分：{total / count:.1f}；当前短板层：【{result['weakest']}】")
    for tip in result["advice"]:
        print(f"  建议：{tip}")
    print(line)


def demo() -> None:
    """内置演示：老张的自评（L0~L5 一路学上来，L4/L5 略薄）。"""
    scores = {
        "L0 认知与动机": [4.5, 4.0],
        "L1 通识与编程": [4.0, 4.0, 3.5],
        "L2 机器学习 / 深度学习": [4.0, 3.5, 3.5],
        "L3 应用工程化": [4.0, 4.0, 3.5, 3.0],
        "L4 工业数据与落地": [3.5, 3.5, 3.0, 3.0],
        "L5 成长生态": [2.5, 2.0, 2.5, 3.0],
    }
    print_report(scores)


def interactive() -> None:
    """交互模式：逐层逐项自评 0~5 分。"""
    scores_by_level = {}
    print("=== 交互模式：逐项输入 0~5 分（0=没接触，5=能独立完成）===")
    for name, ch, items in LEVELS:
        scores = []
        for label, desc in items:
            while True:
                try:
                    val = float(input(f"  {name} · {label}（{desc}）[0~5]：").strip())
                    if 0 <= val <= 5:
                        scores.append(val)
                        break
                    print("    请输入 0~5 之间的数字")
                except ValueError:
                    print("    请输入数字（如 3、3.5）")
        scores_by_level[name] = scores
    print_report(scores_by_level)


def main() -> None:
    parser = argparse.ArgumentParser(description="能力自评打分器：对照全书 L0~L5 定位自己")
    parser.add_argument("--interactive", action="store_true",
                        help="逐项打分算自己的自评（默认跑演示案例）")
    args = parser.parse_args()
    if args.interactive:
        interactive()
    else:
        demo()


if __name__ == "__main__":
    main()
