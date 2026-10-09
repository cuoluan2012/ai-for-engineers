"""
09-2 LoRA 机制最小演示：不更新全部权重，只学一个低秩增量
==========================================================

配套《从工程师到 AI 工程师》第 9 章 9.4 节。

问题背景
--------
09-1 里全量微调把通用知识"带偏"了（灾难性遗忘），而且每个参数都要
更新梯度、都要占显存。LoRA 的思路是：**原权重 W 完全冻结不动**，
在旁边加两个小矩阵 B、A（低秩），让新权重 = W + B×A。
训练时只更新 B、A——参数少、显存省、通用知识不动。

本演示用同一个"粗糙度"任务对比两条路线：
  输入  = [硬度, 轴径]（归一化）
  输出  = 表面粗糙度建议值 Ra

  基线  ：预训练好的"通用模型"（不懂厂规）
  路线 A：全量微调 —— 更新所有 1185 个参数
  路线 B：LoRA —— 原权重冻结，只更新低秩旁路 B×A（524 个参数）

运行方式：CPU 即可，秒级完成。依赖：torch（CPU 版即可）。
"""

import torch

torch.manual_seed(42)


# ---------- 规则与数据（与 09-1 相同） ----------

def rule_general(x1, x2):
    return 3.2 - (x1 - 150) / 200 * 1.0 + (x2 - 10) / 70 * 0.5

def rule_factory(x1, x2):
    return 0.6 * rule_general(x1, x2)

def gen_data(n, rule):
    x1 = torch.rand(n) * 150 + 150
    x2 = torch.rand(n) * 70 + 10
    return torch.stack([(x1 - 150) / 150, (x2 - 10) / 70], dim=1), rule(x1, x2).unsqueeze(1)

def make_model():
    """稍大一点的 3 层网络：2 → 32 → 32 → 1（让参数对比更有说服力）。"""
    return torch.nn.Sequential(
        torch.nn.Linear(2, 32),
        torch.nn.ReLU(),
        torch.nn.Linear(32, 32),
        torch.nn.ReLU(),
        torch.nn.Linear(32, 1),
    )

def mae(model, x, y, forward=None):
    """平均绝对误差；LoRA 模型需传入带旁路的前向函数 forward(model, x)。"""
    fn = forward or (lambda m, xx: m(xx))
    with torch.no_grad():
        return (fn(model, x) - y).abs().mean().item()

def count_params(params):
    return sum(p.numel() for p in params)


# ---------- 1. 基线：预训练一个"通用模型" ----------

torch.manual_seed(42)
x_g, y_g = gen_data(600, rule_general)
x_f, y_f = gen_data(300, rule_factory)
x_tf, y_tf = gen_data(100, rule_factory)

model = make_model()
opt = torch.optim.SGD(model.parameters(), lr=0.01)
for _ in range(400):                      # 预训练：学通用规则
    opt.zero_grad()
    loss = torch.nn.functional.mse_loss(model(x_g), y_g)
    loss.backward()
    opt.step()

print("=" * 66)
print("基线：预训练好的通用模型")
print("=" * 66)
print(f"    模型总参数：{count_params(model.parameters())}")
print(f"    厂规测试集 平均误差：{mae(model, x_tf, y_tf):.4f} Ra（不懂厂规）")

# ---------- 2. 路线 A：全量微调 ----------

print()
print("=" * 66)
print("路线 A：全量微调 —— 更新全部权重")
print("=" * 66)
model_a = make_model()
model_a.load_state_dict(model.state_dict())   # 从通用模型出发
opt_a = torch.optim.SGD(model_a.parameters(), lr=0.01)
for _ in range(400):
    opt_a.zero_grad()
    loss = torch.nn.functional.mse_loss(model_a(x_f), y_f)
    loss.backward()
    opt_a.step()
print(f"    更新参数数量：{count_params(model_a.parameters())}（全部）")
print(f"    厂规测试集 平均误差：{mae(model_a, x_tf, y_tf):.4f} Ra")

# ---------- 3. 路线 B：LoRA（原权重冻结 + 低秩旁路） ----------

print()
print("=" * 66)
print("路线 B：LoRA —— 冻结原权重，只学低秩旁路 B×A")
print("=" * 66)

r = 4  # 低秩秩（rank）：旁路矩阵的"宽度"，r 越大表达能力越强、参数越多

def lora_params(model, r):
    """收集 LoRA 需要更新的参数：每层线性层旁路 A(r×in) 与 B(out×r)。"""
    ps = []
    for i, m in enumerate(model):
        if isinstance(m, torch.nn.Linear):
            A = torch.randn(r, m.in_features) * 0.01
            B = torch.zeros(m.out_features, r)
            A.requires_grad_(True)
            B.requires_grad_(True)
            setattr(model, f"lora_A_{i}", A)   # 挂到模型上，方便前向
            setattr(model, f"lora_B_{i}", B)
            ps += [A, B]
    return ps

# 冻结原权重：requires_grad 全关掉
model_b = make_model()
model_b.load_state_dict(model.state_dict())
for p in model_b.parameters():
    p.requires_grad = False
lora_ps = lora_params(model_b, r)
n_lora = count_params(lora_ps)

# 带 LoRA 旁路的前向：y = f(W x) 改为 y = f(W x + B(A x))
def forward_with_lora(model, x):
    h = x
    for i, m in enumerate(model):
        if isinstance(m, torch.nn.Linear):
            # 旁路：(h @ A.T) 得到 (batch×r)，再 @ B.T 得到 (batch×out)
            h = m(h) + (h @ getattr(model, f"lora_A_{i}").T) @ getattr(
                model, f"lora_B_{i}").T
        elif isinstance(m, torch.nn.ReLU):
            h = torch.relu(h)
    return h

opt_b = torch.optim.SGD(lora_ps, lr=0.05)
for _ in range(400):
    opt_b.zero_grad()
    loss = torch.nn.functional.mse_loss(forward_with_lora(model_b, x_f), y_f)
    loss.backward()
    opt_b.step()

print(f"    更新参数数量：{n_lora}（仅旁路 B、A，原权重冻结）")
print(f"    占全量微调的 {n_lora / count_params(model_a.parameters()) * 100:.1f}%")
print(f"    厂规测试集 平均误差：{mae(model_b, x_tf, y_tf, forward_with_lora):.4f} Ra")

# ---------- 4. 合并验证：W + B×A 等价于 LoRA 前向 ----------

print()
print("=" * 66)
print("合并验证：把旁路 B×A 加回原权重，得到'微调后模型'")
print("=" * 66)
model_merged = make_model()
model_merged.load_state_dict(model.state_dict())
for i, m in enumerate(model_merged):
    if isinstance(m, torch.nn.Linear):
        # 把旁路 B×A 加回原权重：W_new = W + B×A（偏置不动）
        m.weight.data.add_(
            getattr(model_b, f"lora_B_{i}") @ getattr(model_b, f"lora_A_{i}"))

with torch.no_grad():
    pred_lora = forward_with_lora(model_b, x_tf)
    pred_merged = model_merged(x_tf)
print(f"    LoRA 前向与'合并后模型'预测最大差：{(pred_lora - pred_merged).abs().max().item():.6f}")
print("    → 两个写法数学等价：部署时只需把 B×A 合进 W，推理速度不变")

# ---------- 5. 三张牌摆一起 ----------

print()
print("=" * 66)
print("对比总表")
print("=" * 66)
print(f"    基线（通用模型）          更新参数 0      厂规误差 {mae(model, x_tf, y_tf):.4f} Ra")
print(f"    全量微调                 更新参数 {count_params(model_a.parameters()):>4}  厂规误差 {mae(model_a, x_tf, y_tf):.4f} Ra")
print(f"    LoRA（r=4）              更新参数 {n_lora:>4}  厂规误差 {mae(model_b, x_tf, y_tf, forward_with_lora):.4f} Ra")
print()
print("结论：LoRA 用不到一半的更新参数达到接近全量微调的效果，")
print("      而且原权重全程冻结——通用知识一点没动。")
print("      真实大模型（如 70 亿参数）上这个差距是数量级的：")
print("      全量要更新 70 亿个参数，LoRA 通常只更新几百万个（占比 <1%）。")
