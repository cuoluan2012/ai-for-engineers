# -*- coding: utf-8 -*-
"""
05-4 配套项目：零件表面缺陷图像分类（简化版）
------------------------------------------------
数据：程序生成的 16×16 灰度"零件图"，三类——normal（正常）、
scratch（划痕：一条暗线）、bubble（气泡：一个暗圆斑）。
模型：一个很小的 CNN（卷积 → 池化 → 卷积 → 全连接）。
目标：训练后能在测试集上给出准确率与混淆矩阵。
零下载依赖：数据是合成的、可复现。
需要先装 PyTorch（CPU 版即可）。
运行：python 05-4_defect_cnn.py
"""
import numpy as np
import torch
import torch.nn as nn

torch.manual_seed(0)
np.random.seed(0)

# ---------- 1) 合成数据：三类 16×16 灰度图 ----------
def make_image(label, rng):
    """生成一张 16×16 图：normal=均匀噪声；scratch=暗线；bubble=暗圆斑"""
    img = rng.uniform(0.35, 0.7, (16, 16))          # 背景：随机灰度
    if label == 1:                                   # 划痕：一条暗线
        c = rng.integers(2, 14)
        img[:, c] = 0.15
    elif label == 2:                                 # 气泡：一个暗圆斑
        cy, cx = rng.integers(5, 11, size=2)
        yy, xx = np.mgrid[0:16, 0:16]
        img[(yy - cy) ** 2 + (xx - cx) ** 2 <= 4] = 0.15
    return img

rng = np.random.default_rng(0)
xs, ys = [], []
for label in range(3):                               # 0=正常 1=划痕 2=气泡
    for _ in range(120):                             # 每类 120 张
        xs.append(make_image(label, rng))
        ys.append(label)
X = np.array(xs, dtype=np.float32).reshape(-1, 1, 16, 16)   # N×1×16×16
Y = np.array(ys, dtype=np.int64)

# 切分前必须打乱！否则同类的图挤在一起，测试集可能只剩一类
idx = np.random.permutation(len(X))
X, Y = X[idx], Y[idx]
n_train = 300
X_train, Y_train = torch.tensor(X[:n_train]), torch.tensor(Y[:n_train])
X_test, Y_test = torch.tensor(X[n_train:]), torch.tensor(Y[n_train:])
print(f"训练集 {X_train.shape[0]} 张，测试集 {X_test.shape[0]} 张（正常/划痕/气泡）")

# ---------- 2) 模型：很小的 CNN ----------
model = nn.Sequential(
    nn.Conv2d(1, 4, 3), nn.ReLU(), nn.MaxPool2d(2),   # 16→14→7
    nn.Conv2d(4, 8, 3), nn.ReLU(), nn.MaxPool2d(2),   # 7→5→2
    nn.Flatten(),
    nn.Linear(8 * 2 * 2, 3),                          # 2×2×8 → 3 类
)
loss_fn = nn.CrossEntropyLoss()                       # 分类损失
optimizer = torch.optim.Adam(model.parameters(), lr=0.02)

# ---------- 3) 训练 60 轮 ----------
for epoch in range(60):
    model.train()
    y_pred = model(X_train)
    loss = loss_fn(y_pred, Y_train)
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()
    if epoch % 12 == 0:
        acc = (model(X_train).argmax(1) == Y_train).float().mean().item()
        print(f"epoch {epoch:2d}  loss={loss.item():.4f}  训练准确率={acc:.2%}")

# ---------- 4) 测试集评估 ----------
model.eval()
with torch.no_grad():
    pred = model(X_test).argmax(1)
acc = (pred == Y_test).float().mean().item()
print("-" * 44)
print(f"测试集准确率 = {acc:.2%}")

# 混淆矩阵（行=实际，列=预测）
cm = np.zeros((3, 3), dtype=int)
for t, p in zip(Y_test.numpy(), pred.numpy()):
    cm[t, p] += 1
print("混淆矩阵（行=实际：正常/划痕/气泡；列=预测）：")
print(cm)
