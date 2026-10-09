# -*- coding: utf-8 -*-
"""
07-2 纯 Python 走一遍 RAG 五步
------------------------------------------------
不依赖任何框架，把 RAG 五步讲透明：
  ① 切分  长手册切成小段
  ② 向量化  每段变成向量（简化版：相邻二字特征）
  ③ 检索  问题变向量，找最相近的 Top-K 段
  ④ 简化重排  用"查询词命中数"给结果二次排序
  ⑤ 生成  把"问题 + 检索到的原文"拼成给大模型的提示词
运行：python 07-2_rag_five_steps.py
"""
import numpy as np

# ---------- 示例设备手册（模拟几页手册内容，按空行分段） ----------
MANUAL = """【概述】本手册适用于 XYZ-2000 型数控机床的日常维护与常见故障处理。操作人员应在上岗前接受培训，并严格遵守本手册规定。
【日常维护】每天开机前检查润滑油液位，低于下限时补充。每周清洁主轴锥孔与刀库。每月检查皮带张紧度与电气接线。
【常见故障】故障代码 E01 表示主轴润滑不足，应立即停机检查油路。故障代码 E02 表示冷却液温度过高，需检查冷却泵与液位。
【安全操作】维修前必须切断电源并悬挂检修牌。禁止在机床运行时用手清理铁屑，必须使用专用工具。
【轴承更换】主轴轴承建议每运行 2000 小时更换一次。更换时注意清洁轴颈，使用指定型号 6205 轴承，并按规定扭矩锁紧。"""

# ① 切分：按行切段（每行一段，模拟按章节/段落切分）
def chunk_by_paragraph(text):
    return [p.strip() for p in text.split("\n") if p.strip()]

chunks = chunk_by_paragraph(MANUAL)
print(f"① 切分：{len(chunks)} 段")
for i, c in enumerate(chunks):
    print(f"   段{i + 1}：{c[:22]}...")

# ② 向量化：每段转成"相邻二字"词频向量（简化词向量）
def bigrams(text):
    out = {}
    for i in range(len(text) - 1):
        g = text[i:i + 2]
        out[g] = out.get(g, 0) + 1
    return out

vocab = {}
for c in chunks:
    for g in bigrams(c):
        if g not in vocab:
            vocab[g] = len(vocab)

def to_vector(text):
    vec = np.zeros(len(vocab), dtype=float)
    for g, cnt in bigrams(text).items():
        if g in vocab:
            vec[vocab[g]] = cnt
    return vec

chunk_vecs = np.array([to_vector(c) for c in chunks])
print(f"\n② 向量化：词表 {len(vocab)} 个特征，5 段手册 → {chunk_vecs.shape[0]}×{chunk_vecs.shape[1]} 向量矩阵")

# ③ 检索：问题变向量，余弦相似度找 Top-K
def cosine(a, b):
    denom = np.linalg.norm(a) * np.linalg.norm(b)
    return float(np.dot(a, b) / denom) if denom else 0.0

query = "主轴轴承多久更换一次"
qv = to_vector(query)
scores = [(i, cosine(qv, chunk_vecs[i])) for i in range(len(chunks))]
scores.sort(key=lambda x: -x[1])
top_k = scores[:3]
print(f"\n③ 检索：问题“{query}” 的 Top-3 召回：")
for i, sc in top_k:
    print(f"   段{i + 1}  相似度 {sc:.3f}  {chunks[i][:26]}...")

# ④ 简化重排：用"查询词命中数"二次打分（真实重排由模型完成，这里用关键词计数演示两段式思想）
def keyword_hits(chunk, query_words):
    return sum(1 for w in query_words if w in chunk)

qw = [w for w in ["轴承", "更换", "主轴", "小时"] if w]  # 手工拆出的查询关键词
for i, _ in top_k:
    hits = keyword_hits(chunks[i], qw)
    print(f"   段{i + 1} 查询词命中 {hits}/4 → 重排分 {hits}")
reranked = sorted(top_k, key=lambda x: keyword_hits(chunks[x[0]], qw), reverse=True)
best_i = reranked[0][0]
print(f"   重排后最佳：段{best_i + 1}（{chunks[best_i][:26]}...）")

# ⑤ 生成：拼装提示词（真实项目中这里才调用大模型）
prompt = f"""你是一个设备维护助手。请只根据下面资料回答问题，资料里没有的信息就说"资料中没有提到"。

【资料】
{chunks[best_i]}

【问题】{query}
【要求】先给出答案，再注明依据来自哪一段资料。"""
print(f"\n⑤ 生成：拼装好的提示词（交给大模型）——\n{prompt}")
