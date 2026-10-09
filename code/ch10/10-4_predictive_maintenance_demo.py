"""
10-4 预测性维护玩具演示：预警阈值怎么定
==========================================

配套《从工程师到 AI 工程师》第 10 章 10.4 节。

问题背景
--------
老张想给关键设备（主轴/电机）做"预测性维护"：
用传感器数据预测设备还能撑多久，提前安排维修，避免意外停机。
但"提前多久报警"是个权衡：
  · 提前太多 → 设备还没坏就维修（误报），白白停机检修，有成本；
  · 提前太少 / 没报警 → 设备真坏了才停（漏报），产线停摆，代价巨大。

本演示（真实运行，torch CPU）：
  1. 合成一批设备的"健康度轨迹"（平稳运行 → 临近故障快速退化 → 故障），
  2. 用最近 8 步健康度预测"剩余寿命"，训练一个小 MLP；
  3. 模拟在线预警：不同预警阈值下，统计"有效预警 / 过早误报 / 漏报"，
     代入成本（误报 500 元、停机 10000 元），算出最优阈值。

运行方式：CPU 真实运行（秒级），依赖 torch（CPU 版）。
"""

import numpy as np
import torch
import torch.nn as nn

torch.manual_seed(42)
np.random.seed(42)

# ---------- 1. 合成设备健康度轨迹 ----------

N_DEV, T_MAX = 300, 100     # 300 台设备，每台最多 100 个时间步
WIN = 8                     # 特征窗口：最近 8 步健康度


def make_trajectory(rng):
    """
    健康度 h(t)：平稳段（约 1.0）→ 退化段（故障前 20~40 步快速下降）→ 故障（0.15~0.25）。
    每台设备退化时长与故障后健康度都随机——模拟真实设备差异：
    有的设备'拖很久才坏'，有的'说坏就坏'。
    """
    t_f = int(rng.uniform(60, 95))                # 故障时刻随机
    t_deg_len = int(rng.uniform(20, 40))          # 退化时长随机
    t_degrade = t_f - t_deg_len                    # 退化开始时刻
    h_fail = float(rng.uniform(0.15, 0.25))        # 故障后健康度随机
    h = np.zeros(T_MAX)
    for t in range(T_MAX):
        if t < t_degrade:
            h[t] = 1.0 - 0.001 * t + rng.normal(0, 0.01)              # 平稳段
        elif t < t_f:
            k = (t - t_degrade) / t_deg_len                           # 0→1 线性退化
            h[t] = 1.0 - (1.0 - h_fail) * k + rng.normal(0, 0.01)     # 快速下降
        else:
            h[t] = h_fail + rng.normal(0, 0.01)                       # 故障后
    return np.clip(h, 0.0, 1.0), t_f


rng = np.random.default_rng(1)
trajectories = [make_trajectory(rng) for _ in range(N_DEV)]


def build_samples(h, t_f):
    """
    特征：最近 8 步健康度 + 窗口斜率（趋势）——这是"特征工程"：
    光给原始值，模型很难分辨'平稳'和'退化'；加上斜率，一眼就能看出来。
    标签：剩余寿命 = (t_f - t)/30，归一化 0~1。
    """
    xs, ys = [], []
    for t in range(WIN, T_MAX):
        window = h[t - WIN:t]
        slope = (window[-1] - window[0]) / (WIN - 1)     # 趋势特征
        xs.append(np.concatenate([window, [slope]]))
        ys.append(min(max((t_f - t) / 30.0, 0.0), 1.0))
    return np.array(xs, dtype=np.float32), np.array(ys, dtype=np.float32)


# 按设备切分：前 240 台训练、后 60 台测试
train_n = int(N_DEV * 0.8)
X_train, Y_train = [], []
X_test, Y_test = [], []
for i, (h, t_f) in enumerate(trajectories):
    x, y = build_samples(h, t_f)
    if i < train_n:
        X_train.append(x)
        Y_train.append(y)
    else:
        X_test.append(x)
        Y_test.append(y)
X_train = torch.tensor(np.concatenate(X_train))       # (N,8)
Y_train = torch.tensor(np.concatenate(Y_train)[:, None])
X_test = torch.tensor(np.concatenate(X_test))
Y_test = torch.tensor(np.concatenate(Y_test)[:, None])

print(f"训练样本：{len(X_train)} 条（{train_n} 台设备）；测试样本：{len(X_test)} 条（{N_DEV - train_n} 台设备）")
print(f"特征：最近 {WIN} 步健康度 + 趋势斜率（共 {WIN + 1} 维）；标签：剩余寿命（归一化 0~1）")

# ---------- 2. 小 MLP：8 维特征 → 预测剩余寿命 ----------

model = nn.Sequential(nn.Linear(WIN + 1, 64), nn.ReLU(), nn.Linear(64, 1))
opt = torch.optim.Adam(model.parameters(), lr=1e-2)
lossf = nn.MSELoss()

# 样本加权：退化/故障段（剩余寿命 < 0.6）权重 3，平稳段权重 1——
# 避免模型被大量"健康样本"带偏（健康样本多，但真正要学的是退化规律）
train_w = torch.where(Y_train < 0.6,
                      torch.full_like(Y_train, 3.0),
                      torch.full_like(Y_train, 1.0))

print("\n训练小 MLP（20 轮，CPU 秒级）……")
for epoch in range(20):
    opt.zero_grad()
    loss = (lossf(model(X_train), Y_train) * train_w).mean()
    loss.backward()
    opt.step()
    with torch.no_grad():
        mae = (model(X_test) - Y_test).abs().mean().item()
    if (epoch + 1) % 5 == 0:
        print(f"  epoch {epoch + 1:>2}: 损失 {loss.item():.5f}，测试平均绝对误差 {mae:.3f}")

# 抽样：3 台测试设备"临近故障段"的预测 vs 真实
print("\n抽样：3 台测试设备临近故障段（真实剩余寿命 < 0.6）的预测 vs 真实")
for dev in range(3):
    h, t_f = trajectories[train_n + dev]
    x, y = build_samples(h, t_f)
    with torch.no_grad():
        p = model(torch.tensor(x)).numpy().ravel()
    print(f"  设备 {dev + 1}（故障时刻 t = {t_f}）：")
    for t in [t_f - 24, t_f - 12, t_f - 4]:
        idx = t - WIN
        if 0 <= idx < len(y):
            print(f"    距故障 {t_f - t:>2} 步：预测剩余寿命 {p[idx]:.3f}，真实 {y[idx]:.3f}")

# ---------- 3. 预警阈值实验：提前报警的代价 ----------

COST_FALSE_ALARM = 500.0     # 误报：没坏就去修，一次检修成本
COST_DOWNTIME = 10000.0      # 漏报：真坏了才停，产线停机损失

print("\n" + "=" * 70)
print("预警策略：预测剩余寿命 < 阈值 → 触发报警（安排检修）")
print("评估口径（每台设备，只记第一次报警）：")
print("  · 故障前 1~10 步内报警 → 有效预警（正好提前发现，成本记 0）")
print("  · 故障前 10 步以上报警 → 过早误报（设备没坏就检修，一次检修成本）")
print("  · 直到故障都没报警（或报警晚于故障）→ 漏报（一次停机损失）")
print("=" * 70)

print(f"{'预警阈值':>8}{'有效预警':>10}{'过早误报':>10}{'漏报':>8}{'总成本(元)':>12}")
best = None
for th in [0.15, 0.25, 0.35, 0.45, 0.55, 0.65]:
    n_ok, n_false, n_miss = 0, 0, 0
    for i in range(train_n, N_DEV):
        h, t_f = trajectories[i]
        x, y = build_samples(h, t_f)
        with torch.no_grad():
            p = model(torch.tensor(x)).numpy().ravel()
        # 找第一次报警时刻（预测剩余寿命 < th）
        alarm_idx = np.where(p < th)[0]
        if len(alarm_idx) == 0:
            n_miss += 1
        else:
            first = alarm_idx[0] + WIN          # 报警时的真实时刻
            lead = t_f - first                  # 提前量（步）
            if 1 <= lead <= 10:
                n_ok += 1
            elif lead > 10:
                n_false += 1
            else:
                n_miss += 1                     # 报警晚于故障
    cost = n_false * COST_FALSE_ALARM + n_miss * COST_DOWNTIME
    flag = ""
    if best is None or cost < best[1]:
        best = (th, cost, n_ok, n_false, n_miss)
        flag = "  ← 当前最优"
    print(f"{th:>8.2f}{n_ok:>10}{n_false:>10}{n_miss:>8}{cost:>12.0f}{flag}")

print("-" * 70)
print(f"结论：本批数据最优预警阈值 {best[0]}（有效预警 {best[2]} 台、"
      f"过早误报 {best[3]} 台、漏报 {best[4]} 台，总成本 {best[1]:.0f} 元）")
print("  · 阈值调高（更容易报警）→ 漏报少、误报多；调低 → 相反；")
print("  · 停机代价（10000 元）远大于一次检修（500 元），所以最优阈值偏'敏感'：")
print("    宁可多检修几次，也别让设备真趴窝；")
print("  · 阈值不是模型参数，是'业务参数'——取决于停机损失与检修成本的比例，")
print("    每家厂的比例不一样，阈值要按自己的账本定。")
