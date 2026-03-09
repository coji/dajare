#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.9"
# dependencies = [
#     "sudachipy>=0.6.8",
#     "sudachidict-core>=20230927",
#     "numpy>=1.24",
# ]
# ///
"""
韻検索・分析スクリプト: 読み変換・母音列・子音列抽出・類似度比較・逆引き韻辞書・韻bedding検索

Usage:
    uv run scripts/rhyme.py <単語> [<単語> ...]
    uv run scripts/rhyme.py --search <単語>
    uv run scripts/rhyme.py --search-embed <単語>
    uv run scripts/rhyme.py --json <単語> [<単語> ...]

Examples:
    uv run scripts/rhyme.py コーヒー
    uv run scripts/rhyme.py コーヒー 公費 高飛車
    uv run scripts/rhyme.py --search コーヒー
    uv run scripts/rhyme.py --search-embed コーヒー
    uv run scripts/rhyme.py --json コーヒー
"""

import gzip
import json
import os
import sys
import unicodedata

from sudachipy import Dictionary

# ひらがな → (子音, 母音) マッピング
# 拗音は前の文字と合わせて処理するため、小書きゃゅょは別扱い
KANA_MAP: dict[str, tuple[str, str]] = {
    # あ行
    "あ": ("", "a"), "い": ("", "i"), "う": ("", "u"), "え": ("", "e"), "お": ("", "o"),
    # か行
    "か": ("k", "a"), "き": ("k", "i"), "く": ("k", "u"), "け": ("k", "e"), "こ": ("k", "o"),
    # が行
    "が": ("g", "a"), "ぎ": ("g", "i"), "ぐ": ("g", "u"), "げ": ("g", "e"), "ご": ("g", "o"),
    # さ行
    "さ": ("s", "a"), "し": ("sh", "i"), "す": ("s", "u"), "せ": ("s", "e"), "そ": ("s", "o"),
    # ざ行
    "ざ": ("z", "a"), "じ": ("j", "i"), "ず": ("z", "u"), "ぜ": ("z", "e"), "ぞ": ("z", "o"),
    # た行
    "た": ("t", "a"), "ち": ("ch", "i"), "つ": ("ts", "u"), "て": ("t", "e"), "と": ("t", "o"),
    # だ行
    "だ": ("d", "a"), "ぢ": ("j", "i"), "づ": ("z", "u"), "で": ("d", "e"), "ど": ("d", "o"),
    # な行
    "な": ("n", "a"), "に": ("n", "i"), "ぬ": ("n", "u"), "ね": ("n", "e"), "の": ("n", "o"),
    # は行
    "は": ("h", "a"), "ひ": ("h", "i"), "ふ": ("f", "u"), "へ": ("h", "e"), "ほ": ("h", "o"),
    # ば行
    "ば": ("b", "a"), "び": ("b", "i"), "ぶ": ("b", "u"), "べ": ("b", "e"), "ぼ": ("b", "o"),
    # ぱ行
    "ぱ": ("p", "a"), "ぴ": ("p", "i"), "ぷ": ("p", "u"), "ぺ": ("p", "e"), "ぽ": ("p", "o"),
    # ま行
    "ま": ("m", "a"), "み": ("m", "i"), "む": ("m", "u"), "め": ("m", "e"), "も": ("m", "o"),
    # や行
    "や": ("y", "a"), "ゆ": ("y", "u"), "よ": ("y", "o"),
    # ら行
    "ら": ("r", "a"), "り": ("r", "i"), "る": ("r", "u"), "れ": ("r", "e"), "ろ": ("r", "o"),
    # わ行
    "わ": ("w", "a"), "ゐ": ("w", "i"), "ゑ": ("w", "e"), "を": ("w", "o"),
}

# 小書き拗音(前の文字の子音と組み合わせて1拍)
YOUON_MAP: dict[str, str] = {
    "ゃ": "a",
    "ゅ": "u",
    "ょ": "o",
}

# 小書き母音(外来語表記等)
SMALL_VOWEL_MAP: dict[str, str] = {
    "ぁ": "a",
    "ぃ": "i",
    "ぅ": "u",
    "ぇ": "e",
    "ぉ": "o",
}


def kata_to_hira(text: str) -> str:
    """カタカナをひらがなに変換"""
    result = []
    for ch in text:
        cp = ord(ch)
        if 0x30A1 <= cp <= 0x30F6:  # ァ-ヶ
            result.append(chr(cp - 0x60))
        elif ch == "ヴ":
            result.append("ゔ")
        else:
            result.append(ch)
    return "".join(result)


_tokenizer = None


def _get_tokenizer():
    global _tokenizer
    if _tokenizer is None:
        _tokenizer = Dictionary().create()
    return _tokenizer


def to_reading(text: str) -> str:
    """sudachipy を使って漢字混じりテキストをひらがなに変換"""
    morphs = _get_tokenizer().tokenize(text)
    return "".join(kata_to_hira(m.reading_form()) for m in morphs)


def analyze_morae(reading: str) -> list[tuple[str, str]]:
    """
    ひらがな文字列をモーラ(拍)に分解し、各拍の(子音, 母音)を返す。

    Returns:
        list of (consonant, vowel) tuples
        特殊拍: ("N", "")=撥音, ("Q", "")=促音
    """
    morae: list[tuple[str, str]] = []
    i = 0
    chars = list(reading)
    last_vowel = ""

    while i < len(chars):
        ch = chars[i]

        # 長音符: 直前の母音を繰り返す
        if ch == "ー":
            if last_vowel:
                morae.append(("", last_vowel))
            i += 1
            continue

        # 促音
        if ch == "っ":
            morae.append(("Q", ""))
            i += 1
            continue

        # 撥音
        if ch == "ん":
            morae.append(("N", ""))
            last_vowel = ""
            i += 1
            continue

        # 通常のかな
        if ch in KANA_MAP:
            consonant, vowel = KANA_MAP[ch]

            # 次の文字が拗音かチェック
            if i + 1 < len(chars) and chars[i + 1] in YOUON_MAP:
                youon_vowel = YOUON_MAP[chars[i + 1]]
                # 子音 + y で拗音子音を作る(し→sh は shy にならないよう調整)
                if consonant in ("sh", "ch", "j"):
                    youon_consonant = consonant
                else:
                    youon_consonant = consonant + "y"
                morae.append((youon_consonant, youon_vowel))
                last_vowel = youon_vowel
                i += 2
                continue

            # 次の文字が小書き母音かチェック(ふぁ、てぃ等)
            if i + 1 < len(chars) and chars[i + 1] in SMALL_VOWEL_MAP:
                small_vowel = SMALL_VOWEL_MAP[chars[i + 1]]
                morae.append((consonant, small_vowel))
                last_vowel = small_vowel
                i += 2
                continue

            morae.append((consonant, vowel))
            last_vowel = vowel
            i += 1
            continue

        # ゔ (ヴの変換)
        if ch == "ゔ":
            # 次が拗音/小書き母音かチェック
            if i + 1 < len(chars) and chars[i + 1] in SMALL_VOWEL_MAP:
                small_vowel = SMALL_VOWEL_MAP[chars[i + 1]]
                morae.append(("v", small_vowel))
                last_vowel = small_vowel
                i += 2
                continue
            morae.append(("v", "u"))
            last_vowel = "u"
            i += 1
            continue

        # 未知の文字はスキップ
        i += 1

    return morae


def analyze_word(word: str) -> dict:
    """単語を分析して読み・母音列・子音列を返す"""
    reading = to_reading(word)
    morae = analyze_morae(reading)

    vowels = [v for _, v in morae]
    consonants = [c for c, _ in morae]

    return {
        "input": word,
        "reading": reading,
        "morae": len(morae),
        "vowels": vowels,
        "consonants": consonants,
        "vowel_str": "-".join(v if v else "·" for v in vowels),
        "consonant_str": "-".join(c if c else "·" for c in consonants),
    }


def lcs_length(a: list, b: list) -> tuple[int, list]:
    """最長共通部分列(LCS)の長さと部分列を返す"""
    m, n = len(a), len(b)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if a[i - 1] == b[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])

    # 部分列を復元
    seq: list = []
    i, j = m, n
    while i > 0 and j > 0:
        if a[i - 1] == b[j - 1]:
            seq.append(a[i - 1])
            i -= 1
            j -= 1
        elif dp[i - 1][j] > dp[i][j - 1]:
            i -= 1
        else:
            j -= 1
    seq.reverse()
    return dp[m][n], seq


def vowel_similarity(a: dict, b: dict) -> dict:
    """2つの単語の母音列の類似度を計算する"""
    va = [v for v in a["vowels"] if v]  # 空文字(促音)を除外
    vb = [v for v in b["vowels"] if v]
    length, seq = lcs_length(va, vb)
    max_len = max(len(va), len(vb))
    ratio = length / max_len if max_len > 0 else 0.0
    return {
        "pair": f"{a['input']} × {b['input']}",
        "ratio": ratio,
        "percent": round(ratio * 100),
        "lcs": seq,
        "lcs_str": "-".join(seq),
        "lcs_length": length,
        "max_length": max_len,
    }


def display_width(s: str) -> int:
    """文字列の表示幅を計算する（全角=2, 半角=1）"""
    width = 0
    for ch in s:
        cat = unicodedata.east_asian_width(ch)
        width += 2 if cat in ("F", "W") else 1
    return width


def pad(s: str, width: int) -> str:
    """全角文字を考慮してパディングする"""
    return s + " " * (width - display_width(s))


def format_text(results: list[dict], similarities: list[dict]) -> str:
    """LLM 向けのコンパクトなテキスト出力を生成する"""
    lines = []

    if len(results) == 1:
        r = results[0]
        lines.append(f"{r['input']} → {r['reading']} ({r['morae']}拍)")
        lines.append(f"  母音: {r['vowel_str']}  子音: {r['consonant_str']}")
    else:
        # カラム幅を計算（表示幅ベース）
        col_input = max(display_width(r["input"]) for r in results)
        col_reading = max(display_width(r["reading"]) for r in results)
        col_vowel = max(len(r["vowel_str"]) for r in results)

        col_input = max(col_input, 4)
        col_reading = max(col_reading, 4)

        header = (
            f"{pad('単語', col_input)}  "
            f"{pad('読み', col_reading)}  "
            f"拍  "
            f"{pad('母音', col_vowel)}  "
            f"子音"
        )
        lines.append(header)

        for r in results:
            line = (
                f"{pad(r['input'], col_input)}  "
                f"{pad(r['reading'], col_reading)}  "
                f"{r['morae']:>2}  "
                f"{r['vowel_str']:<{col_vowel}}  "
                f"{r['consonant_str']}"
            )
            lines.append(line)

        if similarities:
            lines.append("")
            lines.append("類似度 (母音LCS):")
            for s in similarities:
                verdict = "⚠ 低い" if s["percent"] < 50 else "✓"
                lines.append(
                    f"  {s['pair']}: "
                    f"{s['percent']}% "
                    f"(共通: {s['lcs_str'] or 'なし'}, "
                    f"{s['lcs_length']}/{s['max_length']}拍) "
                    f"{verdict}"
                )

    return "\n".join(lines)


def load_rhyme_dict() -> dict[str, list[list[str]]]:
    """韻辞書を読み込む"""
    dict_path = os.path.join(os.path.dirname(__file__), "rhyme-dict.json.gz")
    if not os.path.exists(dict_path):
        print(
            f"韻辞書が見つかりません: {dict_path}\n"
            "  uv run scripts/build-rhyme-dict.py で生成してください",
            file=sys.stderr,
        )
        sys.exit(1)
    with gzip.open(dict_path, "rt", encoding="utf-8") as f:
        return json.load(f)


def search_rhymes(word: str) -> None:
    """単語の母音列で韻辞書を検索し、完全一致・部分一致の候補を表示する"""
    info = analyze_word(word)
    vowels = [v for v in info["vowels"] if v]  # 促音を除外
    vowel_str = "-".join(vowels)

    print(f"{info['input']} → {info['reading']} ({info['morae']}拍)")
    print(f"  母音: {info['vowel_str']}  子音: {info['consonant_str']}")
    print()

    rhyme_dict = load_rhyme_dict()

    # 完全一致
    exact = rhyme_dict.get(vowel_str, [])
    # 自分自身を除外
    exact = [[w, r] for w, r in exact if w != word]

    if exact:
        print(f"完全一致 ({vowel_str}): {len(exact)}件")
        for w, r in exact[:20]:
            print(f"  {w} ({r})")
        if len(exact) > 20:
            print(f"  ... 他 {len(exact) - 20}件")
    else:
        print(f"完全一致 ({vowel_str}): なし")

    # 部分一致: 辞書内の各パターンとLCSで類似度を計算し、50%以上のものを抽出
    print()
    print("類似パターン (類似度50%以上):")

    similar: list[tuple[int, str, list[list[str]]]] = []
    for pattern, entries in rhyme_dict.items():
        if pattern == vowel_str:
            continue
        pattern_vowels = [v for v in pattern.split("-") if v != "·"]
        lcs_len, _ = lcs_length(vowels, pattern_vowels)
        max_len = max(len(vowels), len(pattern_vowels))
        if max_len > 0:
            ratio = lcs_len / max_len
            if ratio >= 0.5:
                percent = round(ratio * 100)
                similar.append((percent, pattern, entries))

    similar.sort(key=lambda x: -x[0])

    if similar:
        for percent, pattern, entries in similar[:10]:
            sample = entries[:5]
            words_str = ", ".join(f"{w}({r})" for w, r in sample)
            more = f" 他{len(entries) - 5}件" if len(entries) > 5 else ""
            print(f"  {percent}% {pattern}: {words_str}{more}")
    else:
        print("  なし")


# ---------------------------------------------------------------------------
# 韻bedding: 母音列の n-gram ベクトル化によるファジー韻検索
# ---------------------------------------------------------------------------

# 母音アルファベット (a,i,u,e,o + X=特殊拍:撥音・促音)
_EMBED_ALPHA = ["a", "i", "u", "e", "o", "X"]


def _build_ngram_vocab() -> dict[str, int]:
    """1-gram, 2-gram, 3-gram の全組み合わせ → ベクトルインデックスのマッピングを構築"""
    vocab: dict[str, int] = {}
    idx = 0
    for n in (1, 2, 3):
        for combo in _ngram_combos(_EMBED_ALPHA, n):
            vocab[combo] = idx
            idx += 1
    return vocab


def _ngram_combos(alpha: list[str], n: int) -> list[str]:
    """alpha の n-gram の全組み合わせを生成"""
    if n == 1:
        return list(alpha)
    result = []
    for prefix in _ngram_combos(alpha, n - 1):
        for ch in alpha:
            result.append(prefix + ch)
    return result


_NGRAM_VOCAB = _build_ngram_vocab()
_NGRAM_DIM = len(_NGRAM_VOCAB)  # 6 + 36 + 216 = 258


def _vowels_to_symbols(vowels: list[str]) -> list[str]:
    """母音リストを embedding 用のシンボル列に変換"""
    symbols = []
    for v in vowels:
        if v in ("a", "i", "u", "e", "o"):
            symbols.append(v)
        else:
            symbols.append("X")  # 撥音・促音・空文字
    return symbols


def _symbols_to_vector(symbols: list[str]) -> "numpy.ndarray":
    """シンボル列を n-gram 頻度ベクトルに変換（L2 正規化済み）"""
    import numpy as np

    vec = np.zeros(_NGRAM_DIM, dtype=np.float32)
    n = len(symbols)

    for ch in symbols:
        if ch in _NGRAM_VOCAB:
            vec[_NGRAM_VOCAB[ch]] += 1
    for i in range(n - 1):
        bg = symbols[i] + symbols[i + 1]
        if bg in _NGRAM_VOCAB:
            vec[_NGRAM_VOCAB[bg]] += 1
    for i in range(n - 2):
        tg = symbols[i] + symbols[i + 1] + symbols[i + 2]
        if tg in _NGRAM_VOCAB:
            vec[_NGRAM_VOCAB[tg]] += 1

    norm = np.linalg.norm(vec)
    if norm > 0:
        vec /= norm
    return vec


def vowels_to_vector(vowels: list[str]) -> "numpy.ndarray":
    """母音リストを n-gram ベクトルに変換（公開API）"""
    return _symbols_to_vector(_vowels_to_symbols(vowels))


def _pattern_to_symbols(pattern: str) -> list[str]:
    """韻辞書のパターン文字列 (e.g. "o-o-i-i") をシンボル列に変換"""
    symbols = []
    for v in pattern.split("-"):
        if v in ("a", "i", "u", "e", "o"):
            symbols.append(v)
        else:
            symbols.append("X")
    return symbols


def search_rhymes_embed(word: str, top_k: int = 30) -> None:
    """韻bedding によるファジー韻検索。語感踏み・長さ違いにも対応。"""
    import numpy as np

    info = analyze_word(word)
    query_symbols = _vowels_to_symbols(info["vowels"])
    query_vec = _symbols_to_vector(query_symbols)

    print(f"{info['input']} → {info['reading']} ({info['morae']}拍)")
    print(f"  母音: {info['vowel_str']}  子音: {info['consonant_str']}")
    print()

    rhyme_dict = load_rhyme_dict()
    patterns = list(rhyme_dict.keys())

    # 全パターンのベクトルを一括計算
    matrix = np.array(
        [_symbols_to_vector(_pattern_to_symbols(p)) for p in patterns],
        dtype=np.float32,
    )

    # コサイン類似度（ベクトルは正規化済みなのでドット積 = コサイン類似度）
    sims = matrix @ query_vec

    # 自分自身のパターンを特定
    own_pattern = "-".join(v if v else "·" for v in info["vowels"])

    # 上位を抽出
    top_indices = np.argsort(sims)[::-1]
    shown = 0
    print(f"韻bedding検索 (上位{top_k}件):")
    for idx in top_indices:
        if shown >= top_k:
            break
        pattern = patterns[idx]
        if pattern == own_pattern:
            continue
        sim_pct = round(float(sims[idx]) * 100)
        if sim_pct < 30:
            break
        entries = rhyme_dict[pattern]
        sample = entries[:5]
        words_str = ", ".join(f"{w}({r})" for w, r in sample)
        more = f" 他{len(entries) - 5}件" if len(entries) > 5 else ""
        print(f"  {sim_pct}% {pattern}: {words_str}{more}")
        shown += 1

    if shown == 0:
        print("  該当なし")


def main() -> None:
    args = sys.argv[1:]

    if not args:
        print(
            "Usage:\n"
            "  uv run scripts/rhyme.py <単語> [<単語> ...]   分析・比較\n"
            "  uv run scripts/rhyme.py --search <単語>       逆引き韻辞書検索\n"
            "  uv run scripts/rhyme.py --search-embed <単語>  韻bedding検索（語感踏み対応）\n"
            "  uv run scripts/rhyme.py --json <単語>         JSON出力",
            file=sys.stderr,
        )
        sys.exit(1)

    # --search-embed モード
    if "--search-embed" in args:
        search_words = [a for a in args if not a.startswith("--")]
        if not search_words:
            print("Usage: uv run scripts/rhyme.py --search-embed <単語>", file=sys.stderr)
            sys.exit(1)
        for word in search_words:
            search_rhymes_embed(word)
            if word != search_words[-1]:
                print()
        return

    # --search モード
    if "--search" in args:
        search_words = [a for a in args if a not in ("--search", "--json")]
        if not search_words:
            print("Usage: uv run scripts/rhyme.py --search <単語>", file=sys.stderr)
            sys.exit(1)
        for word in search_words:
            search_rhymes(word)
            if word != search_words[-1]:
                print()
        return

    use_json = "--json" in args
    words = [a for a in args if a not in ("--json",)]

    if not words:
        print("Usage: uv run scripts/rhyme.py <単語> [<単語> ...] [--json]", file=sys.stderr)
        sys.exit(1)

    results = [analyze_word(w) for w in words]

    # 2語以上なら全ペアの類似度を計算
    similarities = []
    if len(results) >= 2:
        for i in range(len(results)):
            for j in range(i + 1, len(results)):
                similarities.append(vowel_similarity(results[i], results[j]))

    if use_json:
        output = {"words": results}
        if similarities:
            output["similarities"] = similarities
        print(json.dumps(output, ensure_ascii=False, indent=2))
    else:
        print(format_text(results, similarities))


if __name__ == "__main__":
    main()
