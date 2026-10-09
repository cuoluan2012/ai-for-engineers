# 本段做什么：特征工程两个常用操作——归一化（拉齐量纲）和独热编码（类别转 0/1）
# 运行前要装什么：scikit-learn、numpy、pandas（见 requirements.txt）
# 数据说明：合成示例数据，模拟一批轴的检验记录
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler, OneHotEncoder

# 示例数据：三根轴的振动幅值（mm/s）与直径（mm）——量纲完全不同
df = pd.DataFrame({
    "轴号": ["轴-01", "轴-02", "轴-03"],
    "振动幅值": [2.1, 5.8, 3.4],       # mm/s
    "直径": [40, 25, 50],              # mm
    "材料": ["45钢", "Q235", "304不锈钢"],
})

# 归一化：把不同量纲的特征拉到同一尺度（均值 0、标准差 1）
scaler = StandardScaler()
scaled = scaler.fit_transform(df[["振动幅值", "直径"]])
print("归一化后（振动幅值、直径都在 0 附近波动）：")
print(np.round(scaled, 3))

# 独热编码：材料是类别，不能当数字比大小，转成 0/1 列
enc = OneHotEncoder(sparse_output=False)
mat = enc.fit_transform(df[["材料"]])
print("\n独热编码后（材料 → 三列 0/1）：")
print(pd.DataFrame(mat, columns=enc.get_feature_names_out(["材料"])))
