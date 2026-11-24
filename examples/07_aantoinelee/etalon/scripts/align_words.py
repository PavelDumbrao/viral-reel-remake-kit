#!/usr/bin/env python3
"""v4_align.py — слова v3 (номера, на которые завязана графика сцен) с временами нового голоса v4.
Сопоставление по нормализованному тексту (difflib); не найденные слова — интерполяция между соседями. Пишет base/words_full.json."""
import json, os, re, difflib
V = os.environ.get("WORK", os.getcwd())   # рабочая папка ролика
old = json.load(open(V + "/base/words_v3.json"))
r = json.load(open(V + "/base/stt_voice.json")); r = r.get("result", r)
new = [w for w in r["words"] if w.get("type") == "word"]
ALIAS = {"клод": "claude", "клода": "claude", "код": "code", "кодекс": "codex", "нанобанане": "nanobanane", "плейрайт": "playwright", "обсидиан": "obsidian", "телеграм": "telegram"}
def n(s):
    s = re.sub(r"[^0-9a-zа-яё]", "", s.lower()).replace("ё", "е"); return ALIAS.get(s, s)
def split(ws):
    out = []
    for w in ws:
        parts = w["text"].replace("-", " ").split()
        d = (w["end"] - w["start"]) / max(1, len(parts))
        for j, p in enumerate(parts): out.append({"t": n(p), "s": w["start"] + j * d, "e": w["start"] + (j + 1) * d})
    return out
nw = split(new); a = [n(w["text"]) for w in old]; b = [w["t"] for w in nw]
sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
tm = [None] * len(old); miss = []
for op, i1, i2, j1, j2 in sm.get_opcodes():
    if op == "equal":
        for k in range(i2 - i1): tm[i1 + k] = (nw[j1 + k]["s"], nw[j1 + k]["e"])
    elif op == "replace" and i2 - i1 == j2 - j1:
        for k in range(i2 - i1): tm[i1 + k] = (nw[j1 + k]["s"], nw[j1 + k]["e"])
    elif op == "replace" and j2 > j1:
        s, e = nw[j1]["s"], nw[j2 - 1]["e"]; d = (e - s) / (i2 - i1)
        for k in range(i2 - i1): tm[i1 + k] = (s + k * d, s + (k + 1) * d)
    if op != "equal": miss.append((op, a[i1:i2], b[j1:j2]))
for i in range(len(tm)):
    if tm[i] is None:
        p = next((tm[j][1] for j in range(i - 1, -1, -1) if tm[j]), 0.0)
        q = next((tm[j][0] for j in range(i + 1, len(tm)) if tm[j]), p + 0.3)
        tm[i] = (p, max(p + 0.05, min(q, p + 0.3)))
out = [{"text": w["text"], "start": round(tm[i][0], 3), "end": round(tm[i][1], 3), "i": i} for i, w in enumerate(old)]
json.dump(out, open(V + "/base/words_full.json", "w"), ensure_ascii=False, indent=0)
print("слов v3", len(old), "голос", len(nw), "ratio %.3f" % sm.ratio()); [print(" ", m) for m in miss]
