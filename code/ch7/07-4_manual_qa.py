# -*- coding: utf-8 -*-
"""
07-4 配套项目：企业设备手册问答机器人（简化版）
------------------------------------------------
完整走一遍 RAG 五步，落在真实项目上：
  ① 程序生成一份示例设备手册（8 段章节化内容）
  ② 每段用 embedding 模型转成向量入库（优先 BGE 中文小模型，
     加载失败自动降级为相邻二字向量，保证零依赖也能跑）
  ③ 把问题转成向量，检索最相近的 Top-3
  ④ 构建提示词，走 OpenAI 兼容 API（无 Key 时打印请求结构，不假生成）
  ⑤ 用 30 条评测问题给出检索命中率报告

运行：python 07-4_manual_qa.py
"""
import os
import logging
import numpy as np

# 模型加载进度条是 stderr 噪音，屏蔽后输出更清爽
logging.getLogger("sentence_transformers").setLevel(logging.ERROR)

# ---------- ① 示例设备手册（程序生成，零下载依赖） ----------
MANUAL = [
    "【概述】本手册适用于 XYZ-2000 型数控机床。操作人员上岗前应接受培训并熟悉本手册。",
    "【日常维护】每天开机前检查润滑油液位，低于下限时补充；每周清洁主轴锥孔与刀库；每月检查皮带张紧度与电气接线。",
    "【常见故障】故障代码 E01 表示主轴润滑不足，立即停机检查油路；E02 表示冷却液温度过高，检查冷却泵与液位。",
    "【安全操作】维修前必须断电并悬挂检修牌；机床运行中禁止用手清理铁屑，须用专用工具；换刀必须在停机状态下进行。",
    "【轴承更换】主轴轴承建议每运行 2000 小时更换；使用 6205 轴承；安装前清洁轴颈，按 45 牛米扭矩锁紧。",
    "【润滑系统】润滑泵压力保持 2.5 兆帕；压力不足先检查滤芯，滤芯每半年更换一次。",
    "【冷却系统】冷却液浓度保持 5% 到 8%，液位低于一半时补充；温度过高检查冷却泵。",
    "【保养周期】日检：油位、气压、清洁；周检：锥孔、刀库、皮带；月检：接线、滤芯；年检：主轴精度与整机大修。",
]
CHUNK_TITLES = ["概述", "日常维护", "常见故障", "安全操作", "轴承更换", "润滑系统", "冷却系统", "保养周期"]

# ---------- ② embedding：真实模型优先，降级相邻二字向量 ----------
def make_embedder():
    os.environ.setdefault("HF_HUB_DISABLE_PROGRESS_BARS", "1")  # 关掉下载/加载进度条
    try:
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer("BAAI/bge-small-zh-v1.5")
        print("已加载语义模型：BAAI/bge-small-zh-v1.5（512 维，语义检索）")
        return lambda texts: model.encode(texts, normalize_embeddings=True)
    except Exception as e:
        print(f"语义模型不可用（{type(e).__name__}），降级为相邻二字向量。")
        return make_bigram_embedder()

def make_bigram_embedder():
    def bigrams(text):
        return [text[i:i + 2] for i in range(len(text) - 1)]
    vocab = {}
    for c in MANUAL:
        for g in bigrams(c):
            vocab.setdefault(g, len(vocab))
    def encode(texts, **kw):
        out = np.zeros((len(texts), len(vocab)), dtype=float)
        for i, t in enumerate(texts):
            for g in bigrams(t):
                if g in vocab:
                    out[i, vocab[g]] += 1
        return out
    return encode

embed = make_embedder()
vecs = embed(MANUAL)                       # 每段一个向量
print(f"手册 {len(MANUAL)} 段 → 向量矩阵 {vecs.shape[0]}×{vecs.shape[1]}")

# ---------- ③ 检索 ----------
def retrieve(query, top_k=3):
    qv = embed([query])[0]
    sims = np.dot(vecs, qv)                # 归一化后点积 = 余弦相似度
    order = np.argsort(-sims)[:top_k]
    return [(int(i), float(sims[i])) for i in order]

# ---------- ⑤ 生成：构建提示词 + OpenAI 兼容请求（无 Key 不假生成） ----------
def build_prompt(query, hits):
    parts = [f"【资料段{idx + 1}】{MANUAL[idx]}" for idx, _ in hits]
    return (
        "你是一名设备维护助手。请只根据下面资料回答问题，"
        "资料里没有的信息请回答“资料中没有提到”，并注明依据来自第几段资料。\n\n"
        + "\n".join(parts)
        + f"\n\n【问题】{query}"
    )

def call_llm(prompt):
    key = os.environ.get("LLM_API_KEY", "")
    if not key:
        return None
    # OpenAI 兼容格式；不同供应商仅 base_url 不同
    import requests
    resp = requests.post(
        os.environ.get("LLM_BASE_URL", "https://api.example.com/v1/chat/completions"),
        headers={"Authorization": f"Bearer {key}"},
        json={"model": os.environ.get("LLM_MODEL", "gpt-4o-mini"),
              "messages": [{"role": "user", "content": prompt}], "temperature": 0.2},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]

# ---------- ④ 一个示例问答 ----------
query = "主轴轴承多久更换一次"
hits = retrieve(query)
print("\n示例问答")
print(f"问题：{query}")
print(f"检索 Top-3：{[(f'段{i + 1}({CHUNK_TITLES[i]})', round(s, 3)) for i, s in hits]}")
prompt = build_prompt(query, hits)
answer = call_llm(prompt)
if answer:
    print(f"模型回答：{answer}")
else:
    print("未配置 LLM_API_KEY：跳过真实生成，已构建好提示词（见下）。")
    print("（真实项目中，这段提示词会发给大模型，得到带出处的答案）")
    print("提示词预览：", prompt[:110], "...")

# ---------- ⑥ 30 条评测：检索命中率报告 ----------
EVAL = [
    # (问题, 期望段落索引)
    ("这台机床的型号是什么", 0),
    ("操作人员上岗前要做什么", 0),
    ("每天开机前要检查什么", 1),
    ("润滑油液位低了怎么办", 1),
    ("主轴锥孔多久清洁一次", 1),
    ("皮带松了怎么处理", 1),
    ("故障代码 E01 是什么意思", 2),
    ("主轴润滑不足怎么办", 2),
    ("冷却液温度过高是什么故障", 2),
    ("维修前必须先做什么", 3),
    ("能在机床运行时清理铁屑吗", 3),
    ("检修牌什么时候挂", 3),
    ("主轴轴承多久更换一次", 4),
    ("更换轴承用什么型号", 4),
    ("轴承安装要注意什么", 4),
    ("轴承锁紧扭矩是多少", 4),
    ("润滑泵压力标准是多少", 5),
    ("压力不足先查什么", 5),
    ("滤芯多久更换一次", 5),
    ("冷却液浓度多少合适", 6),
    ("冷却液液位低了会怎样", 6),
    ("设备多久做一次年检", 7),
    ("周检要检查哪些项目", 7),
    ("日检内容有哪些", 7),
    ("月检和年检有什么区别", 7),
    ("机床开着的时候能直接换刀吗", 3),
    ("主轴声音变大可能是什么问题", 4),
    ("换了新滤芯还是压力不足怎么办", 5),
    ("加工精度突然变差先检查哪里", 4),
    ("整机大修几年一次", 7),
]
print(f"\n评测：{len(EVAL)} 条问题")
top1, top3 = 0, 0
miss = []
for q, target in EVAL:
    hits = retrieve(q, top_k=3)
    ids = [i for i, _ in hits]
    if ids[0] == target:
        top1 += 1
    if target in ids:
        top3 += 1
    else:
        miss.append((q, target))
print(f"Top-1 命中率：{top1}/{len(EVAL)} = {top1 / len(EVAL):.1%}")
print(f"Top-3 命中率：{top3}/{len(EVAL)} = {top3 / len(EVAL):.1%}")
if miss:
    print(f"未命中 {len(miss)} 条（Top-3 之外）：")
    for q, t in miss:
        print(f"  问题“{q}” 期望段{t + 1}（{CHUNK_TITLES[t]}）")
else:
    print("全部问题 Top-3 命中。")
