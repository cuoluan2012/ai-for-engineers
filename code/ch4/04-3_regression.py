# 本段做什么：线性回归拟合刀具磨损曲线——切削件数越多，刀具磨损越大
# 运行前要装什么：scikit-learn、numpy、matplotlib（见 requirements.txt）
# 数据说明：示例数据为合成数据，模拟某车床刀具的累计切削件数与磨损量
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

# 中文字体（macOS/Windows/Linux 各留一个候选）
matplotlib.rcParams["font.sans-serif"] = ["PingFang SC", "Heiti SC",
                                          "Arial Unicode MS", "SimHei"]
matplotlib.rcParams["axes.unicode_minus"] = False

# 合成示例数据：累计切削件数（100~500 件），磨损量随件数线性增长并带波动
rng = np.random.default_rng(42)
cuts = np.arange(100, 501, 50)                      # 累计切削件数（件）
wear = 0.02 * cuts / 100 + rng.normal(0, 0.02, len(cuts))   # 磨损量（mm）

X = cuts.reshape(-1, 1)                             # 特征：切削件数
model = LinearRegression().fit(X, wear)             # 训练线性回归模型

# 模型参数解读（工程语义）
print(f"斜率：每加工 100 件，刀具磨损 {model.coef_[0] * 100:.3f} mm")
print(f"截距：初始磨损量 {model.intercept_:.4f} mm")

# 用模型预测：加工到第 600 件时磨损多少
pred_600 = model.predict([[600]])[0]
print(f"预测第 600 件的磨损量：{pred_600:.3f} mm")
print(f"判断：超过 0.60 mm 即到换刀线 → 第 600 件{'需要' if pred_600 > 0.60 else '尚不需'}换刀")

# 画图：散点为实测，直线为拟合规律
plt.figure(figsize=(6, 4))
plt.scatter(cuts, wear, s=40, color="#2B6CB0", label="实测磨损量")
plt.plot(cuts, model.predict(X), color="#FF7D00", linewidth=2, label="拟合直线")
plt.axhline(0.60, color="#D32F2F", linestyle="--", linewidth=1.5, label="换刀线 0.60 mm")
plt.xlabel("累计切削件数（件）")
plt.ylabel("磨损量（mm）")
plt.title("刀具磨损趋势：线性回归拟合")
plt.legend()
plt.tight_layout()
plt.savefig("刀具磨损拟合.png", dpi=120)
print("已保存图示：刀具磨损拟合.png")
