<div align="center">

# AI for Engineers

**从工程师到 AI 工程师 —— 理工科零基础学习指南**

一套为"有工作经验、零计算机背景"的理工科工程师准备的开源学习资料。
面向机械、电气、化工、土木……每一位想用 AI 赋能本专业的工程师。

<p>
<a href="https://github.com/cuoluan2012/ai-for-engineers/blob/main/LICENSE"><img src="https://img.shields.io/badge/License-CC_BY_NC_SA_4.0-4ecdc4?style=for-the-badge&logo=creative-commons&logoColor=white&labelColor=1a1a2e" alt="License"></a>
<a href="https://cuoluan2012.github.io/ai-for-engineers/"><img src="https://img.shields.io/badge/Online-Docs-2b6cb0?style=for-the-badge&logo=readthedocs&logoColor=white&labelColor=1a1a2e" alt="Online Docs"></a>
<a href="https://github.com/cuoluan2012/ai-for-engineers/releases"><img src="https://img.shields.io/badge/PDF-Download-ff7d00?style=for-the-badge&logo=adobeacrobatreader&logoColor=white&labelColor=1a1a2e" alt="PDF"></a>
</p>

**🔖 当前状态：全书 11 章 + 附录术语表已完成（v1.0 · 234 条术语）**

</div>

---

## 为什么会有这套资料

市面上的 AI 学习资料大多面向**有计算机基础的科班生**：默认你会命令行、懂数据库、见过微服务。

但现实中大量工程师是这样的：

> 我干了十几年机械设计，画图、算强度、管产线都在行。可让我面对"命令行""API""Docker"这些词，就像让一个老钳工直接去看整条自动化产线的控制代码——每个字都认识，连起来不知道在说什么。

这套资料的目标，就是**填补这条鸿沟**：从"什么是命令行"讲起，一步一步，讲到你能自己搭一个 AI 应用、读懂一张架构图、把 AI 用回你的专业里。

作者本人就是一位从业十余年的机械工程师，2023 年起从 Python 零基础自学 AI，本资料是**完整学习经历的结构化沉淀**。

## 本书适合谁

- ✅ 从业 3 年以上的理工科工程师（机械 / 电气 / 化工 / 土木 / 工艺……）
- ✅ 完全零编程基础，但想用 AI 赋能本专业的工程师
- ✅ 有产品 / 项目管理经验、想理解 AI 工程化的技术负责人
- ❌ 计算机科班出身、想找进阶技术文档的读者（你会觉得太基础）

## 学习路径地图

<div align="center">
<img src="figures/learning-map.png" alt="学习路径地图：从工程师到 AI 工程师" width="90%" style="border-radius: 10px; box-shadow: 0 8px 20px rgba(45,55,72,0.3);" />
</div>

**怎么读这本书**（三批写作顺序，也即推荐阅读顺序）：

| 批次 | 章节 | 读完你能做什么 |
|---|---|---|
| 第一批：地基 | 第 1–2 章 | 建立计算机素养，看懂 AI 世界的底层语言 |
| 第二批：AI 核心 | 第 3–6 章 | 自己跑通 Python、机器学习、深度学习示例 |
| 第三批：工程落地 | 第 7–11 章 | 搭 RAG 知识库、智能体，看懂工业 AI 落地 |

## 内容目录

| 章节 | 核心内容 | 状态 |
|---|---|---|
| 第 1 章 为什么工程师要拥抱 AI | 产业趋势、学习路径、用 AI 学 AI | ✅ 已完成 |
| 第 2 章 计算机通识：学 AI 前必懂的基础课 | 硬件/CPU/GPU、Linux、服务器与网络、前端后端、UI/UX、数据库、架构、Docker/K8s、部署、软件工程 | ✅ 已完成 |
| 第 3 章 编程第一课：像搭积木一样学 Python | 变量、容器、控制流、函数、虚拟环境 | ✅ 已完成 |
| 第 4 章 机器学习：让机器从数据里找规律 | 经典算法、模型评估、特征工程 | ✅ 已完成 |
| 第 5 章 深度学习与神经网络 | 神经网络、CNN/RNN、PyTorch 起步 | ✅ 已完成 |
| 第 6 章 大语言模型与提示词 | Token、Transformer、提示工程 | ✅ 已完成 |
| 第 7 章 RAG 知识库 | Embedding、向量数据库、企业标准/图纸问答 | ✅ 已完成 |
| 第 8 章 AI 智能体：从"问答"到"干活" | Agent、工具调用、多智能体 | ✅ 已完成 |
| 第 9 章 模型微调与私有化部署 | LoRA、量化、GPU 服务器、企业防火墙内部署 | ✅ 已完成 |
| 第 10 章 工业数据与 AI 落地 | 工业数据资产、CAD/CAE/PLM 场景、数字孪生 | ✅ 已完成 |
| 第 11 章 从学到做：企业试点与个人成长 | 试点选型、ROI、工程师的 AI 转型路线 | ✅ 已完成 |
| 附录 术语表（234 条） | 全章节术语、中文译名、工程类比、所属模块 | ✅ 已完成 |

## 在线阅读与下载

- 📖 **在线文档**：<https://cuoluan2012.github.io/ai-for-engineers/>
- 📄 **PDF 下载**：在 [Releases](https://github.com/cuoluan2012/ai-for-engineers/releases) 页面下载分章 PDF（`tools/build-pdf.sh` 可本地一键生成全部章节）
- 📚 **术语表**：`glossary/` 目录（Markdown / CSV，当前 **234 条**，覆盖全书 11 章）

## 仓库结构

```
ai-for-engineers/
├── README.md          # 本文件
├── LICENSE            # CC BY-NC-SA 4.0
├── docs/              # 全书 Markdown 源（MkDocs 站点）
├── figures/           # 配图（SVG 源 + PNG 导出）
├── code/              # 示例代码（按章分目录，均真实运行过）
├── glossary/          # 术语表（Markdown / CSV / 章节覆盖矩阵）
├── artifacts/         # 分章 PDF 构建产物（通过 GitHub Releases 发布）
└── tools/             # PDF 生成等脚本
```

## 如何参与

- 🐛 **纠错**：正文或配图发现错误，欢迎提 [Issue](https://github.com/cuoluan2012/ai-for-engineers/issues)（请带章节号与原文）
- 💡 **建议**：你希望哪一章优先写完？在 Discussion 里告诉我们
- ✍️ **贡献**：写作规范、构建命令与提交流程见 [CONTRIBUTING](https://github.com/cuoluan2012/ai-for-engineers/blob/main/CONTRIBUTING.md)

## License

<a rel="license" href="http://creativecommons.org/licenses/by-nc-sa/4.0/">
<img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by-nc-sa/4.0/88x31.png" />
</a>

本作品采用 **知识共享署名-非商业性使用-相同方式共享 4.0 国际许可协议**（CC BY-NC-SA 4.0）授权。您可以自由分享、改编，但需署名、不得商用、衍生作品须以相同协议发布。
