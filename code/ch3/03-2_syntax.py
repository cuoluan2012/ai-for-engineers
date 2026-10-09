# 用途：第 3 章 3.2 节示例——变量、容器、循环与判断
# 运行前：无需安装任何额外库（Python 3.10+）
# 场景：老张对 6 根轴做直径公差检验。名义直径 40 mm，公差 ±0.05 mm。

# ---------- 一、变量与数据类型：给数据贴标签 ----------
diameters = [40.02, 40.01, 39.97, 40.05, 40.08, 39.95]  # 实测直径，单位 mm
nominal = 40.0      # 名义直径（浮点数 float）
tol = 0.05          # 公差（浮点数 float）
axis_name = "轴-01"  # 文本（字符串 str）

print(f"变量 axis_name 的类型：{type(axis_name).__name__}，值：{axis_name}")
print(f"变量 nominal 的类型：{type(nominal).__name__}，值：{nominal}")

# ---------- 二、字典：像查图册目录一样按名称取值 ----------
axis = {"轴号": "轴-01", "材料": "45钢", "直径": 40, "热处理": "调质"}
print(axis["材料"])       # 按键取值
axis["表面处理"] = "镀铬"   # 追加一项
print(axis)

# ---------- 三、循环 + 判断：逐根检验 ----------
for i, d in enumerate(diameters, 1):
    ok = abs(d - nominal) <= tol
    status = "合格" if ok else "超差"
    print(f"第{i}根轴：实测 {d:.2f} mm，偏差 {d - nominal:+.2f} mm → {status}")
