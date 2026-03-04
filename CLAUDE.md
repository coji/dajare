# dajare 開発ガイド

## プロジェクト概要

日本語のダジャレを生成する Agent Skill。Agent Skills オープン標準 (https://agentskills.io) に準拠。

## ファイル構成と整合性ルール

### SKILL.md の一元管理

**ルートの `SKILL.md` が唯一の正（Single Source of Truth）。**

- `skills/dajare/SKILL.md` はルートのコピー（Claude Code プラグイン用）
- SKILL.md を編集するときは **必ずルートの `SKILL.md` だけを編集する**
- `skills/dajare/SKILL.md` は直接編集しない
- pre-commit hook (`.githooks/pre-commit`) が commit 時に自動でコピーする
- clone 後は `git config core.hooksPath .githooks` を実行して hook を有効化する

### 各ファイルの役割

| ファイル | 用途 | 編集時の注意 |
|---|---|---|
| `SKILL.md` (ルート) | スキル本体。`npx skills add` で発見される | **ここだけ編集する** |
| `skills/dajare/SKILL.md` | `/plugin install` 用コピー | **編集禁止**（hook が自動同期） |
| `AGENTS.md` | openskills / Cursor 等クロスエージェント対応 | description を変えたら SKILL.md の frontmatter と揃える |
| `.claude-plugin/plugin.json` | Claude Code プラグインマニフェスト | バージョン更新時に編集 |
| `.claude-plugin/marketplace.json` | Claude Code マーケットプレイスカタログ | バージョン更新時に plugin.json と揃える |
| `README.md` | インストール手順・使い方 | 機能追加時に更新 |

### description の同期

SKILL.md の frontmatter `description` を変更したら、以下も同じ内容に揃えること：

1. `AGENTS.md` の `<description>` タグ内
2. `.claude-plugin/plugin.json` の `description` フィールド（こちらは短縮版でもOK）
3. `.claude-plugin/marketplace.json` の plugins[0].description
4. `README.md` の冒頭説明

## 配布チャネル

3つのインストール方法に対応している：

- `npx skills add coji/dajare` — ルートの SKILL.md を使用
- `npx openskills install coji/dajare` — AGENTS.md を使用
- `/plugin marketplace add coji/dajare` → `/plugin install dajare@dajare` — .claude-plugin/ + skills/ を使用

## リリース手順

1. ルートの `SKILL.md` を編集
2. 必要なら `AGENTS.md`, `plugin.json`, `README.md` の description を同期
3. `plugin.json` と `marketplace.json` の `version` をバンプ（両方揃える）
4. commit（pre-commit hook が skills/ を自動同期）
5. push
