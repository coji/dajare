---
name: dajare-spinner
description: Claude Codeのスピナー（spinner、処理中表示）にランダムなダジャレを設定する dajare-spinner スキル。作業中にダジャレが流れてきて楽しくなる。
license: MIT
---

# dajare-spinner

Claude Code の処理中スピナーにダジャレを表示するスキル。ダジャレデータは [@mattn](https://github.com/mattn) さん提供の [ダジャレ API](https://dajare-api.compile-error.net/api) を利用しています。

- 初回: このスキルをトリガーしてダジャレを設定（opt-in）
- 以降: セッション開始時に自動で6時間ごとにリフレッシュ（plugin hook）

## 実行手順

このスキルがトリガーされたら、以下を実行してください：

### 1. ダジャレを取得して spinnerVerbs に設定

以下のコマンドを実行してください：

```bash
bash "${CLAUDE_PLUGIN_ROOT:-$(dirname "$0")}/scripts/update-spinner.sh" 30
```

第1引数で取得件数を指定できます（デフォルト30件）。

### 2. 完了メッセージ

設定が完了したら、以下のように報告してください：

> スピナーにダジャレを設定しました！次の処理から表示されます。
> 以降はセッション開始時に自動で更新されます（6時間ごと）。
> 無効にするには settings.json から spinnerVerbs を削除してください。

### オプション: セッション文脈からの動的生成

ユーザーが「セッションの内容からダジャレ作って」等と言った場合は、
直近の会話で出てきたキーワードを拾い、そこからダジャレを生成して
`spinnerVerbs` に追加してください。

手順：
1. 直近の会話からキーワードを3〜5個抽出
2. 各キーワードでダジャレを1つずつ生成（dajare スキルの手法を使う）
3. 生成したダジャレを `~/.claude/settings.json` の `spinnerVerbs.verbs` に追加
