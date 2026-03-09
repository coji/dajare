#!/bin/sh
# skills/ 配下のスキルを .skill ファイル (zip) にパッケージングする
# Usage: scripts/package-skill.sh [output-dir]
#
# .skill ファイルは zip 形式で、展開すると <skill-name>/SKILL.md ... という構造になる。
# skills/ 内の SKILL.md を持つ各ディレクトリを個別にパッケージングする。

set -eu

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUTPUT_DIR="${1:-.}"

mkdir -p "$OUTPUT_DIR"
OUTPUT_DIR="$(cd "$OUTPUT_DIR" && pwd)"

cd "$REPO_ROOT/skills"

for skill_dir in */; do
  skill_name="${skill_dir%/}"
  if [ -f "$skill_dir/SKILL.md" ]; then
    SKILL_FILE="$OUTPUT_DIR/${skill_name}.skill"
    rm -f "$SKILL_FILE"
    zip -r "$SKILL_FILE" "$skill_dir" \
      -x "${skill_name}/__pycache__/*" \
      -x "${skill_name}/*.pyc" \
      -x "${skill_name}/.DS_Store" \
      -x "${skill_name}/evals/*"
    echo "Packaged: $SKILL_FILE"
  fi
done
