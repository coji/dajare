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
| `SKILL.md` (ルート) | スキル本体（オーケストレーター）。`npx skills add` で発見される | **ここだけ編集する** |
| `references/*.md` (ルート) | 段階的開示用の詳細ドキュメント（正） | **ここだけ編集する** |
| `scripts/rhyme.py` | 読み変換・母音列抽出スクリプト（正） | PEP 723 依存、`uv run` で実行 |
| `skills/dajare/SKILL.md` | `/plugin install` 用コピー | **編集禁止**（hook が自動同期） |
| `skills/dajare/references/*.md` | プラグイン用 references コピー | **編集禁止**（hook が自動同期） |
| `skills/dajare/scripts/rhyme.py` | プラグイン用 rhyme.py コピー | **編集禁止**（hook が自動同期） |
| `AGENTS.md` | openskills / Cursor 等クロスエージェント対応 | description を変えたら SKILL.md の frontmatter と揃える |
| `.claude-plugin/plugin.json` | Claude Code プラグインマニフェスト | バージョン更新時に編集 |
| `.claude-plugin/marketplace.json` | Claude Code マーケットプレイスカタログ | バージョン更新時に plugin.json と揃える |
| `README.md` | インストール手順・使い方 | 機能追加時に更新 |
| `scripts/package-skill.sh` | .skill パッケージング | `skills/dajare/` を zip して配布用 `.skill` を生成 |
| `.github/workflows/release.yml` | GitHub Release 時の自動ビルド | Release publish で `dajare.skill` を asset に添付 |

### description の同期

SKILL.md の frontmatter `description` を変更したら、以下も同じ内容に揃えること：

1. `AGENTS.md` の `<description>` タグ内
2. `.claude-plugin/plugin.json` の `description` フィールド（こちらは短縮版でもOK）
3. `.claude-plugin/marketplace.json` の plugins[0].description
4. `README.md` の冒頭説明

## 設計方針：Progressive Disclosure（段階的開示）

SKILL.md はオーケストレーター（フロー制御）に徹し、詳細な知識は references/ に分離している。

| 層 | 内容 | 読み込みタイミング |
|---|---|---|
| Level 1 | name + description (~100トークン) | 常にシステムプロンプトに注入 |
| Level 2 | SKILL.md 本体 (~120行) | スキルがトリガーされた時 |
| Level 3 | references/, scripts/ | 生成フロー中に必要に応じて |

references/ のファイル：
- `humor-theory.md` — 面白さの3層構造（音・意味・文脈）
- `generation-guide.md` — 生成ステップの詳細手法・検証手順・バリエーション定義
- `examples.md` — 思考プロセス付き生成例
- `bad-examples.md` — LLM が陥りやすい失敗パターン

## 配布チャネル

4つのインストール方法に対応している：

- `npx skills add coji/dajare` — ルートの SKILL.md を使用
- `npx openskills install coji/dajare` — AGENTS.md を使用
- `/plugin marketplace add coji/dajare` → `/plugin install dajare@dajare` — .claude-plugin/ + skills/ を使用
- GitHub Releases の `dajare.skill` — Cowork で「Copy to your skills」からインストール

### バージョン管理

`plugin.json` と `marketplace.json` の `version` は常に揃えること。バンプの目安：

- **patch**（x.x.+1）：バグ修正、パス修正、ドキュメント修正
- **minor**（x.+1.0）：新機能追加（例：`--style` オプション追加）
- **major**（+1.0.0）：破壊的変更

## リリース手順

1. ルートの `SKILL.md` を編集
2. 必要なら `AGENTS.md`, `plugin.json`, `README.md` の description を同期
3. `plugin.json` と `marketplace.json` の `version` をバンプ（両方揃える）
4. commit（pre-commit hook が `SKILL.md`、`references/*.md`、`scripts/rhyme.py` を skills/ に自動同期）
5. push
6. GitHub で Release を作成（タグ例: `v1.3.0`）→ Actions が `dajare.skill` を自動ビルドして release asset に添付
