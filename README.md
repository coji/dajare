# dajare-generator

日本語のダジャレ（駄洒落）を生成する [Agent Skill](https://agentskills.io)。

単語やお題・状況を入力すると、音の類似度・意味の距離・文脈の自然さを考慮した質の高いダジャレを 3〜5 個生成します。

[Agent Skills](https://agentskills.io) オープン標準に準拠しており、Claude Code / Cursor / Codex / Gemini CLI など 40 以上のエージェントで利用できます。

## インストール

### npx skills (推奨)

```bash
# プロジェクトにインストール
npx skills add coji/dajare-generator

# グローバルにインストール（全プロジェクトで使用）
npx skills add coji/dajare-generator -g

# 特定のエージェントを指定
npx skills add coji/dajare-generator --agent claude-code --agent cursor
```

### openskills

```bash
npx openskills install coji/dajare-generator
```

### Claude Code プラグイン

```
/plugin install coji/dajare-generator
```

### 手動インストール

```bash
# Claude Code
cp -r dajare-generator ~/.claude/skills/

# Cursor / その他のエージェント
cp -r dajare-generator .agents/skills/
```

## 使い方

### 自動トリガー

「ダジャレ」「駄洒落」「おやじギャグ」「pun」などのキーワードや、「〇〇で何か面白いこと言って」のような言い回しで自動的にスキルが発動します。

### スラッシュコマンド

```
/dajare-generator コーヒー
/dajare-generator 会議中の眠気
```

### 出力例

> コーヒーで攻めます。
>
> 1. **交費ーがかさむ喫茶店** （「こーひー」→「交費ー（交通費）」。カフェと出費という意味の衝突）
> 2. **恋い焦がれて深煎り**（「こい」→「恋い」と「濃い」、「こがれて」→「焦がれて」と「焦がして」の二重掛け）
> 3. **氷ーヒーで涼む夏**（「こおり」→「コーヒー」に「氷」を埋め込み。アイスコーヒーの情景）

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

## 開発

### セットアップ

```bash
git clone https://github.com/coji/dajare-generator.git
cd dajare-generator
git config core.hooksPath .githooks
```

### SKILL.md の編集

**ルートの `SKILL.md` だけを編集してください。** `skills/dajare-generator/SKILL.md` は pre-commit hook で自動的に同期されます。

description を変更した場合は `AGENTS.md` と `.claude-plugin/plugin.json` も揃えてください。

詳しくは [CLAUDE.md](CLAUDE.md) を参照。

## ライセンス

MIT
