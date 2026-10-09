# 用途：第 3 章 3.8 节配套项目——轴静强度校核工具 v0.1
# 运行：python 03-8_project.py（axes.csv 与本脚本同目录）
# 依赖：pandas、numpy、matplotlib（见 requirements.txt）
# 场景：老张拿到 6 根轴的参数表，要按第三强度理论算弯扭合成应力、
#       安全系数，输出报告 + 图，并把不合格的挑出来。

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams["font.sans-serif"] = ["PingFang SC", "Heiti SC", "Arial Unicode MS", "SimHei"]
plt.rcParams["axes.unicode_minus"] = False

INPUT_CSV = "axes.csv"
OUTPUT_CSV = "校核结果.csv"
OUTPUT_PNG = "安全系数分布.png"
MIN_SAFETY = 1.5  # 最小许用安全系数


def 校核(df):
    """对整批轴做静强度校核，返回带计算列的表"""
    d = df["直径mm"].to_numpy()
    W = np.pi * d ** 3 / 32                       # 抗弯截面系数 mm³
    Wt = np.pi * d ** 3 / 16                      # 抗扭截面系数 mm³
    sigma = df["弯矩N·m"].to_numpy() * 1000 / W    # 弯曲应力 MPa
    tau = df["扭矩N·m"].to_numpy() * 1000 / Wt     # 扭转应力 MPa
    sigma_ca = np.sqrt(sigma ** 2 + 4 * tau ** 2)  # 第三强度理论
    df["弯扭合成应力MPa"] = np.round(sigma_ca, 2)
    df["安全系数"] = np.round(df["屈服强度MPa"].to_numpy() / sigma_ca, 2)
    df["结论"] = np.where(df["安全系数"] >= MIN_SAFETY, "合格", "不合格")
    return df


def 主程序():
    df = pd.read_csv(INPUT_CSV, encoding="utf-8")
    df = 校核(df)

    # 1) 控制台报告
    print("=" * 50)
    print("轴静强度校核报告（第三强度理论，最小安全系数 n = 1.5）")
    print("=" * 50)
    print(df[["轴号", "材料", "弯扭合成应力MPa", "安全系数", "结论"]].to_string(index=False))
    bad = df[df["结论"] == "不合格"]
    print("-" * 50)
    print(f"共校核 {len(df)} 根轴；不合格 {len(bad)} 根；最低安全系数 n = {df['安全系数'].min():.2f}")

    # 2) 导出结果 CSV（utf-8-sig 让 Excel 打开不乱码）
    df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")

    # 3) 安全系数分布图
    plt.figure(figsize=(8, 4))
    colors = ["#2B6CB0" if c == "合格" else "#FF7D00" for c in df["结论"]]
    plt.bar(df["轴号"], df["安全系数"], color=colors)
    plt.axhline(MIN_SAFETY, color="#D32F2F", linestyle="--", linewidth=1)
    plt.text(0.02, MIN_SAFETY + 0.08, "n=1.5 合格线", color="#D32F2F", fontsize=9)
    plt.ylabel("安全系数 n")
    plt.title("轴静强度校核：各轴安全系数分布")
    plt.tight_layout()
    plt.savefig(OUTPUT_PNG, dpi=150)
    print(f"结果已导出：{OUTPUT_CSV}；图已保存：{OUTPUT_PNG}")


if __name__ == "__main__":
    主程序()
