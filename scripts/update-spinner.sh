#!/usr/bin/env bash
# ダジャレAPIからランダムにダジャレを取得して
# ~/.claude/settings.json の spinnerVerbs に設定するスクリプト
set -euo pipefail

COUNT="${1:-30}"
API_URL="https://dajare-api.compile-error.net/api"
SETTINGS="$HOME/.claude/settings.json"

# settings.json がなければ作る
if [ ! -f "$SETTINGS" ]; then
  echo '{}' > "$SETTINGS"
fi

echo "ダジャレを ${COUNT} 件取得中..."

# 並列でAPIを叩いてダジャレを収集
dajare_list=()
for i in $(seq 1 "$COUNT"); do
  text=$(curl -sf "$API_URL" | python3 -c "import sys,json; print(json.load(sys.stdin)['text'])" 2>/dev/null) || continue
  # スピナー表示用に長すぎるものはスキップ (80文字以内)
  if [ "${#text}" -le 80 ]; then
    dajare_list+=("$text")
  fi
done

echo "${#dajare_list[@]} 件取得完了"

# JSON配列に変換して settings.json に書き込む
python3 - "$SETTINGS" "${dajare_list[@]}" <<'PYTHON'
import sys, json

settings_path = sys.argv[1]
verbs = list(sys.argv[2:])

with open(settings_path, "r") as f:
    settings = json.load(f)

settings["spinnerVerbs"] = {"mode": "replace", "verbs": verbs}

with open(settings_path, "w") as f:
    json.dump(settings, f, ensure_ascii=False, indent=2)
    f.write("\n")

print(f"spinnerVerbs を {len(verbs)} 件に更新しました: {settings_path}")
PYTHON
