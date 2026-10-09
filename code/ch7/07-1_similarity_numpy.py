# -*- coding: utf-8 -*-
"""
07-1 用 NumPy 手写"词频向量 + 余弦相似度"
------------------------------------------------
零依赖演示向量检索的核心机制：
1) 把句子变成向量（这里用"相邻两字"特征统计词频，是简化版词向量）；
2) 用余弦相似度量两个向量有多像；
3) 在 3 句机械句子里查"轴承磨损"，看谁最像。
运行：python 07-1_similarity_numpy.py
"""
import numpy as np

# 1) 语料：三句机械相关的句子
sentences = [
    "轴承磨损后要及时更换",          # 含"轴承""磨损"
    "机床主轴需要定期加润滑油",      # 无关句
    "更换磨损的轴承并检查间隙",      # 含"磨损""轴承"
]
query = "轴承磨损"                   # 要查的问题

# 2) 特征：相邻两字（bigram）当作"词"。例："轴承"→ 轴承、承磨、磨损
def bigrams(text):
    out = {}
    for i in range(len(text) - 1):
        g = text[i:i + 2]
        out[g] = out.get(g, 0) + 1
    return out

def to_vector(text, vocab):
    """把句子转成词频向量（长度 = 词表大小）"""
    vec = np.zeros(len(vocab), dtype=float)
    for g, c in bigrams(text).items():
        if g in vocab:
            vec[vocab[g]] = c
    return vec

# 3) 词表 = 语料里出现过的所有 bigram
vocab = {}
for s in sentences + [query]:
    for g in bigrams(s):
        if g not in vocab:
            vocab[g] = len(vocab)
print(f"词表大小（相邻二字特征数）：{len(vocab)}")

# 4) 余弦相似度：方向越一致越相似（0~1 之间）
def cosine(a, b):
    denom = np.linalg.norm(a) * np.linalg.norm(b)
    if denom == 0:
        return 0.0
    return float(np.dot(a, b) / denom)

# 5) 逐句算相似度并排序
qv = to_vector(query, vocab)
print("\n查询：“轴承磨损” 与各句的相似度：")
scores = []
for s in sentences:
    sv = to_vector(s, vocab)
    scores.append((s, cosine(qv, sv)))

for s, sc in sorted(scores, key=lambda x: -x[1]):
    print(f"  {sc:.3f}  {s}")

# 6) 取最相近的一句
best = max(scores, key=lambda x: x[1])
print(f"\n最相近的一句：{best[0]}（相似度 {best[1]:.3f}）")
