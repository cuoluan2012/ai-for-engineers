# -*- coding: utf-8 -*-
"""
08-3_multi_agent.py
第 8 章《AI 智能体》代码 8-3：多智能体协作简化示例（零依赖）

对应正文 8.6「多智能体协作：班组协作」。

三个角色，对照车间里的班组：
- 工艺智能体（process_agent）：出工艺方案（干活的人）；
- 质检智能体（qa_agent）：挑毛病（把关的人）；
- 协调者（coordinator）：派活、汇总、仲裁（工艺组长）。

协作方式是"消息传递"：一个智能体的输出，成为另一个智能体的输入。
消息就是普通字典：from / to / type / content。

流程：协调者派任务 → 工艺出草稿 → 质检审查 → 有问题退回工艺改 →
再审查 → 通过后协调者出最终版。为防止无限互踢皮球，设定最多退改 2 次，
超过后协调者"升级给人"（现实中是转人工）。
"""
import json

MAX_REVISIONS = 2  # 最多退回修改次数，超过即升级给人


# ─────────────────────── 角色实现：每个智能体是一个函数 ───────────────────────
def process_agent(message: dict) -> dict:
    """工艺智能体：接收任务，出一份工艺卡片草稿。"""
    part = message["content"]["part"]
    material = message["content"]["material"]
    # 简单规则：45 钢推荐切削速度 100 m/min；转速 = 1000×v/(π×d)
    cutting_speed = 100.0
    diameter = message["content"]["diameter_mm"]
    spindle_speed = round(1000.0 * cutting_speed / (3.14159 * diameter))
    draft = {
        "part": part,
        "material": material,
        "diameter_mm": diameter,
        "cutting_speed": cutting_speed,
        "spindle_speed": spindle_speed,
        "spindle_limit": 3000,  # 机床主轴转速上限（来自设备台账）
    }
    return {"from": "工艺智能体", "to": "质检智能体", "type": "draft", "content": draft}


def qa_agent(message: dict) -> dict:
    """质检智能体：审查草稿，返回问题列表（空列表 = 通过）。"""
    c = message["content"]
    problems = []
    if c["spindle_speed"] > c["spindle_limit"]:
        problems.append(f"转速 {c['spindle_speed']} r/min 超过主轴上限 {c['spindle_limit']} r/min")
    if c["diameter_mm"] > 200:
        problems.append("直径大于 200 mm，建议分粗车、精车两道工序")
    return {"from": "质检智能体", "to": "协调者", "type": "review",
            "content": {"problems": problems}}


def fix_draft(message: dict) -> dict:
    """工艺智能体收到质检意见后修改草稿：降速到上限以内。"""
    c = dict(message["content"])
    c["spindle_speed"] = min(c["spindle_speed"], c["spindle_limit"])
    c["revised"] = True
    return {"from": "工艺智能体", "to": "质检智能体", "type": "draft", "content": c}


# ─────────────────────── 协调者：派活、汇总、仲裁 ───────────────────────
def coordinator(task: dict):
    print(f"协调者：收到任务「{task['part']}」，派给工艺智能体。")
    messages = []  # 全程消息日志

    # 1) 派任务
    msg = {"from": "协调者", "to": "工艺智能体", "type": "task", "content": task}
    messages.append(msg)

    reply = process_agent(msg)
    messages.append(reply)
    print(f"工艺智能体 → 质检智能体：草稿 转速={reply['content']['spindle_speed']} r/min")

    revision = 0
    while True:
        # 质检智能体把关
        review = qa_agent(reply)
        messages.append(review)
        problems = review["content"]["problems"]
        if not problems:
            print("质检智能体 → 协调者：审查通过，无问题。")
            break

        print(f"质检智能体 → 协调者：发现 {len(problems)} 个问题：{problems[0]}")
        revision += 1
        if revision > MAX_REVISIONS:
            print(f"协调者：已退改 {MAX_REVISIONS} 次仍未通过，升级给人处理（人工确认）。")
            messages.append({"from": "协调者", "to": "人工", "type": "escalate",
                             "content": {"draft": reply["content"], "problems": problems}})
            return messages

        # 退回工艺智能体修改：直接修正草稿，再送质检（不再从头重算）
        reply = fix_draft(reply)
        messages.append(reply)
        print(f"协调者 → 工艺智能体：请修改（第 {revision} 次退改）。")

    # 通过：协调者汇总出最终版
    final = {"from": "协调者", "to": "车间", "type": "final",
             "content": reply["content"]}
    messages.append(final)
    print(f"协调者 → 车间：最终版 转速={final['content']['spindle_speed']} r/min，下发。")
    return messages


if __name__ == "__main__":
    print("场景一：正常任务（一次通过）")
    print("-" * 60)
    coordinator({"part": "法兰", "material": "45钢", "diameter_mm": 100})
    print()
    print("场景二：转速超限（质检退回，修改后通过）")
    print("-" * 60)
    coordinator({"part": "细轴", "material": "45钢", "diameter_mm": 10})
    print()
    print("场景三：多次不通过（质检与工艺无法达成一致，升级给人）")
    print("-" * 60)
    coordinator({"part": "大法兰", "material": "45钢", "diameter_mm": 300})
