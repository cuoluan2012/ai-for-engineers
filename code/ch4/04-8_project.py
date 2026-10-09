# 配套项目：设备异常分类（sklearn 全流程）
# 本段做什么：从"数据采集 → 清洗 → 特征 → 训练 → 评估"跑通一个设备状态分类项目
# 运行前要装什么：scikit-learn、numpy、pandas、matplotlib（见 requirements.txt）
# 数据说明：合成示例数据，模拟 6 台泵类设备的运行记录，
#           特征为振动幅值、温度、转速、振动 RMS；标签为 正常/磨损预警/故障 三类。
#           真实项目中用现场传感器数据替换即可（字段结构不变）。
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

# 中文字体（macOS/Windows/Linux 各留一个候选）
matplotlib.rcParams["font.sans-serif"] = ["PingFang SC", "Heiti SC",
                                          "Arial Unicode MS", "SimHei"]
matplotlib.rcParams["axes.unicode_minus"] = False

# ---------- 1. 数据采集：生成合成示例数据 ----------
rng = np.random.default_rng(42)
n_normal, n_wear, n_fault = 200, 120, 80          # 三类样本数（故障最少，接近实际）
normal = rng.normal([2.0, 40, 1450, 2.2], [0.5, 6, 30, 0.4], (n_normal, 4))
wear   = rng.normal([4.5, 58, 1440, 4.0], [0.6, 7, 40, 0.5], (n_wear, 4))
fault  = rng.normal([7.5, 78, 1400, 6.8], [0.9, 9, 60, 0.7], (n_fault, 4))
data = np.vstack([normal, wear, fault])
labels = np.array([0] * n_normal + [1] * n_wear + [2] * n_fault)
df = pd.DataFrame(data, columns=["振动幅值", "温度", "转速", "振动RMS"])
df["状态"] = labels
df["状态名"] = df["状态"].map({0: "正常", 1: "磨损预警", 2: "故障"})

# ---------- 2. 数据检查（清洗的第一步：看有没有缺失、量纲如何）----------
print("=== 数据概览（400 条运行记录）===")
print(df.describe().round(2).loc[["mean", "std", "min", "max"]])
print(f"\n各状态数量：\n{df['状态名'].value_counts().to_string()}")

# ---------- 3. 特征与标签 ----------
X = df[["振动幅值", "温度", "转速", "振动RMS"]].values
y = df["状态"].values

# ---------- 4. 训练/测试切分（测试集 25%，按类别比例分层）----------
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.25, random_state=42, stratify=y)

# ---------- 5. 训练两个模型 ----------
models = {
    "决策树": DecisionTreeClassifier(max_depth=5, random_state=42),
    "KNN(k=5)": KNeighborsClassifier(n_neighbors=5),
}
for name, model in models.items():
    model.fit(X_train, y_train)
    acc = accuracy_score(y_test, model.predict(X_test))
    print(f"\n{name} 测试集准确率：{acc:.2%}")

# ---------- 6. 评估：分类报告 + 混淆矩阵 ----------
best = DecisionTreeClassifier(max_depth=5, random_state=42).fit(X_train, y_train)
y_pred = best.predict(X_test)
print("\n=== 决策树分类报告 ===")
print(classification_report(y_test, y_pred, target_names=["正常", "磨损预警", "故障"]))
cm = confusion_matrix(y_test, y_pred)
print("混淆矩阵（行=实际，列=预测）：")
print(cm)

# ---------- 7. 混淆矩阵可视化 ----------
plt.figure(figsize=(5, 4))
plt.imshow(cm, cmap="Blues")
plt.colorbar()
plt.xticks([0, 1, 2], ["正常", "磨损预警", "故障"])
plt.yticks([0, 1, 2], ["正常", "磨损预警", "故障"])
plt.xlabel("预测状态")
plt.ylabel("实际状态")
for i in range(3):
    for j in range(3):
        plt.text(j, i, cm[i][j], ha="center", va="center", fontsize=14)
plt.title("设备异常分类 · 混淆矩阵")
plt.tight_layout()
plt.savefig("设备异常分类-混淆矩阵.png", dpi=120)
print("\n已保存图示：设备异常分类-混淆矩阵.png")

# ---------- 8. 特征重要性：哪个特征最管用 ----------
importances = pd.Series(best.feature_importances_,
                        index=["振动幅值", "温度", "转速", "振动RMS"])
print("\n特征重要性（越大越能区分状态）：")
print(importances.round(3).to_string())
