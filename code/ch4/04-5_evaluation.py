# 本段做什么：用混淆矩阵和分类报告评估分类器——故障样本少时准确率会骗人
# 运行前要装什么：scikit-learn、numpy（见 requirements.txt）
# 数据说明：合成示例数据，两类有重叠（更接近真实车间数据，模型无法完美区分）
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import confusion_matrix, classification_report

rng = np.random.default_rng(7)
normal = rng.normal([2.0, 40], [0.8, 10], (150, 2))   # 正常：振动幅值 ~2mm/s，温度 ~40°C
fault = rng.normal([4.5, 60], [1.0, 12], (50, 2))     # 故障：振动幅值 ~4.5mm/s，温度 ~60°C
X = np.vstack([normal, fault])
y = np.array([0] * 150 + [1] * 50)          # 0=正常，1=故障

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42, stratify=y)

tree = DecisionTreeClassifier(max_depth=4, random_state=42).fit(X_train, y_train)
y_pred = tree.predict(X_test)

# 混淆矩阵：行=实际，列=预测（顺序为 0=正常、1=故障）
cm = confusion_matrix(y_test, y_pred)
print("混淆矩阵（行=实际，列=预测）：")
print(f"  正常判正常（正确放行）: {cm[0][0]}")
print(f"  正常判故障（误报）    : {cm[0][1]}")
print(f"  故障判正常（漏检）    : {cm[1][0]}")
print(f"  故障判故障（正确拦截）: {cm[1][1]}")

# 只看准确率会怎样？
acc = (cm[0][0] + cm[1][1]) / cm.sum()
print(f"\n准确率 = {acc:.2%} —— 但故障只占 25%，全判正常也能有 75%")
print("\n分类报告（precision 精确率 / recall 召回率 / f1）：")
print(classification_report(y_test, y_pred, target_names=["正常", "故障"]))
