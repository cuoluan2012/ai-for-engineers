# 本段做什么：演示过拟合——多项式次数越高，训练误差越小、测试误差反而变大
# 运行前要装什么：scikit-learn、numpy（见 requirements.txt）
# 数据说明：合成示例数据，模拟"振动幅值与刀具磨损"的非线性关系
import numpy as np
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import make_pipeline
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import cross_val_score

rng = np.random.default_rng(3)
X = np.sort(rng.uniform(0, 6, 40)).reshape(-1, 1)          # 振动幅值（mm/s）
y = 0.5 * X.ravel() ** 2 + rng.normal(0, 1.2, 40)          # 磨损量（mm），真实是二次关系

# 用三个"模型复杂度"拟合：次数 1（太简单）/ 3（合适）/ 15（过拟合）
for degree in (1, 3, 15):
    model = make_pipeline(PolynomialFeatures(degree), LinearRegression())
    model.fit(X, y)
    mse_train = mean_squared_error(y, model.predict(X))
    # 交叉验证：换着题目考 5 次，防止一次考运
    scores = cross_val_score(model, X, y, cv=5,
                             scoring="neg_mean_squared_error")
    print(f"次数 {degree:>2}：训练误差 {mse_train:6.2f}，"
          f"5 折交叉验证平均误差 {-scores.mean():6.2f}")

print("\n解读：次数 1 训练误差大（欠拟合）；次数 3 两边都好（合适）；")
print("次数 15 训练误差最小但交叉验证误差最大——把噪声也当规律了（过拟合）")
