"""
09-5 配套项目：算清"自建 vs 调用 API"的账
============================================

配套《从工程师到 AI 工程师》第 9 章 9.8 节（工程师贴士落地版）。

做什么
------
私有化部署前先算账：同样一套"设计规范助手"，是每月按量调用云端
API 划算，还是自己买 GPU、租机房、养运维划算？本脚本把账算成一张
可以反复改参数的表格——读者改自己的数字，立刻得到结论。

所有价格均为**示意值，仅用于演示算法**；真实报价以供应商官网为准。

运行方式：离线真实运行，零第三方依赖，纯标准库。
"""

# ---------- 1. 参数（读者按自己的情况改这里） ----------

# 使用量
MONTH_CALLS = 1_000_000        # 月调用次数（次/月）
AVG_IN_TOKENS = 500            # 每次请求平均输入 token 数
AVG_OUT_TOKENS = 200           # 每次请求平均输出 token 数

# 调用 API（示意价：某国产大模型 API 公开价量级）
API_IN_PRICE = 12.0            # 元 / 百万输入 token
API_OUT_PRICE = 12.0           # 元 / 百万输出 token

# 自建（示意值：1 台 4×A100 服务器，企业内网部署）
HW_COST = 300_000              # 硬件一次性投入（元）
DEPREC_YEARS = 3               # 折旧年限（年）
GPU_POWER_W = 4 * 400          # 4 卡 × 400W
ELECTRIC_YUAN_PER_KWH = 0.8    # 电费单价（元/度）
OPS_COST = 100_000             # 运维人力 + 机房 + 带宽（元/年）


# ---------- 2. 算账 ----------

def api_yearly(month_calls, in_tok, out_tok):
    """调用 API 的年度成本（元）。"""
    in_m = month_calls * in_tok / 1e6      # 月输入 token（百万）
    out_m = month_calls * out_tok / 1e6    # 月输出 token（百万）
    return (in_m * API_IN_PRICE + out_m * API_OUT_PRICE) * 12


def self_yearly():
    """自建的年度成本（元）= 折旧 + 电费 + 运维。"""
    elec = GPU_POWER_W / 1000 * 24 * 365 * ELECTRIC_YUAN_PER_KWH
    return HW_COST / DEPREC_YEARS + elec + OPS_COST


def breakeven():
    """盈亏临界点：月调用量达到多少时，自建开始比 API 便宜。"""
    lo, hi = 1, 10_000_000_000
    while lo < hi:
        mid = (lo + hi) // 2
        if api_yearly(mid, AVG_IN_TOKENS, AVG_OUT_TOKENS) >= self_yearly():
            hi = mid
        else:
            lo = mid + 1
    return lo


# ---------- 3. 输出 ----------

api_cost = api_yearly(MONTH_CALLS, AVG_IN_TOKENS, AVG_OUT_TOKENS)
self_cost = self_yearly()
per_million = api_cost / (MONTH_CALLS * (AVG_IN_TOKENS + AVG_OUT_TOKENS) / 1e6)

print("=" * 66)
print("自建 vs 调用 API 算账表（示意价，算法可复用）")
print("=" * 66)
print(f"使用量      ：月 {MONTH_CALLS:,} 次，平均每次 输入 {AVG_IN_TOKENS} + 输出 {AVG_OUT_TOKENS} token")
print(f"调用 API    ：年度成本 ¥{api_cost:,.0f}  "
      f"（约 ¥{per_million:.2f}/百万 token）")
print(f"自建部署    ：年度成本 ¥{self_cost:,.0f}")
print(f"           （硬件 ¥{HW_COST/10000:.0f} 万 / {DEPREC_YEARS} 年折旧 + "
      f"电费 ¥{GPU_POWER_W/1000*24*365*ELECTRIC_YUAN_PER_KWH:,.0f} + "
      f"运维 ¥{OPS_COST/10000:.0f} 万）")
print("-" * 66)
print(f"盈亏临界点  ：月调用量约 {breakeven():,} 次时，两条路线打平")
print()
if api_cost > self_cost:
    print("结论：按当前参数，自建更便宜（但别忘了数据隐私、")
    print("      升级维护、GPU 故障这些 API 方案没有的隐性成本）。")
else:
    print("结论：按当前参数，调用 API 更便宜；等月调用量涨过临界点")
    print("      再考虑自建。")
print()
print("改一下参数再看：把 MONTH_CALLS、API 单价、硬件价格换成你的真实数字，")
print("      立刻得到你自己的结论——这就是'算账'的意义。")
