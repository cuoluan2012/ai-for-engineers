# -*- coding: utf-8 -*-
"""
05-1 手写一个神经元：用梯度下降学出一条直线
------------------------------------------------
目标：让一个神经元（y = w*x + b）自己"学会" y ≈ 2x + 1。
不依赖任何深度学习框架，只用 NumPy，把
"前向 → 算损失 → 求梯度 → 更新参数"四步走一遍，就完成了"训练"。
运行：python 05-1_neuron_numpy.py
"""
import numpy as np

# 1) 造数据：x 从 0 到 6，y = 2x + 1，加一点噪声模拟测量误差
np.random.seed(0)
x = np.arange(0, 7, dtype=float)                    # [0, 1, 2, 3, 4, 5, 6]
y_true = 2.0 * x + 1.0 + np.random.normal(0, 0.2, size=len(x))

# 2) 初始化：权重 w 和偏置 b 从 0 起跑
w, b = 0.0, 0.0
lr = 0.05    # 学习率：每次参数更新的步长，太大震荡、太小太慢

def forward(x, w, b):
    """前向：算预测值 y_pred = w*x + b"""
    return w * x + b

def calc_loss(y_pred, y_true):
    """损失：均方误差 MSE，衡量"错多少"（数值越大错得越多）"""
    return np.mean((y_pred - y_true) ** 2)

# 3) 训练循环：前向 → 算损失 → 求梯度 → 更新，共 300 轮
for step in range(300):
    y_pred = forward(x, w, b)                       # 前向
    err = y_pred - y_true                           # 每个点的误差
    dw = np.mean(2 * err * x)                       # 损失对 w 的梯度
    db = np.mean(2 * err)                           # 损失对 b 的梯度
    w -= lr * dw                                    # 更新：朝损失变小的方向走一步
    b -= lr * db
    if step % 50 == 0:
        print(f"step {step:3d}  loss={calc_loss(y_pred, y_true):.4f}  w={w:.3f}  b={b:.3f}")

# 4) 结果对照：学到的 w、b 应逼近真值 2.0 和 1.0
print("-" * 42)
print(f"学到的 w = {w:.3f}（真值 2.0），b = {b:.3f}（真值 1.0）")
print(f"最终损失 = {calc_loss(forward(x, w, b), y_true):.4f}")
