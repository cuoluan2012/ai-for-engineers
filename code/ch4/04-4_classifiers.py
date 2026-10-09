# 本段做什么：在轴承振动数据上对比三种分类器——KNN、决策树、逻辑回归
# 运行前要装什么：scikit-learn、numpy（见 requirements.txt）
# 数据说明：合成示例数据，模拟轴承两个特征（振动幅值、温度），标签为正常/故障
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score

# 合成示例数据：正常轴承（低温、低振动）与故障轴承（高温、高振动）两簇
rng = np.random.default_rng(7)
normal = rng.normal([2.0, 40], [0.6, 8], (150, 2))     # 振动幅值 ~2mm/s，温度 ~40°C
fault = rng.normal([6.0, 75], [0.8, 9], (50, 2))       # 振动幅值 ~6mm/s，温度 ~75°C
X = np.vstack([normal, fault])
y = np.array([0] * 150 + [1] * 50)                     # 0=正常，1=故障

# 训练/测试切分：测试集 30%，随机种子固定保证可复现
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42, stratify=y)

# 三种分类器，同一份数据、同样的训练/测试切分
models = {
    "KNN（看邻居，k=5）": KNeighborsClassifier(n_neighbors=5),
    "决策树（一连串 if-else）": DecisionTreeClassifier(max_depth=4, random_state=42),
    "逻辑回归（输出故障概率）": LogisticRegression(max_iter=1000),
}
for name, model in models.items():
    model.fit(X_train, y_train)
    acc = accuracy_score(y_test, model.predict(X_test))
    print(f"{name:<24} 测试集准确率：{acc:.2%}")

# 打印前 3 个测试样本的决策树预测结果，方便对照正文
tree = models["决策树（一连串 if-else）"]
probe = X_test[:3]
print("\n决策树对前 3 个测试样本的预测：", tree.predict(probe).tolist(), "（1=故障）")
