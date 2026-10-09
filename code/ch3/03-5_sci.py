# 用途：第 3 章 3.5 节示例——科学计算三件套：NumPy / Pandas / Matplotlib
# 运行前：pip install numpy pandas matplotlib；axes.csv 与本脚本同目录
# 场景：一次读入整批轴参数，向量化计算安全系数，筛选不合格轴，画安全系数图。

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # 无界面环境（服务器/脚本）用 Agg 后端
import matplotlib.pyplot as plt

plt.rcParams["font.sans-serif"] = ["PingFang SC", "Heiti SC", "Arial Unicode MS", "SimHei"]
plt.rcParams["axes.unicode_minus"] = False

# 1) Pandas：把 CSV 表格读成 DataFrame（像把 Excel 搬进 Python）
df = pd.read_csv("axes.csv", encoding="utf-8")
print("前 3 行：")
print(df.head(3).to_string(index=False))

# 2) NumPy：数组向量化计算——一次算整批，不用逐行写循环
d = df["直径mm"].to_numpy()                 # 直径数组
W = np.pi * d ** 3 / 32                     # 抗弯截面系数 mm³（整批一起算）
Wt = np.pi * d ** 3 / 16                    # 抗扭截面系数 mm³
sigma = df["弯矩N·m"].to_numpy() * 1000 / W  # 弯曲应力 MPa
tau = df["扭矩N·m"].to_numpy() * 1000 / Wt   # 扭转应力 MPa
sigma_ca = np.sqrt(sigma ** 2 + 4 * tau ** 2)  # 第三强度理论合成应力

df["弯扭合成应力MPa"] = np.round(sigma_ca, 2)
df["安全系数"] = np.round(df["屈服强度MPa"].to_numpy() / sigma_ca, 2)
df["结论"] = np.where(df["安全系数"] >= 1.5, "合格", "不合格")

# 3) Pandas 筛选：只看不合格的轴
bad = df[df["结论"] == "不合格"]
print("\n不合格轴：")
print(bad[["轴号", "材料", "弯扭合成应力MPa", "安全系数"]].to_string(index=False))

# 4) Matplotlib：把安全系数画出来（柱状图 + 合格线）
plt.figure(figsize=(8, 4))
colors = ["#2B6CB0" if c == "合格" else "#FF7D00" for c in df["结论"]]
plt.bar(df["轴号"], df["安全系数"], color=colors)
plt.axhline(1.5, color="#D32F2F", linestyle="--", linewidth=1)
plt.text(0.02, 1.58, "n=1.5 合格线", color="#D32F2F", fontsize=9)
plt.ylabel("安全系数 n")
plt.title("轴静强度校核：各轴安全系数分布")
plt.tight_layout()
plt.savefig("安全系数分布.png", dpi=150)
print("\n图已保存：安全系数分布.png")
