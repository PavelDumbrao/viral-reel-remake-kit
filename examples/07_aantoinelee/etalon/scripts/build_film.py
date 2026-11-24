#!/usr/bin/env python3
"""v3_build.py — сборщик ролика 07 v3 (ремейк aantoinelee «7 инструментов вокруг Claude Code»). Все секунды — из words_film.json
(распознавание готового голоса). Смена дубля/голоса = пересборка одной командой.

  python3 v3_build.py --print                          # сцены и их слова (время фильма)
  python3 v3_build.py [--ver v1]                       # собрать proj/ (сцены, титры, корень) + timing.json
  python3 v3_build.py --only s09,s11 --out sb/A        # песочница исполнителя: только эти сцены

Шаблон сцены tpl/sNN.html (<template>…</template>) получает: @@KIT@@ (шрифты+kit.css), @@LIB@@ (icons.js+lib.js),
@@WORDS@@ (JSON слов сцены [{t,i,s,e}], s/e — ЛОКАЛЬНОЕ время сцены, i — сквозной индекс слова голоса), @@DUR@@, @@SID@@.
Без шаблона сцена — пустая заглушка (видно только видео корня)."""
import json, math, os, re, shutil, sys

V = os.environ.get("WORK", os.getcwd())   # рабочая папка ролика
W = V + "/om"; TPL = W + "/tpl"
FPS, LEAD, TAIL = 30, 0.10, 0.55
# (id, раскладка, сквозной индекс слова-начала). SP сплит · FW Павел общий · FC Павел крупно · BR B-roll · SC экран на весь кадр · MO моушн на весь кадр
SCENES = [("s01","SP",0),("s02","SP",7),("s03","FW",14),("s04","BR",19),("s05","FW",22),("s06","MO",26),("s07","FC",36),("s08","FW",44),
 ("s09","SP",50),("s10","FC",65),("s11","SP",70),("s12","SC",77),("s13","FW",79),("s14","SP",81),("s15","FW",90),("s16","FC",93),
 ("s17","SP",99),("s18","FW",112),("s19","FC",115),("s20","FW",119),("s21","MO",121),("s22","FW",127),("s23","SP",129),("s24","SC",136),
 ("s25","FW",147),("s26","SP",149),("s27","FC",159),("s28","SP",161),("s29","FW",166),("s30","BR",173),("s31","SP",181),("s32","FW",190),
 ("s33","FC",197),("s34","FW",204),("s35","FC",205),("s36","FW",212),("s37","FC",217)]
BROLL = {"s04": ("hands", 0.0, "full"), "s30": ("laptop", 0.0, "full")}
CAPY = {"SP": 985, "FW": 1180, "FC": 1180, "BR": 1250, "SC": 1600, "MO": 1600}
CAPY_SCENE = {}
# титры: '*' — жёлтое слово; {показ|голос} — показ отличается от звучания ('+' в голосе — несколько слов STT); ' | ' — граница группы
GROUPS = """Если ты пользуешься | Claude Code | вот *так, | а у других | постоянно видишь | вот *такое, | вот семь инструментов, | которые я |
*каждый *день | использую | вместе с Claude Code. |
На этой связке | я веду уже | *шестой *поток | {Хардкодинг PRO,|хардкодинг+про} | а *агенты | пишут код за меня | каждый день. |
Номер один, | параллельные *сессии | Claude Code. | Несколько *агентов *рядом, | у каждого | своя *задача, | а тот, кто {ждёт|ждет} | моего ответа, |
сразу *подсвечен. |
Второй, Obsidian | как второй мозг. | Агенты сами | *читают и *пишут | в него через *MCP. | Самое важное, | у всех агентов | во всех *проектах |
*{общий|один+общий} *контекст. |
Третий, | Playwright *MCP. | По сути, это | *глаза для агента. | Он сам открывает *сайт, | *прокликивает его | и *проверяет, | что {всё|все} работает |
как надо. |
Номер четыре, | обязательно | второй агент на ревью. | {Codex|Кодекс} проверяет | каждую правку | {Claude|Клода} против | *всего *проекта. |
Номер пять, | *{дизайн-скиллы.|дизайн+скиллы} | {Claude|Клод} {берёт|берет} {приёмы|приемы} | *лучших *интерфейсов, | видит, что у них | *работает, |
и переносит это | в *твой *UI. |
Номер шесть, | если не хочешь, | чтобы сайт выглядел | *шаблонно, | делай свою *графику. | Подключи {Claude|Клода} | к *{Nano Banana|Нанобанане} |
{или|или+к} *Kling. |
И номер семь, | запускай агентов | в *облаке, | потому что {всё,|все} | что выше, | требует открытого | *ноутбука. |
Claude Code спокойно | работает *без *экрана | на {твоём|твоем} *VPS, | а пишешь ты ему | прямо в *Telegram. |
Советую это | для любой задачи, | которую гоняешь | *регулярно. |
Как настроить каждый, | разберу в следующих | роликах, | так что | *подписывайся на меня | и напиши | в комментариях | *{«ИИ»,|и+и} | если хочешь |
полный гайд."""


def q(x): return round(x * FPS) / FPS
def norm(w): return re.sub(r"[«»—–\-.,?!:;…\"\s]", "", w.lower()).replace("ё", "е")


def load():
    return json.load(open(V + "/base/words_full.json", encoding="utf-8"))


def timing(words):
    plan = json.load(open(V + "/base/plan.json"))
    total = math.ceil((plan["duration"] + TAIL) * FPS) / FPS
    cuts = [0.0 if wi == 0 else q(words[wi]["start"] - LEAD) for _, _, wi in SCENES]
    ends = cuts[1:] + [total]
    sc = {}
    for k, (sid, lay, wi) in enumerate(SCENES):
        sc[sid] = {"start": cuts[k], "end": ends[k], "layout": lay, "w0": wi, "w1": SCENES[k + 1][2] if k + 1 < len(SCENES) else len(words)}
    return total, sc


STUB = """<template><style>@@KIT@@</style>
<div id="@@SID@@-root" data-composition-id="@@SID@@" data-width="1080" data-height="1920"></div>
<script>window.__timelines=window.__timelines||{};window.__timelines["@@SID@@"]=gsap.timeline({paused:true});</script></template>"""


def main():
    words = load()
    total, sc = timing(words)
    if "--print" in sys.argv:
        for sid, v in sc.items():
            ws = [w for w in words if v["w0"] <= w["i"] < v["w1"]]
            print("%s %-2s %6.2f–%6.2f (%.2f)  %s" % (sid, v["layout"], v["start"], v["end"], v["end"] - v["start"],
                  " ".join("%d:%s" % (w["i"], w["text"]) for w in ws)))
        print("total", total); return
    ver = sys.argv[sys.argv.index("--ver") + 1] if "--ver" in sys.argv else "v1"
    only = set(sys.argv[sys.argv.index("--only") + 1].split(",")) if "--only" in sys.argv else None
    out = sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else W + "/proj"
    if out != W + "/proj" and not os.path.exists(out):
        os.makedirs(out + "/compositions")
        os.symlink(W + "/proj/assets", out + "/assets"); shutil.copy(W + "/proj/hyperframes.json", out)
    os.makedirs(out + "/compositions", exist_ok=True)
    kit = open(TPL + "/fonts.css", encoding="utf-8").read() + "\n" + open(TPL + "/kit.css", encoding="utf-8").read()
    lib = open(TPL + "/icons.js", encoding="utf-8").read() + "\n" + open(TPL + "/lib.js", encoding="utf-8").read()
    hosts = []
    for k, (sid, v) in enumerate(sc.items()):
        if only and sid not in only: continue
        a, b = v["start"], v["end"]
        loc = [{"t": w["text"], "i": w["i"], "s": round(w["start"] - a, 3), "e": round(w["end"] - a, 3)} for w in words if v["w0"] <= w["i"] < v["w1"]]
        p = TPL + "/%s.html" % sid
        s = open(p, encoding="utf-8").read() if os.path.exists(p) else STUB
        s = (s.replace("@@KIT@@", kit).replace("@@LIB@@", lib).replace("@@WORDS@@", json.dumps(loc, ensure_ascii=False))
              .replace("@@DUR@@", str(round(b - a, 4))).replace("@@SID@@", sid))
        left = re.findall(r"@@[A-Z_0-9]+@@", s)
        if left: sys.exit("не подставлено в %s: %s" % (sid, left))
        open(out + "/compositions/%s.html" % sid, "w", encoding="utf-8").write(s)
        hosts.append('  <div id="h-%s" class="scene" data-composition-id="%s" data-composition-src="compositions/%s.html" '
                     'data-start="%s" data-duration="%s" data-track-index="%d" data-track-kind="graphics" '
                     'data-width="1080" data-height="1920"></div>' % (sid, sid, sid, "%.6f" % (round(a * FPS) / FPS), "%.6f" % ((round(b * FPS) - round(a * FPS)) / FPS - 0.004), 1 + k % 2))
    # ---- титры ----
    toks = re.findall(r"\*?\{[^}]*\}|\S+", GROUPS.replace("\n", " "))
    groups, cur, ci = [], [], 0
    for tok in toks:
        if tok == "|": groups.append(cur); cur = []; continue
        hot = tok.startswith("*"); tok = tok.lstrip("*")
        m = re.match(r"\{([^|]*)\|([^}]*)\}$", tok)
        disp, say = (m.group(1), m.group(2)) if m else (tok, tok)
        parts = say.split("+"); first = None
        for sp in parts:
            w = words[ci]
            if norm(w["text"]) != norm(sp): sys.exit("титры: ждали «%s», в голосе «%s» (#%d)" % (sp, w["text"], w["i"]))
            first = first or w; last = w; ci += 1
        cur.append({"disp": disp, "hot": hot, "s": first["start"], "e": last["end"], "i": first["i"]})
    if cur: groups.append(cur)
    if ci != len(words): sys.exit("титры: распределено %d из %d слов" % (ci, len(words)))
    def scene_of(t):
        for sid, v in sc.items():
            if v["start"] <= t < v["end"]: return sid, v
        return list(sc.items())[-1]
    html, gj = [], []
    for gi, g in enumerate(groups):
        st = q(max(0, g[0]["s"] - 0.04)); sid, v = scene_of(g[0]["s"])
        en = g[-1]["e"] + 0.25
        if gi + 1 < len(groups): en = min(en, groups[gi + 1][0]["s"] - 0.04)
        en = q(min(en, total))
        y = CAPY_SCENE.get(sid, CAPY[v["layout"]])
        spans, wj = [], []
        for wi, w in enumerate(g):
            wid = "cw%d_%d" % (gi, wi)
            spans.append('<span class="cw" id="%s">%s</span>' % (wid, w["disp"]))
            wj.append({"id": wid, "s": round(w["s"], 3), "hot": w["hot"]})
        html.append('<div id="cg%d" class="cg clip" data-start="%s" data-duration="%s" style="top:%dpx"><div class="gi" id="cgi%d">%s</div></div>'
                    % (gi, st, round(en - st, 4), y - 50, gi, " ".join(spans)))
        gj.append({"id": "cgi%d" % gi, "start": st, "end": en, "words": wj})
    cap = open(TPL + "/captions.html", encoding="utf-8").read()
    cap = cap.replace("@@KIT@@", kit).replace("@@GROUPS@@", "\n".join(html)).replace("@@GJSON@@", json.dumps(gj, ensure_ascii=False))
    open(out + "/compositions/captions.html", "w", encoding="utf-8").write(cap)
    vd = total
    root = f"""<!doctype html>
<html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=1080, height=1920">
<title>07 · 7 инструментов вокруг Claude Code</title>
<script src="assets/gsap.min.js"></script>
<style>
html,body{{margin:0;padding:0;background:#000}}
#main{{position:relative;width:1080px;height:1920px;overflow:hidden;background:#000}}
.scene{{position:absolute;left:0;top:0;width:1080px;height:1920px}}
#av{{position:absolute;left:0;top:0;width:1080px;height:1920px;object-fit:cover}}
</style></head>
<body>
<div id="main" data-composition-id="main" data-start="0" data-duration="{total}" data-width="1080" data-height="1920" data-fps="30">
  <video id="av" class="clip" src="assets/07v3/07v3_avatar_{ver}.mp4" data-start="0" data-duration="{total}" data-media-start="0" data-track-index="0" muted playsinline></video>
{chr(10).join(hosts)}
  <div id="h-captions" class="scene" data-composition-id="captions" data-composition-src="compositions/captions.html" data-start="0" data-duration="{total}" data-track-index="5" data-track-kind="graphics" data-width="1080" data-height="1920"></div>
  <audio id="vo" class="clip" src="assets/07v3/07v3_voice_{ver}.wav" data-start="0" data-duration="{total}" data-track-index="6" data-volume="1"></audio>
</div>
<script>window.__timelines = window.__timelines || {{}}; window.__timelines["main"] = gsap.timeline({{paused:true}});</script>
</body></html>
"""
    open(out + "/index.html", "w", encoding="utf-8").write(root)
    json.dump({"total": total, "scenes": sc, "broll": BROLL}, open(W + "/timing.json", "w"), indent=1, ensure_ascii=False)
    print("готово: %.3f с, сцен %d, групп титров %d -> %s" % (total, len(hosts), len(groups), out))


if __name__ == "__main__":
    main()
