#!/bin/sh
# skills/dajare/ ディレクトリを .skill ファイル (zip) にパッケージングする
# Usage: scripts/package-skill.sh [output-dir]
#
# .skill ファイルは zip 形式で、展開すると dajare/SKILL.md ... という構造になる。
# skill-creator の package_skill.py と同等の出力を生成する。

set -eu

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SKILL_DIR="$REPO_ROOT/skills/dajare"
OUTPUT_DIR="${1:-.}"

if [ ! -f "$SKILL_DIR/SKILL.md" ]; then
  echo "Error: $SKILL_DIR/SKILL.md not found." >&2
  exit 1
fi

# 出力先を絶対パスに変換
mkdir -p "$OUTPUT_DIR"
OUTPUT_DIR="$(cd "$OUTPUT_DIR" && pwd)"

SKILL_FILE="$OUTPUT_DIR/dajare.skill"
rm -f "$SKILL_FILE"

# zip は skills/ から見た相対パス (dajare/...) をアーカイブ名にする
cd "$REPO_ROOT/skills"
zip -r "$SKILL_FILE" dajare/ \
  -x "dajare/__pycache__/*" \
  -x "dajare/*.pyc" \
  -x "dajare/.DS_Store" \
  -x "dajare/evals/*"

echo "Packaged: $SKILL_FILE"
