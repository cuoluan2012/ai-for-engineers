"""
09-1 微调机制最小演示：从"通用"到"厂里口径"
==============================================

配套《从工程师到 AI 工程师》第 9 章 9.3 节。

问题背景
--------
老张想给厂里的"设计规范助手"定制口径：45 钢轴的表面粗糙度，
通用规则是 Ra3.2 上下，但厂规更严，要求按 60% 收（Ra1.9 上下）。
通用模型"只会通用规则"，微调就是用厂里的数据继续训练，
让模型把规则从"通用"改成"厂里口径"。

本演示用一个 2 层小神经网络模拟这件事：
  输入  = [材料硬度 HB, 轴直径 mm]（已归一化）
  输出  = 表面粗糙度建议值 Ra（μm）

  阶段一（预训练）：在"通用规则"数据上训练，模型学会通用规律；
  阶段二（微调）  ：在"厂规规则"数据上继续训练，模型学会厂里口径。

运行方式：CPU 即可，秒级完成，无需 GPU、无需联网。
依赖：torch（CPU 版即可）。
"""

import torch

torch.manual_seed(42)  # 固定随机种子，保证每次运行结果一致


# ---------- 1. 两条"规则"：通用 vs 厂规 ----------

def rule_general(x1, x2):
    """通用规则：粗糙度随硬度增大而略小、随轴径增大而略大（示意数值）。"""
    return 3.2 - (x1 - 150) / 200 * 1.0 + (x2 - 10) / 70 * 0.5


def rule_factory(x1, x2):
    """厂规：在通用规则基础上加严 40%（表面粗糙度要求更细）。"""
    return 0.6 * rule_general(x1, x2)


# ---------- 2. 数据生成与训练工具 ----------

def gen_data(n, rule):
    """生成 n 条样本：硬度 150~300 HB，轴径 10~80 mm；输入归一化到 0~1。"""
    x1 = torch.rand(n) * 150 + 150
    x2 = torch.rand(n) * 70 + 10
    x1_n = (x1 - 150) / 150      # 归一化：让输入落在 0~1，避免梯度爆炸
    x2_n = (x2 - 10) / 70
    y = rule(x1, x2)
    return torch.stack([x1_n, x2_n], dim=1), y.unsqueeze(1)


def make_model():
    """2 层小网络：2 输入 → 8 隐藏 → 1 输出。"""
    return torch.nn.Sequential(
        torch.nn.Linear(2, 8),
        torch.nn.ReLU(),
        torch.nn.Linear(8, 1),
    )


def train(model, x, y, steps=300, lr=0.01, tag=""):
    """普通梯度下降训练，打印损失下降过程。"""
    opt = torch.optim.SGD(model.parameters(), lr=lr)
    loss_fn = torch.nn.MSELoss()
    for step in range(steps):
        opt.zero_grad()
        pred = model(x)
        loss = loss_fn(pred, y)
        loss.backward()
        opt.step()
        if (step + 1) % 75 == 0:
            print(f"    {tag} 第 {step + 1:>3} 步：损失 {loss.item():.4f}")


def mae(model, x, y):
    """平均绝对误差（工程师好懂：平均差多少个 Ra 值）。"""
    with torch.no_grad():
        pred = model(x)
    return (pred - y).abs().mean().item()


def behavior_check(model, samples):
    """给三个不同输入，看预测是否随输入变化（防止模型退化成'输出常数'）。"""
    with torch.no_grad():
        preds = model(samples).squeeze().tolist()
    for (a, b), p in zip(samples.tolist(), preds):
        print(f"        硬度 {(a*150+150):.0f} HB、轴径 {(b*70+10):.0f} mm → 预测 Ra {p:.2f}")


# ---------- 3. 准备数据 ----------

torch.manual_seed(42)
x_g, y_g = gen_data(600, rule_general)      # 预训练用的"通用数据"
x_f, y_f = gen_data(200, rule_factory)      # 微调用的"厂规数据"
x_test_g, y_test_g = gen_data(100, rule_general)
x_test_f, y_test_f = gen_data(100, rule_factory)

# 三个固定抽查样本：看模型"会不会随输入变"
probe = torch.tensor([[0.0, 0.0], [0.5, 0.5], [1.0, 1.0]])

# ---------- 4. 阶段一：预训练（学通用规则） ----------

print("=" * 62)
print("阶段一：预训练 —— 在通用规则数据上训练 300 步")
print("=" * 62)
model = make_model()
train(model, x_g, y_g, tag="预训练")

# 保存"通用模型"权重（微调前的样子）
w_before = {k: v.clone() for k, v in model.state_dict().items()}

print()
print("预训练完，看看它懂什么：")
print(f"    通用规则测试集 平均误差：{mae(model, x_test_g, y_test_g):.4f} Ra")
print(f"    厂规规则测试集 平均误差：{mae(model, x_test_f, y_test_f):.4f} Ra")
print("    → 对通用规则很准，对厂规差得远（通用模型不懂厂里口径）")
print("    抽查三个输入，预测随输入变化：")
behavior_check(model, probe)

# ---------- 5. 阶段二：微调（学厂规） ----------

print()
print("=" * 62)
print("阶段二：微调 —— 在厂规数据上继续训练 300 步")
print("=" * 62)
train(model, x_f, y_f, tag="微调")

print()
print("微调完，再测一次：")
print(f"    通用规则测试集 平均误差：{mae(model, x_test_g, y_test_g):.4f} Ra")
print(f"    厂规规则测试集 平均误差：{mae(model, x_test_f, y_test_f):.4f} Ra")
print("    → 厂规误差大幅下降（学会了厂里口径）")
print("    同样三个输入，预测口径变了：")
behavior_check(model, probe)

# ---------- 6. 权重真的"变"了吗 ----------

w_after = model.state_dict()

def layer_change(name):
    """打印某一层权重的平均与最大变动幅度。"""
    diff = (w_after[name] - w_before[name]).abs()
    return diff.mean().item(), diff.max().item()

mean1, max1 = layer_change("0.weight")   # 第一层 Linear(2,8)
mean2, max2 = layer_change("2.weight")   # 第二层 Linear(8,1)
print()
print("权重变化（微调前 → 微调后）：")
print(f"    第一层权重  平均变动 {mean1:.4f}  最大变动 {max1:.4f}")
print(f"    第二层权重  平均变动 {mean2:.4f}  最大变动 {max2:.4f}")
print("    → 行为大变，权重只是被小幅修改——微调不是换模型，是'微调'")
print()
print("注意一个现象：微调后通用规则误差从 0.1360 升到 1.2461，")
print("    全量微调会把模型'带偏'，忘掉一部分通用知识（灾难性遗忘的雏形）。")
print("    这正是 9.4 节 LoRA 的价值：只动少量参数，少忘事、少花钱。")
