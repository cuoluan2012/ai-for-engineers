# -*- coding: utf-8 -*-
"""
08-2_agent_loop.py
第 8 章《AI 智能体》代码 8-2：手写 Agent 循环（ReAct 简化版，零依赖）

对应正文 8.5「Agent 循环的真面目」。

智能体的循环不是魔法，就是一个 while 循环：
  思考（Reasoning）→ 行动（Action，调用工具）→ 观察（Observation）→ 再思考……
直到任务完成，或达到最大轮数。

真实环境中，"思考"由大模型完成（决定下一步做什么）；
本代码用一个「决策函数」模拟模型的思考，规则写死、可复现，
方便你观察循环每一轮的输入输出。

任务：为「45 钢轴，直径 φ50，车削外圆」填一张工艺卡片。
步骤：查手册（切削速度）→ 算转速 → 填卡片。
"""
import math

MAX_STEPS = 6  # 循环上限：防止智能体"自己乱来"


# ─────────────────────── 工具（给智能体的"专用设备"） ───────────────────────
def search_manual(keyword: str) -> str:
    """工具 1：查工艺手册（内置小手册，模拟真实手册检索）。"""
    manual = {
        "45钢": "45 钢车削外圆推荐切削速度 80~120 m/min，进给量 0.2~0.4 mm/r",
        "轴承钢": "GCr15 轴承钢车削推荐切削速度 60~90 m/min，进给量 0.1~0.3 mm/r",
    }
    for k, v in manual.items():
        if k in keyword or keyword in k:
            return v
    return f"手册里没查到「{keyword}」，请换关键词"


def calc_spindle_speed(diameter_mm: float, cutting_speed: float) -> str:
    """工具 2：转速公式 n = 1000 × v / (π × d)。"""
    n = 1000.0 * cutting_speed / (math.pi * diameter_mm)
    return f"{round(n)} r/min（按切削速度 {cutting_speed} m/min、直径 {diameter_mm} mm 计算）"


def fill_card(fields: dict) -> str:
    """工具 3：把收集到的信息填进工艺卡片模板。"""
    return (
        "工艺卡片\n"
        f"  零件：{fields.get('part', '未填')}\n"
        f"  材料：{fields.get('material', '未填')}\n"
        f"  工序：{fields.get('process', '未填')}\n"
        f"  切削速度：{fields.get('cutting_speed', '未填')}\n"
        f"  主轴转速：{fields.get('spindle_speed', '未填')}"
    )


# ─────────────────────── 模拟模型的"思考"：决定下一步动作 ───────────────────────
def decide_next_step(state: dict):
    """根据当前已经收集到的信息，决定下一步行动。

    这是教学用的简化决策规则；真实环境中由大模型完成这一步，
    它会阅读工具描述、结合任务目标给出行动。
    """
    if state.get("cutting_speed") is None:
        return ("search_manual", {"keyword": state["material"]})
    if state.get("spindle_speed") is None:
        return ("calc_spindle_speed", {"diameter_mm": state["diameter_mm"],
                                       "cutting_speed": state["cutting_speed"]})
    if state.get("card") is None:
        return ("fill_card", {"fields": state})
    return None  # 所有信息齐了，任务完成


TOOL_IMPLS = {
    "search_manual": lambda **kw: search_manual(**kw),
    "calc_spindle_speed": lambda **kw: calc_spindle_speed(**kw),
    "fill_card": lambda **kw: fill_card(**kw),
}


# ─────────────────────── Agent 循环本体 ───────────────────────
def run_agent(task: str, state: dict):
    print(f"任务：{task}")
    print(f"初始状态：{state}")
    print("=" * 60)

    step = 0
    while step < MAX_STEPS:
        step += 1
        print(f"── 第 {step} 轮 ──")

        # 思考：决定下一步
        decision = decide_next_step(state)
        if decision is None:
            print("思考：所有信息已齐，任务完成，不再行动。")
            break
        action, arguments = decision
        print(f"思考：还需要「{action}」，参数 {arguments}")

        # 行动：执行工具
        print(f"行动：调用工具「{action}」……")
        result = TOOL_IMPLS[action](**arguments)
        print(f"观察：工具返回「{result}」")

        # 把观察结果写进记忆（状态），供下一轮思考使用
        if action == "search_manual":
            state["cutting_speed"] = 100.0  # 手册推荐区间取中值（正文会解释简化）
            state["manual_note"] = result
        elif action == "calc_spindle_speed":
            state["spindle_speed"] = result
        elif action == "fill_card":
            state["card"] = result
        print()

    print("=" * 60)
    if state.get("card") is None:
        print(f"警告：达到 {MAX_STEPS} 轮上限仍未完成——这就是日志里要盯的「循环失控」。")
    else:
        print("任务完成，最终产物：")
        print(state["card"])


if __name__ == "__main__":
    task = "为 45 钢轴（直径 φ50）车削外圆填写工艺卡片"
    initial_state = {
        "part": "传动轴",
        "material": "45钢",
        "diameter_mm": 50,
        "process": "车削外圆",
        "cutting_speed": None,
        "spindle_speed": None,
        "card": None,
    }
    run_agent(task, initial_state)
