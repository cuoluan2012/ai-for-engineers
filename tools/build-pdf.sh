#!/usr/bin/env bash
# ============================================================
# 《从工程师到 AI 工程师》PDF 构建脚本
# 把 docs/ 下的章节 Markdown 用 pandoc + tectonic 编译为中文 PDF。
#
# 依赖（本机已验证路径）：
#   pandoc 3.12.1（arm64）：/opt/anaconda3/bin/pandoc
#   tectonic 0.15.0      ：/opt/anaconda3/bin/tectonic
# 安装来源：conda install -c conda-forge pandoc tectonic（清华镜像）
#
# 用法：
#   ./tools/build-pdf.sh                 # 输出全部章节到 ai-for-engineers/artifacts/
#   ./tools/build-pdf.sh /tmp/out        # 指定输出目录
#   PANDOC=/path/to/pandoc ./tools/build-pdf.sh   # 覆盖工具路径
# ============================================================
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PANDOC="${PANDOC:-/opt/anaconda3/bin/pandoc}"
TECTONIC="${TECTONIC:-/opt/anaconda3/bin/tectonic}"
OUT_DIR="${1:-$REPO_ROOT/artifacts}"

if [ ! -x "$PANDOC" ]; then
  echo "错误：找不到 pandoc（$PANDOC）。请先安装或设置 PANDOC 环境变量。" >&2
  exit 1
fi
if [ ! -x "$TECTONIC" ]; then
  echo "错误：找不到 tectonic（$TECTONIC）。请先安装或设置 TECTONIC 环境变量。" >&2
  exit 1
fi

mkdir -p "$OUT_DIR"
cd "$REPO_ROOT/docs"

# 中文排版参数：CJK 主字体用系统中文字体；页边距 2cm；链接着色
COMMON_ARGS=(
  --pdf-engine="$TECTONIC"
  -V CJKmainfont="PingFang SC"
  -V geometry:margin=2cm
  -V colorlinks=true
)

for f in ch*.md; do
  [ -f "$f" ] || continue
  name="${f%.md}"
  echo ">> 编译 $f ..."
  "$PANDOC" "$f" -o "$OUT_DIR/$name.pdf" "${COMMON_ARGS[@]}"
  echo "   → $OUT_DIR/$name.pdf"
done

echo "全部完成。输出目录：$OUT_DIR"
