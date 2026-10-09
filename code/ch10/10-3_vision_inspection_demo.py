"""
10-3 视觉质检玩具演示：漏检 vs 误报，阈值怎么定
==================================================

配套《从工程师到 AI 工程师》第 10 章 10.3 节。

问题背景
--------
老张要上"机器视觉质检"：摄像头拍工件，模型判断"良品/缺陷"。
但模型判断不是非黑即白——它输出一个"缺陷概率"，
定多少为"判缺陷"（判定阈值）直接影响两类错误：
  · 漏检（False Negative）：缺陷品被判成良品流出 → 客户索赔，代价大；
  · 误报（False Positive）：良品被判成缺陷被拦下 → 人工复检，代价小。
两张错误的代价不对等，阈值不能拍脑袋。

本演示（真实运行，torch CPU）：
  1. 合成"工件图像"数据（良品/带凹坑缺陷，加噪声），训练一个小 CNN；
  2. 用不同判定阈值做测试，统计漏检率 / 误报率；
  3. 代入成本（漏检 100 元/次、误报 5 元/次），算出最优阈值。

运行方式：CPU 真实运行（秒级），依赖 torch（CPU 版）。
"""

import numpy as np
import torch
import torch.nn as nn

torch.manual_seed(42)
np.random.seed(42)

# ---------- 1. 合成数据：16×16 的"工件图像" ----------

SIZE = 16


def make_image(label, rng):
    """生成一张工件图：主体矩形 + 轻微噪声；label=1 时加划痕或凹坑（缺陷）。"""
    img = np.zeros((SIZE, SIZE), dtype=np.float32)
    img[3:13, 3:13] = 1.0                     # 工件主体
    img += rng.normal(0, 0.02, (SIZE, SIZE))  # 拍摄噪声（轻微）
    if label == 1:
        if rng.random() < 0.7:
            # 划痕：一条 5 像素的暗线（水平或垂直），穿过工件内部
            if rng.random() < 0.5:
                row = int(rng.integers(4, 12))
                col = int(rng.integers(4, 8))
                for c in range(col, col + 5):
                    img[row, c] = 0.0
            else:
                col = int(rng.integers(4, 12))
                row = int(rng.integers(4, 8))
                for r in range(row, row + 5):
                    img[r, col] = 0.0
        else:
            # 凹坑：2×2 暗块
            x = int(rng.integers(4, 12))
            y = int(rng.integers(4, 12))
            img[x, y] = 0.0
            img[x + 1, y] = 0.0
            img[x, y + 1] = 0.0
            img[x + 1, y + 1] = 0.0
    return np.clip(img, 0.0, 1.0)


def make_dataset(n, rng):
    xs, ys = [], []
    for _ in range(n):
        label = int(rng.random() < 0.5)
        xs.append(make_image(label, rng))
        ys.append(label)
    x = torch.tensor(np.stack(xs)[:, None, :, :])   # (N,1,16,16)
    y = torch.tensor(ys, dtype=torch.long)
    return x, y


rng = np.random.default_rng(1)
X_train, y_train = make_dataset(1000, rng)
X_test, y_test = make_dataset(300, rng)
print(f"训练集：{len(X_train)} 张（良品/缺陷各半）；测试集：{len(X_test)} 张")

# ---------- 2. 小 CNN（第 5 章讲过：卷积层提特征 → 全连接层分类） ----------

class TinyCNN(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv = nn.Sequential(
            nn.Conv2d(1, 4, 3, padding=1), nn.ReLU(),
            nn.Conv2d(4, 8, 3, padding=1), nn.ReLU(),
        )
        self.fc = nn.Linear(8 * SIZE * SIZE, 2)

    def forward(self, x):
        h = self.conv(x)
        return self.fc(h.flatten(1))


model = TinyCNN()
opt = torch.optim.Adam(model.parameters(), lr=1e-3)
lossf = nn.CrossEntropyLoss()

print("\n训练小 CNN（30 轮，CPU 秒级）……")
for epoch in range(30):
    opt.zero_grad()
    loss = lossf(model(X_train), y_train)
    loss.backward()
    opt.step()
    if (epoch + 1) % 5 == 0:
        acc = (model(X_test).argmax(1) == y_test).float().mean().item()
        print(f"  epoch {epoch + 1:>2}: 损失 {loss.item():.3f}，测试准确率 {acc:.3f}")

# ---------- 3. 阈值实验：漏检 vs 误报 ----------

with torch.no_grad():
    prob_defect = torch.softmax(model(X_test), 1)[:, 1]   # 缺陷概率
    is_defect = (y_test == 1).numpy()
    prob = prob_defect.numpy()

print("\n" + "=" * 70)
print("阈值实验：缺陷概率 ≥ 阈值 → 判缺陷")
print("=" * 70)

COST_MISS = 100.0    # 漏检代价：缺陷品流出，客户索赔/返工
COST_FALSE = 5.0     # 误报代价：良品被拦，人工复检

print(f"{'阈值':>6}{'漏检率':>10}{'误报率':>10}{'漏检数':>8}{'误报数':>8}{'总成本(元)':>12}")
best = None
rows = []
for t in [0.3, 0.4, 0.5, 0.6, 0.7, 0.8]:
    pred_defect = prob >= t
    fn = int(((pred_defect == False) & is_defect).sum())     # 漏检：真缺陷判良品
    fp = int(((pred_defect == True) & (~is_defect)).sum())   # 误报：良品判缺陷
    fn_rate = fn / is_defect.sum()
    fp_rate = fp / (~is_defect).sum()
    cost = fn * COST_MISS + fp * COST_FALSE
    rows.append((t, fn_rate, fp_rate, fn, fp, cost))
    flag = ""
    if best is None or cost < best[1]:
        best = (t, cost, fn, fp)
        flag = "  ← 当前最优"
    print(f"{t:>6.1f}{fn_rate:>10.3f}{fp_rate:>10.3f}{fn:>8}{fp:>8}{cost:>12.0f}{flag}")

# 工程约束：误报率上限 10%——产线复检资源有限，误报太多会堵死
print("-" * 70)
print("工程约束视角：误报率 > 10% 的阈值产线根本跑不动（复检堆成山），剔除后再选：")
constr_rows = [r for r in rows if r[2] <= 0.10]
best2 = min(constr_rows, key=lambda r: r[5])
print(f"  约束（误报率 ≤ 10%）下最优：阈值 {best2[0]}（漏检 {best2[3]} 次 × 100 元 + "
      f"误报 {best2[4]} 次 × 5 元 = {best2[5]:.0f} 元，误报率 {best2[2]:.1%}）")
print(f"  对比：无约束时最优阈值 {best[0]} 虽然账上成本低（{best[1]:.0f} 元），但误报率太高，不可上线。")

print("-" * 70)
print(f"结论：本批数据最优阈值 {best[0]}（漏检 {best[2]} 次 × 100 元 + 误报 {best[3]} 次 × 5 元 = {best[1]:.0f} 元）")
print("  · 阈值往低调 → 漏检少、误报多；往高调 → 漏检多、误报少；")
print("  · 因为漏检代价（100 元）远大于误报（5 元），最优阈值偏'保守'：")
print("    宁可多拦几个良品，也别放走一个缺陷品；")
print("  · 但'账上最优'还要过'工程约束'（误报率上限）——两张错误代价的比例，")
print("    加上产线能承受的误报率，一起决定最终阈值；")
print("  · 换一条产线、换一种缺陷，代价比例变了，阈值要重定——")
print("    这就是'误判成本账'：先把账算清楚，再谈模型好不好。")
