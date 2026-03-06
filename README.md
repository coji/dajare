# dajare

日本語のダジャレ（駄洒落）を生成する [Agent Skill](https://agentskills.io)。

単語やお題・状況を入力すると、音の類似度・意味の距離・文脈の自然さを考慮した質の高いダジャレを 3〜5 個生成します。

[Agent Skills](https://agentskills.io) オープン標準に準拠しており、Claude Code / Cursor / Codex / Gemini CLI など 40 以上のエージェントで利用できます。

## インストール

### npx skills (推奨)

```bash
# プロジェクトにインストール
npx skills add coji/dajare

# グローバルにインストール（全プロジェクトで使用）
npx skills add coji/dajare -g

# 特定のエージェントを指定
npx skills add coji/dajare --agent claude-code --agent cursor
```

### openskills

```bash
npx openskills install coji/dajare
```

### Claude Code プラグイン

```
/plugin marketplace add coji/dajare
/plugin install dajare@dajare
```

### 手動インストール

```bash
# Claude Code
cp -r dajare ~/.claude/skills/

# Cursor / その他のエージェント
cp -r dajare .agents/skills/
```

## 処理の流れ

```
┌─────────────────────────────────────────────────┐
│  ステップ1: 音の分解                              │
│  rhyme.py で元ネタの読み・母音列・子音列を取得      │
└────────────────────┬────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        ▼                        ▼
┌───────────────────┐  ┌──────────────────────┐
│ ステップ2A:        │  │ ステップ2B:            │
│ LLM が語彙から連想  │  │ rhyme.py --search で   │
│ (メインエージェント) │  │ 韻辞書4万語を検索       │
│                   │  │ (サブエージェント)      │
└────────┬──────────┘  └──────────┬───────────┘
         └────────────┬───────────┘
                      ▼
          ┌───────────────────────┐
          │  候補をマージ           │
          └───────────┬───────────┘
                      ▼
┌─────────────────────────────────────────────────┐
│  ステップ3: 文脈のある一文に仕上げる                │
└────────────────────┬────────────────────────────┘
                     ▼
┌─────────────────────────────────────────────────┐
│  ステップ4: 検証 (サブエージェントに委譲)            │
│  rhyme.py で音の照合 + bad-examples.md と照合      │
│  → 不合格があれば理由付きで返却                     │
└──────┬──────────────────────────────┬───────────┘
       │ 合格                         │ 不合格 & 3個未満
       ▼                             ▼
┌──────────────┐             ┌────────────────┐
│ ステップ5:    │             │ 改善ループ (1回) │
│ バリエーション │             │ → ステップ2-3   │
│ バランス調整  │             └────────────────┘
└──────┬───────┘
       ▼
┌─────────────────────────────────────────────────┐
│  出力: 前置き + ダジャレ3〜5個(解説付き) + 締め     │
└─────────────────────────────────────────────────┘
```

## 使い方

### 自動トリガー

「ダジャレ」「駄洒落」「おやじギャグ」「pun」などのキーワードや、「〇〇で何か面白いこと言って」のような言い回しで自動的にスキルが発動します。

### スタイル指定

`--style` オプションで語り口を切り替えられます。

```
/dajare コーヒー --style 関西弁
```

### スラッシュコマンド

```
/dajare コーヒー
/dajare 会議中の眠気
/dajare コーヒー --style 関西弁
```

### 出力例

> コーヒーで一杯やりましょう。
>
> 1. **公費でコーヒー、苦い話だ**（「こうひ（公費）」と「こーひー」の音重なり＋「苦い」がコーヒーの味と不祥事の両義。税金で飲むコーヒーの罪悪感）
> 2. **コーヒーを講評したら「こう挽いて」と返された**（「講評」「コーヒー」「挽いて」の三重掛け。カフェのマスターに一本取られる情景）

## 対応エージェント

[Agent Skills](https://agentskills.io) 標準に対応したすべてのエージェントで利用可能です：

- Claude Code
- Cursor
- OpenAI Codex
- Gemini CLI
- VS Code (GitHub Copilot)
- Windsurf
- Roo Code
- その他 30 以上

## アップデート

### npx skills

```bash
npx skills add coji/dajare
```

再度 `add` を実行すると最新版に更新されます。

### openskills

```bash
npx openskills install coji/dajare
```

### Claude Code プラグイン

```
/plugin marketplace update coji/dajare
```

自動アップデートを有効にする場合は `/plugin` → Marketplaces タブ → `coji/dajare` を選択 → auto-update を有効にしてください。

## 開発

### セットアップ

```bash
git clone https://github.com/coji/dajare.git
cd dajare
git config core.hooksPath .githooks
```

### SKILL.md の編集

**ルートの `SKILL.md` だけを編集してください。** `skills/dajare/SKILL.md` は pre-commit hook で自動的に同期されます。

description を変更した場合は `AGENTS.md` と `.claude-plugin/plugin.json` も揃えてください。

詳しくは [CLAUDE.md](CLAUDE.md) を参照。

## ライセンス

MIT
