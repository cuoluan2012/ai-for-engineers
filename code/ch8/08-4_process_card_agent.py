# -*- coding: utf-8 -*-
"""
08-4_process_card_agent.py
第 8 章《AI 智能体》配套项目：自动生成工艺卡片的智能体（约 190 行，零依赖）

对应正文 8.8「配套项目」。

功能：输入零件信息（名称 / 材料 / 直径 / 工序），智能体自动完成
  查手册 → 算转速 → 自检 → 填卡片 → 生成确认清单，
人工确认后才算完成——关键动作必须人点头（Human-in-the-loop）。

设计要点：
- 工具集 = 给智能体的"专用设备"：手册检索 / 转速计算 / 转速校验 / 卡片填充；
- Agent 循环：每轮"思考 → 行动 → 观察"，直到卡片填好或达到轮数上限；
- 生成环节沿用第 6 章模式：默认 mock（展示提示词结构与工具轨迹），
  配 API Key 后可在 `generate_text` 处接入真实大模型；
- 效果报告：10 张零件卡片的人工确认通过率 + 工具调用轨迹。

运行：python3 08-4_process_card_agent.py
"""
import math

MAX_STEPS = 8  # 循环上限

# ─────────────────────── 工艺手册（内置小手册） ───────────────────────
MANUAL = {
    "45钢": {"cutting_speed": (80, 120), "feed": "0.2~0.4 mm/r",
             "tool": "硬质合金车刀 YT15"},
    "铝合金": {"cutting_speed": (150, 250), "feed": "0.1~0.3 mm/r",
              "tool": "硬质合金车刀 YG6"},
    "不锈钢": {"cutting_speed": (50, 80), "feed": "0.1~0.2 mm/r",
              "tool": "涂层硬质合金车刀"},
}
MACHINE_LIMIT = 3000  # 机床主轴转速上限（来自设备台账）


# ─────────────────────── 工具（智能体的"专用设备"） ───────────────────────
def query_manual(material: str) -> dict:
    """工具 1：查手册，返回该材料的切削参数建议。"""
    row = MANUAL.get(material)
    if row is None:
        return {"error": f"手册没有「{material}」，可选：{list(MANUAL.keys())}"}
    return row


def calc_spindle_speed(diameter_mm: float, cutting_speed: float) -> float:
    """工具 2：转速公式 n = 1000 × v / (π × d)，取整。"""
    return round(1000.0 * cutting_speed / (math.pi * diameter_mm))


def check_speed(spindle_speed: float, limit: float) -> list:
    """工具 3：校验转速是否超限，返回问题列表（空 = 通过）。"""
    problems = []
    if spindle_speed > limit:
        problems.append(f"转速 {spindle_speed} r/min 超过主轴上限 {limit} r/min")
    if spindle_speed < 30:
        problems.append(f"转速 {spindle_speed} r/min 过低，建议提高切削速度")
    return problems


def fill_card(part: str, material: str, process: str, diameter_mm: float,
              cutting_speed: float, spindle_speed: float, feed: str, tool: str) -> str:
    """工具 4：把参数填进工艺卡片模板（Markdown）。"""
    return (
        f"## 工艺卡片：{part}\n\n"
        f"| 项目 | 内容 |\n|---|---|\n"
        f"| 零件 | {part} |\n"
        f"| 材料 | {material}（φ{diameter_mm} mm） |\n"
        f"| 工序 | {process} |\n"
        f"| 切削速度 | {cutting_speed} m/min |\n"
        f"| 主轴转速 | {spindle_speed} r/min |\n"
        f"| 进给量 | {feed} |\n"
        f"| 刀具 | {tool} |\n"
    )


# ─────────────────────── 模拟模型的"思考"（决策状态机） ───────────────────────
# 真实环境：这一行由大模型完成（生成"下一步动作"的 JSON）；
# 教学环境：用规则模拟同样的决策，保证可复现。
def decide(state: dict):
    if state.get("manual") is None:
        return ("query_manual", {"material": state["material"]})
    if state.get("spindle_speed") is None:
        mid = sum(state["manual"]["cutting_speed"]) / 2
        return ("calc_spindle_speed",
                {"diameter_mm": state["diameter_mm"], "cutting_speed": mid})
    if state.get("check_result") is None:
        return ("check_speed",
                {"spindle_speed": state["spindle_speed"], "limit": MACHINE_LIMIT})
    if state.get("card") is None:
        m = state["manual"]
        return ("fill_card", {"part": state["part"], "material": state["material"],
                              "process": state["process"], "diameter_mm": state["diameter_mm"],
                              "cutting_speed": state["cutting_speed"],
                              "spindle_speed": state["spindle_speed"],
                              "feed": m["feed"], "tool": m["tool"]})
    return None


TOOL_IMPLS = {
    "query_manual": query_manual, "calc_spindle_speed": calc_spindle_speed,
    "check_speed": check_speed, "fill_card": fill_card,
}


# ─────────────────────── 生成环节：mock / 真实双模式 ───────────────────────
def generate_text(prompt: str) -> str:
    """生成环节。默认 mock：展示会发给大模型的提示词结构。

    接入真实大模型：在此函数里把 prompt 发给 API（见第 6 章 06-4），
    并解析返回文本即可，其余流程不变。
    """
    return f"[mock 生成] 提示词结构：\n{prompt.strip()[:120]}……"


# ─────────────────────── 人工确认环节 ───────────────────────
def build_confirm_list(state: dict, card: str) -> list:
    """生成确认清单：关键项、影响、能否撤销——给人看，人点头才算数。"""
    return [
        {"item": "主轴转速", "value": f"{state['spindle_speed']} r/min",
         "impact": "转速超限会损伤刀具和主轴", "reversible": "是，改参数即可"},
        {"item": "切削速度", "value": f"{state['cutting_speed']} m/min",
         "impact": "影响表面粗糙度和刀具寿命", "reversible": "是"},
        {"item": "下发车间", "value": "工艺卡片投入生产",
         "impact": "一旦执行会影响实际加工", "reversible": "否，执行后只能返工"},
    ]


def confirm_by_human(confirm_list: list, card: str) -> bool:
    """人工确认：mock 模式模拟人的判断——自检发现问题的卡片拒绝，正常卡片通过。

    真实环境：清单展示给人，人点击"确认 / 拒绝"；这里的规则只是演示，
    可改成任何你想要的确认策略（例如"涉及下发车间的一律人工审批"）。
    """
    if "注意：" in card:  # 卡片带了自检发现的问题，人拒绝放行
        return False
    return True


# ─────────────────────── 单个零件的完整流程 ───────────────────────
def run_one_part(part: dict, verbose: bool = True) -> dict:
    state = {"part": part["part"], "material": part["material"],
             "diameter_mm": part["diameter_mm"], "process": part["process"],
             "manual": None, "cutting_speed": None, "spindle_speed": None,
             "check_result": None, "card": None}
    trace = []
    step = 0
    if verbose:
        print(f"任务：{part['part']}（{part['material']}，φ{part['diameter_mm']} mm，{part['process']}）")

    while step < MAX_STEPS:
        step += 1
        decision = decide(state)
        if decision is None:
            break
        action, arguments = decision
        result = TOOL_IMPLS[action](**arguments)
        trace.append({"step": step, "action": action,
                      "arguments": arguments, "result": str(result)[:60]})
        if verbose:
            print(f"  第{step}步：{action} → {str(result)[:55]}……")
        # 观察结果写入记忆
        if action == "query_manual":
            if "error" in result:
                state["card"] = "错误：" + result["error"]
                break
            state["manual"] = result
            mid = sum(result["cutting_speed"]) / 2
            state["cutting_speed"] = mid
        elif action == "calc_spindle_speed":
            state["spindle_speed"] = result
        elif action == "check_speed":
            state["check_result"] = result
        elif action == "fill_card":
            state["card"] = result

    if state["card"] is None:
        state["card"] = "任务未完成：达到轮数上限或参数不足"
    if state["check_result"]:
        state["card"] += "\n注意：" + "；".join(state["check_result"])

    # 人工确认
    confirm_list = build_confirm_list(state, state["card"])
    ok = confirm_by_human(confirm_list, state["card"])
    if verbose:
        print("  确认清单：")
        for item in confirm_list:
            print(f"    - {item['item']}：{item['value']}（影响：{item['impact']}；可撤销：{item['reversible']}）")
        print(f"  人工确认：{'通过，卡片生效' if ok else '拒绝，返回修改'}")
        print("-" * 60)
    return {"card": state["card"], "confirm_list": confirm_list,
            "ok": ok, "trace": trace}


# ─────────────────────── 效果报告：10 张卡片 ───────────────────────
def run_report(parts: list):
    print("效果报告：10 张工艺卡片的人工确认通过率")
    print("-" * 60)
    passed = 0
    total_tools = 0
    for part in parts:
        result = run_one_part(part, verbose=False)
        total_tools += len(result["trace"])
        mark = "√" if result["ok"] else "×"
        print(f"  {mark} {part['part']}（{part['material']}）："
              f"工具调用 {len(result['trace'])} 步，卡片{'已生效' if result['ok'] else '被拒'}")
        if result["ok"]:
            passed += 1
    print("-" * 60)
    print(f"确认通过率：{passed}/{len(parts)} = {passed / len(parts) * 100:.1f}%")
    print(f"平均每张卡片工具调用步数：{total_tools / len(parts):.1f}")


if __name__ == "__main__":
    print("=== 示例一：45 钢传动轴（完整轨迹） ===")
    run_one_part({"part": "传动轴", "material": "45钢", "diameter_mm": 50, "process": "车削外圆"})
    print("=== 示例二：铝合金法兰（完整轨迹） ===")
    run_one_part({"part": "法兰", "material": "铝合金", "diameter_mm": 120, "process": "车削端面"})

    parts = [
        {"part": "传动轴", "material": "45钢", "diameter_mm": 50, "process": "车削外圆"},
        {"part": "法兰", "material": "45钢", "diameter_mm": 120, "process": "车削端面"},
        {"part": "小轴", "material": "45钢", "diameter_mm": 30, "process": "车削外圆"},
        {"part": "盖板", "material": "铝合金", "diameter_mm": 150, "process": "车削端面"},
        {"part": "套筒", "material": "45钢", "diameter_mm": 80, "process": "车削内孔"},
        {"part": "支架", "material": "铝合金", "diameter_mm": 90, "process": "车削外圆"},
        {"part": "阀杆", "material": "不锈钢", "diameter_mm": 40, "process": "车削外圆"},
        {"part": "端盖", "material": "45钢", "diameter_mm": 180, "process": "车削端面"},
        {"part": "衬套", "material": "不锈钢", "diameter_mm": 60, "process": "车削内孔"},
        {"part": "微细轴", "material": "45钢", "diameter_mm": 5, "process": "车削外圆"},
    ]
    run_report(parts)
