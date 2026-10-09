# -*- coding: utf-8 -*-
"""
08-1_function_calling.py
第 8 章《AI 智能体》代码 8-1：Function Calling 协议演示（零依赖）

对应正文 8.3「智能体怎么干活：工具调用」。

Function Calling 的真实机制（先讲协议，再看代码）：
1. 你告诉模型"有哪些工具可用、每个工具干什么"（工具描述）；
2. 模型不执行代码，只返回一个"调用请求"：选哪个工具、填什么参数；
3. 你的程序执行这个工具，拿到真实结果；
4. 把结果回填给模型，模型基于结果给出最终回答。

为了在零依赖、无 API Key 的环境下把协议讲透，本代码用一个
「模拟模型」代替真实大模型：它根据问题的关键词，返回和真实
大模型一样的结构化调用请求。真实环境中，这一步由大模型的
function calling 能力完成，协议结构完全一致。

运行：python3 08-1_function_calling.py
"""
import json


# ─────────────────────────── 第一步：定义工具 ───────────────────────────
# 工具 = 给 AI 的"专用设备"。每个工具要有：名称、用途说明、参数说明。

TOOL_SPECS = [
    {
        "name": "query_equipment_params",
        "description": "查询设备的关键参数（转速范围、功率等），输入设备名称和参数名。",
        "parameters": {"equipment": "设备名称，如 主轴", "param": "参数名，如 转速范围"},
    },
    {
        "name": "calc_spindle_speed",
        "description": "计算车削主轴转速：n = 1000 × 切削速度 / (π × 工件直径)。",
        "parameters": {"diameter_mm": "工件直径（毫米）", "cutting_speed": "切削速度（米/分钟）"},
    },
]


def query_equipment_params(equipment: str, param: str):
    """工具实现 1：查设备参数（这里用内置小表模拟车间设备台账）。"""
    device_table = {
        "主轴": {"转速范围": "50 ~ 3000 r/min", "功率": "11 kW"},
        "进给轴": {"进给范围": "0.05 ~ 5 mm/r", "定位精度": "0.01 mm"},
    }
    device = device_table.get(equipment)
    if device is None:
        return f"设备台账中没有「{equipment}」，请检查名称"
    if param not in device:
        return f"设备「{equipment}」没有参数「{param}」，可选：{list(device.keys())}"
    return f"{equipment}的{param}：{device[param]}"


def calc_spindle_speed(diameter_mm: float, cutting_speed: float) -> str:
    """工具实现 2：转速计算公式（45 钢车削常用切削速度 80~120 m/min）。"""
    import math
    n = 1000.0 * cutting_speed / (math.pi * diameter_mm)
    return f"工件直径 {diameter_mm} mm、切削速度 {cutting_speed} m/min 时，主轴转速约 {round(n)} r/min"


# 把"工具名 → 实现函数"登记成字典，方便程序按模型的选择去调用
TOOL_IMPLS = {
    "query_equipment_params": query_equipment_params,
    "calc_spindle_speed": calc_spindle_speed,
}


# ─────────────────────── 第二步：模拟模型（选择工具、填参数） ───────────────────────
# 真实场景里，这一步由大模型完成：它阅读工具描述，返回一个
# 结构化的调用请求（tool_call）。这里用规则模拟同样的行为。
def fake_llm(user_question: str):
    """根据问题关键词，返回与大模型同构的调用请求。"""
    if "算" in user_question:  # 计算类问题 → 计算工具
        return {"name": "calc_spindle_speed",
                "arguments": {"diameter_mm": 50, "cutting_speed": 100}}
    if "参数" in user_question or "转速" in user_question:  # 查参数类问题 → 查询工具
        return {"name": "query_equipment_params",
                "arguments": {"equipment": "主轴", "param": "转速范围"}}
    return None  # 模型认为不需要工具，直接回答


def fake_llm_final_answer(tool_name: str, tool_result: str) -> str:
    """模拟模型看到工具结果后，组织的最终回答。"""
    if tool_name == "query_equipment_params":
        return f"查到了：{tool_result}。选转速时不要超出这个范围。"
    if tool_name == "calc_spindle_speed":
        return f"算好了：{tool_result}。把转速圆整到机床可设置的挡位即可。"
    return tool_result


# ─────────────────────── 第三步：跑一遍完整协议 ───────────────────────
def run_one_round(user_question: str):
    print("=" * 60)
    print(f"用户提问：{user_question}")
    print()

    # 1) 模型读工具描述 → 决定要不要调用工具
    print("【第 1 步】模型读工具描述后，返回的内容（注意：不是答案，是调用请求）：")
    tool_call = fake_llm(user_question)
    if tool_call is None:
        print("  模型判断不需要工具，直接回答。")
        return
    print("  " + json.dumps(tool_call, ensure_ascii=False, indent=4))

    # 2) 你的程序执行工具
    print("【第 2 步】你的程序按请求执行工具：")
    impl = TOOL_IMPLS[tool_call["name"]]
    tool_result = impl(**tool_call["arguments"])
    print(f"  工具「{tool_call['name']}」返回：{tool_result}")

    # 3) 把结果回填给模型
    print("【第 3 步】结果回填给模型，模型基于真实结果给出最终回答：")
    final = fake_llm_final_answer(tool_call["name"], tool_result)
    print(f"  {final}")
    print()


if __name__ == "__main__":
    run_one_round("主轴转速范围是多少？")
    run_one_round("帮我算一下 φ50 工件的车削转速")
    print("=" * 60)
    print("小结：模型不执行代码，只「选工具、填参数」；")
    print("执行和回填都由你的程序完成——这就是 Function Calling 协议。")
