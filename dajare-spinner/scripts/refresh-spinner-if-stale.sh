#!/usr/bin/env bash
# spinnerVerbs が一定時間以上古ければバックグラウンドで更新する
# hooks から呼ばれることを想定（即座にreturnしてブロックしない）
set -euo pipefail

SETTINGS="$HOME/.claude/settings.json"
STAMP_FILE="$HOME/.claude/.dajare-spinner-updated"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# 更新間隔（秒）: デフォルト6時間
INTERVAL="${DAJARE_SPINNER_INTERVAL:-21600}"

# opt-in チェック: spinnerVerbs が設定されていなければ何もしない
if [ ! -f "$SETTINGS" ] || ! python3 -c "
import json, sys
d = json.load(open('$SETTINGS'))
sv = d.get('spinnerVerbs', {})
if not isinstance(sv, dict) or not sv.get('verbs'):
    sys.exit(1)
" 2>/dev/null; then
  exit 0
fi

# タイムスタンプファイルがなければ即更新
if [ ! -f "$STAMP_FILE" ]; then
  touch "$STAMP_FILE"
  nohup bash "$SCRIPT_DIR/update-spinner.sh" 30 > /dev/null 2>&1 &
  exit 0
fi

# 前回更新からの経過秒数を計算
if [[ "$OSTYPE" == darwin* ]]; then
  last_updated=$(stat -f %m "$STAMP_FILE")
else
  last_updated=$(stat -c %Y "$STAMP_FILE")
fi
now=$(date +%s)
elapsed=$((now - last_updated))

if [ "$elapsed" -ge "$INTERVAL" ]; then
  touch "$STAMP_FILE"
  nohup bash "$SCRIPT_DIR/update-spinner.sh" 30 > /dev/null 2>&1 &
fi
