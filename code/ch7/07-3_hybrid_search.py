# -*- coding: utf-8 -*-
"""
07-3 关键词检索 vs 向量检索 vs 混合检索
------------------------------------------------
三种检索方式在同一批手册段落上对比：
- 关键词检索（简化 BM25：字面命中 + 稀有度加权）：专有名词/编号不丢
- 向量检索（相邻二字特征 + 余弦相似度）：意思相近就能召回
- 混合检索 = 两者得分加权合并，取长补短
运行：python 07-3_hybrid_search.py
"""
import numpy as np

# ---------- 语料：四段手册文本 ----------
CHUNKS = [
    "【日常维护】每天开机前检查润滑油液位，低于下限时补充。",
    "【常见故障】故障代码 E01 表示主轴润滑不足，应立即停机检查油路。",
    "【润滑系统】润滑泵压力应保持在 2.5 兆帕，压力不足时检查滤芯。",
    "【轴承更换】主轴轴承建议每运行 2000 小时更换一次。",
]

# ---------- 特征工具 ----------
def bigrams(text):
    out = {}
    for i in range(len(text) - 1):
        g = text[i:i + 2]
        out[g] = out.get(g, 0) + 1
    return out

vocab = {}
for c in CHUNKS:
    for g in bigrams(c):
        if g not in vocab:
            vocab[g] = len(vocab)

def to_vector(text):
    vec = np.zeros(len(vocab), dtype=float)
    for g, cnt in bigrams(text).items():
        if g in vocab:
            vec[vocab[g]] = cnt
    return vec

def cosine(a, b):
    denom = np.linalg.norm(a) * np.linalg.norm(b)
    return float(np.dot(a, b) / denom) if denom else 0.0

# 简化 BM25：bigram 词频 × 逆文档频率（越稀有权重越高）
import math
N = len(CHUNKS)
idf = {}
for g in vocab:
    df = sum(1 for c in CHUNKS if g in bigrams(c))
    idf[g] = math.log((N + 1) / (df + 1)) + 1

def keyword_score(text, query_bigrams):
    """关键词得分 = 命中 bigram 的权重之和"""
    tb = bigrams(text)
    return sum(idf[g] for g in query_bigrams if g in tb)

def hybrid_score(kw, vec, w=0.5):
    """混合得分：关键词与向量分数各自归一化后加权"""
    return w * kw + (1 - w) * vec

def evaluate(query):
    qv = to_vector(query)
    qbg = list(bigrams(query).keys())
    print(f"\n查询：“{query}”")
    kw_scores = [(i, keyword_score(c, qbg)) for i, c in enumerate(CHUNKS)]
    vec_scores = [(i, cosine(qv, to_vector(c))) for i, c in enumerate(CHUNKS)]
    kw_max = max(s for _, s in kw_scores) or 1
    vec_max = max(s for _, s in vec_scores) or 1
    hy_scores = [(i, hybrid_score(kw_scores[i][1] / kw_max, vec_scores[i][1] / vec_max))
                 for i in range(len(CHUNKS))]
    best_kw = max(kw_scores, key=lambda x: x[1])[0]
    best_vec = max(vec_scores, key=lambda x: x[1])[0]
    best_hy = max(hy_scores, key=lambda x: x[1])[0]
    print("   段落    关键词分   向量相似度   混合分   最佳来源")
    for i in range(len(CHUNKS)):
        print(f"   段{i + 1}   {kw_scores[i][1]:6.2f}   {vec_scores[i][1]:7.3f}   {hy_scores[i][1]:.3f}   {CHUNKS[i][:14]}...")
    print(f"   → 关键词最佳：段{best_kw + 1}  向量最佳：段{best_vec + 1}  混合最佳：段{best_hy + 1}")
    return best_kw, best_vec, best_hy

# ---------- 两个典型查询 ----------
print("=" * 64)
print("场景一：查询里带编号（专有名词）——关键词检索占优")
r1 = evaluate("故障代码 E01 怎么处理")
print("\n场景二：查询用口语、不含编号（意思相近）——向量检索占优")
r2 = evaluate("润滑系统压力不够怎么办")

print("\n" + "=" * 64)
print("小结：混合检索综合两者，两种场景下都不会落到最差结果。")
