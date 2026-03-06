#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.9"
# dependencies = [
#     "sudachipy>=0.6.8",
#     "sudachidict-core>=20230927",
#     "wordfreq>=3.0",
# ]
# ///
"""
韻辞書ビルドスクリプト: wordfreq の日本語頻出語から母音列インデックスを生成する

Usage:
    uv run scripts/build-rhyme-dict.py

出力: scripts/rhyme-dict.json.gz
"""

import gzip
import json
import os
import re
import sys

from sudachipy import Dictionary
from wordfreq import top_n_list

# rhyme.py と同じ音韻分析ロジックを使うため、同ディレクトリからインポート
sys.path.insert(0, os.path.dirname(__file__))
from rhyme import analyze_morae, kata_to_hira


def main() -> None:
    print("Fetching top 50000 Japanese words...", file=sys.stderr)
    raw_words = top_n_list("ja", 50000)

    # フィルタ: 2文字以上、ASCII/記号のみでない、活用語尾の断片でない
    words = [
        w
        for w in raw_words
        if len(w) >= 2 and not w.isascii() and not re.match(r"^[ぁ-ん]{1,2}$", w)
    ]
    print(f"Filtered to {len(words)} words", file=sys.stderr)

    tokenizer = Dictionary().create()

    # 母音列 → [(単語, 読み)] のインデックスを構築
    index: dict[str, list[list[str]]] = {}
    skipped = 0

    for i, word in enumerate(words):
        if (i + 1) % 5000 == 0:
            print(f"  Processing {i + 1}/{len(words)}...", file=sys.stderr)

        try:
            morphs = tokenizer.tokenize(word)
            reading = "".join(kata_to_hira(m.reading_form()) for m in morphs)

            if not reading or (reading == word and any(
                "\u4e00" <= c <= "\u9fff" for c in word
            )):
                skipped += 1
                continue

            morae = analyze_morae(reading)
            vowels = [v for _, v in morae]
            vowel_str = "-".join(v if v else "·" for v in vowels)

            if vowel_str not in index:
                index[vowel_str] = []
            index[vowel_str].append([word, reading])
        except Exception:
            skipped += 1
            continue

    print(f"Built index: {len(index)} patterns, skipped {skipped}", file=sys.stderr)

    # パターンごとにエントリ数でソート（多い順）、各パターン内は元の頻度順を維持
    sorted_index = dict(sorted(index.items(), key=lambda x: -len(x[1])))

    output_path = os.path.join(os.path.dirname(__file__), "rhyme-dict.json.gz")
    with gzip.open(output_path, "wt", encoding="utf-8") as f:
        json.dump(sorted_index, f, ensure_ascii=False)

    # サイズ確認
    size_kb = os.path.getsize(output_path) / 1024
    total_entries = sum(len(v) for v in sorted_index.values())
    print(
        f"Saved to {output_path} ({size_kb:.0f} KB, {total_entries} entries)",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
