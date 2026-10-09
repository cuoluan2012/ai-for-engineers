#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
代码 11-2：第一个试点项目的启动检查清单
第 11 章 11.2（从学到做：企业试点与个人成长）

零依赖，仅用标准库。演示"老张的视觉质检试点"立项前的十项检查：
  范围 → 数据 → 验收 → 止损 → 支持 → 合规 → 部署 → 运维 → 退路 → 复盘
输出：
  逐项就绪状态、就绪率、未就绪项清单（每一项都附"怎么做才就绪"的提示）

用法：
  python3 11-2_project_checklist.py              # 跑内置演示（老张案例，含 2 项未就绪）
  python3 11-2_project_checklist.py --interactive  # 逐项回答 y/n，算自己项目的就绪率
"""

import argparse

# 十项检查：每项 = (标题, 检查问题, 就绪提示)
CHECKLIST = [
    ("范围", "是否只选了一个场景、一条线、一个环节，而不是'全厂上 AI'？",
     "把目标切小：先做成一个闭环（第 10 章 10.2 的'先小场景出闭环'）"),
    ("数据", "是否已经看过真实数据：数据源、格式、量级、质量都确认了？",
     "先看数据再定目标：数据质量决定模型上限（第 10 章 10.1）"),
    ("验收", "验收标准是否写成了数字（准确率/省人力/节拍/停机时长）？",
     "'效果还行'不算验收，写成可测量的数字才有止损依据（11.2.2）"),
    ("止损", "是否设了止损线：时间、预算、最低效果三条线？",
     "不过线就停，停不是失败是止损（11.2.3，对应术语 Stop-loss Line）"),
    ("支持", "业务（痛点）、IT（资源）、高层（拍板）三类人都找到了？",
     "先找业务部门确认痛点，再拉 IT 谈资源，最后用 ROI 说服高层（11.1.4）"),
    ("合规", "是否按'分类分级→脱敏→权限→留痕→评估'五步过了一遍红线？",
     "数据能不能进模型、能不能出域，先过红线清单（第 10 章 10.7）"),
    ("部署", "是否确认了部署条件：硬件、网络、能否私有化？",
     "生产环境不是笔记本：GPU/服务器/内网隔离先谈好（第 9 章 9.6）"),
    ("运维", "是否安排了上线后的运维：谁监控、多久重训一次？",
     "模型会'旧'：数据变了它就不准，运维与定期重训要提前排班（第 9 章 9.6.4）"),
    ("退路", "是否保留了退路：试点失败时能退回原流程？",
     "模型不行就退回人工/原系统，别让试点成为唯一选项（第 10 章 10.8）"),
    ("复盘", "是否计划了复盘：无论成败都留下'数据+代码+复盘三件事'？",
     "复盘产物直接喂给作品集（11.3）：问题→方案→数字结果"),
]


def evaluate(answers: list) -> dict:
    """根据逐项回答（True=就绪），返回就绪率与未就绪项。"""
    not_ready = [CHECKLIST[i] for i, ok in enumerate(answers) if not ok]
    ready_rate = sum(answers) / len(answers) * 100
    return {"not_ready": not_ready, "ready_rate": ready_rate}


def print_report(title: str, answers: list) -> None:
    line = "-" * 58
    print(line)
    print(f"项目：{title} —— 启动检查报告")
    print(line)
    for i, (name, question, _) in enumerate(CHECKLIST, start=1):
        mark = "√ 就绪" if answers[i - 1] else "× 未就绪"
        print(f"  {i:>2}. [{mark}] {name}：{question}")
    result = evaluate(answers)
    print(line)
    print(f"  就绪率：{result['ready_rate']:.0f}%（{sum(answers)}/{len(answers)} 项）")
    if result["not_ready"]:
        print("  未就绪项与补齐动作：")
        for name, _, tip in result["not_ready"]:
            print(f"    - {name}：{tip}")
    else:
        print("  全部就绪：可以进入试点（但别忘了 11.2 的止损线随时生效）")
    print(line)


def demo() -> None:
    """内置演示：老张的视觉质检试点 —— 8 项就绪、2 项未就绪。"""
    answers = [
        True,   # 范围：只选了质检线一条线
        True,   # 数据：看过三个月检验记录
        True,   # 验收：漏检率、误报率、节省人力都写成数字
        False,  # 止损：还没定时间和预算上限 ← 未就绪
        True,   # 支持：质检科长（痛点）、IT 主任（资源）、副厂长（拍板）
        True,   # 合规：检验数据不涉及个人数据，五步已过
        False,  # 部署：产线工控机算力不足，GPU 还没申请 ← 未就绪
        True,   # 运维：计划每季度重训一次
        True,   # 退路：试点期保留人工复检
        True,   # 复盘：试点结束写复盘报告
    ]
    print_report("视觉质检试点（演示案例）", answers)


def interactive() -> None:
    """交互模式：逐项回答 y/n，算自己项目的就绪率。"""
    answers = []
    print("=== 交互模式：逐项回答 y（就绪）或 n（未就绪）===")
    for name, question, tip in CHECKLIST:
        while True:
            ans = input(f"  {name}：{question} [y/n] ").strip().lower()
            if ans in ("y", "n"):
                answers.append(ans == "y")
                break
            print("    请输入 y 或 n")
    print_report("我的试点项目", answers)


def main() -> None:
    parser = argparse.ArgumentParser(description="第一个试点项目的启动检查清单")
    parser.add_argument("--interactive", action="store_true",
                        help="逐项回答 y/n，算自己项目的就绪率（默认跑演示案例）")
    args = parser.parse_args()
    if args.interactive:
        interactive()
    else:
        demo()


if __name__ == "__main__":
    main()
