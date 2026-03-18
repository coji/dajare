---
name: dajare-spinner
description: Claude Codeのスピナー（処理中表示）にランダムなダジャレを設定するスキル。作業中にダジャレが流れてきて楽しくなる。
triggers:
  - "スピナー"
  - "spinner"
  - "ダジャレスピナー"
  - "dajare-spinner"
---

# dajare-spinner

Claude Code の処理中スピナーにダジャレを表示するスキル。

## 実行手順

このスキルがトリガーされたら、以下を実行してください：

### 1. ダジャレを取得

以下のスクリプトで、ダジャレAPIからランダムに取得して `~/.claude/settings.json` の `spinnerVerbs` に設定します：

```bash
bash "$(dirname "$0")/scripts/update-spinner.sh" 30
```

`scripts/update-spinner.sh` の第1引数で取得件数を指定できます（デフォルト30件）。

### 2. 完了メッセージ

設定が完了したら、以下のように報告してください：

> スピナーにダジャレを設定しました！次の処理から表示されます。

### オプション: セッション文脈からの動的生成（レイヤー2）

ユーザーが「セッションの内容からダジャレ作って」等と言った場合は、
直近の会話で出てきたキーワードを拾い、そこからダジャレを生成して
`spinnerVerbs` に追加してください。

手順：
1. 直近の会話からキーワードを3〜5個抽出
2. 各キーワードでダジャレを1つずつ生成（dajare スキルの手法を使う）
3. 生成したダジャレを `~/.claude/settings.json` の `spinnerVerbs` に追加
