# -*- coding: utf-8 -*-
"""
05-3 PyTorch 五步法：把"训练一个网络"变成五步模板
------------------------------------------------
第 5.5 节的模板：数据 → 模型 → 损失与优化器 → 训练循环 → 保存模型。
本例用 2 层小网络拟合 y = 2x + 1。
需要先装 PyTorch（CPU 版即可）：
    pip install torch --index-url https://download.pytorch.org/whl/cpu
运行：python 05-3_pytorch_five_steps.py
"""
import torch
import torch.nn as nn

# ① 数据：造 11 个点，y = 2x + 1
x = torch.arange(0, 11, dtype=torch.float32).view(-1, 1)   # 列向量 [0..10]
y_true = 2.0 * x + 1.0

# ② 模型：输入 1 个数 → 隐层 8 个神经元（ReLU 激活）→ 输出 1 个数
model = nn.Sequential(
    nn.Linear(1, 8),
    nn.ReLU(),
    nn.Linear(8, 1),
)

# ③ 损失与优化器
loss_fn = nn.MSELoss()      # 均方误差：衡量"错多少"
# 为什么用 Adam 而不是 SGD？ReLU 网络对步长很敏感，SGD 容易卡在局部极小
#（步长太大震荡、太小不动）；Adam 自动调节每一步的步长，省心很多。
optimizer = torch.optim.Adam(model.parameters(), lr=0.01)

# ④ 训练循环：前向 → 算损失 → 清梯度 → 反向 → 更新，共 800 轮
for step in range(800):
    y_pred = model(x)                      # 前向
    loss = loss_fn(y_pred, y_true)         # 损失
    optimizer.zero_grad()                  # 清空上一步的梯度
    loss.backward()                        # 反向传播：自动算每一层梯度
    optimizer.step()                       # 更新参数
    if step % 160 == 0:
        print(f"step {step:3d}  loss={loss.item():.4f}")

# ⑤ 保存模型（之后加载回来就能直接预测）
torch.save(model.state_dict(), "model_05-3.pt")
print("-" * 42)
print(f"输入 10 时预测值 = {model(x[-1]).item():.3f}（真值 21.0）")
print("模型参数已保存到 model_05-3.pt")
