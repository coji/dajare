<skills_system priority="1">

## Available Skills

<usage>
When users ask you to perform tasks, check if any of the available skills below match.
Skills provide specialized capabilities and domain knowledge.

To load a skill's full instructions, run:
```
npx openskills read <skill-name>
```
</usage>

<available_skills>
<skill>
  <name>dajare-generator</name>
  <description>日本語のダジャレ（駄洒落）を生成するスキル。ユーザーが単語やお題・状況を入力すると、それをもとに面白いダジャレを3〜5個つくって返す。「ダジャレ」「駄洒落」「だじゃれ」「おやじギャグ」「シャレ」「洒落」「しゃれ」「語呂合わせ」「pun」といった言葉が出てきたら必ずこのスキルを使う。また、「〇〇で何か面白いこと言って」「〇〇でひとボケして」のように、言葉遊びやボケを求められた場合もこのスキルをトリガーする。</description>
  <location>project</location>
</skill>
</available_skills>

</skills_system>

<!-- Maintenance Note for AI Agents -->
<!-- ルートの SKILL.md が唯一の正（Single Source of Truth）。 -->
<!-- description を変更する場合は SKILL.md の frontmatter、このファイル、.claude-plugin/plugin.json を同期すること。 -->
<!-- skills/dajare-generator/SKILL.md は pre-commit hook で自動コピーされるため直接編集しない。 -->
