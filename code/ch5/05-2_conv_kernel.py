# -*- coding: utf-8 -*-
"""
05-2 用 NumPy 手动做一次卷积：让机器"看"出边缘
------------------------------------------------
一张 8×8 的小图（0~1 灰度，模拟零件表面），中间有一条竖直亮线。
用一个 3×3 的"边缘检测核"扫过全图，竖线处响应最强；
再做一次 2×2 最大池化，把图缩小一半。
运行：python 05-2_conv_kernel.py
"""
import numpy as np

# 1) 造一张 8×8 的"零件表面图"：背景 0.4，第 5 列一条竖线 0.9，一个亮点 0.9
img = np.full((8, 8), 0.4)
img[:, 4] = 0.9      # 竖直亮线（模拟划痕）
img[2, 2] = 0.9      # 一个小亮点（模拟点状缺陷）

# 2) 3×3 边缘检测核（Sobel 竖边缘）：左右两侧差得越多，响应越强
kernel = np.array([
    [-1, 0, 1],
    [-2, 0, 2],
    [-1, 0, 1],
])

# 3) 卷积：核在图上滑过，每个位置做"逐元素相乘再求和"
h, w = img.shape
out = np.zeros((h - 2, w - 2))
for i in range(h - 2):
    for j in range(w - 2):
        patch = img[i:i + 3, j:j + 3]      # 取 3×3 小窗口
        out[i, j] = (patch * kernel).sum()

# 4) 2×2 最大池化：每 2×2 块取最大值，图缩小一半
pool = np.zeros((3, 3))
for i in range(3):
    for j in range(3):
        pool[i, j] = img[i * 2:i * 2 + 2, j * 2:j * 2 + 2].max()

np.set_printoptions(precision=2, suppress=True)
print("原始图（8×8，0~1 灰度）：")
print(img)
print("\n卷积后（6×6）：竖线所在列响应最强（数值大），背景响应接近 0：")
print(out)
print("\n池化后（3×3）：每块取最大灰度，图缩小一半：")
print(pool)
