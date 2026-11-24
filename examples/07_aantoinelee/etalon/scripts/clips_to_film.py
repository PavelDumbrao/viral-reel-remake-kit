#!/usr/bin/env python3
"""v3_base.py — склейка 11 реплик Omni в один говорящий фильм 07 v3.
Пишет base/07_talk.mp4 (1080x1920, 30 к/с, без звука, ускорение K), base/07_raw_voice.wav (натуральная скорость, под STS),
base/plan.json (места клипов в фильме) и base/words_clips.json (слова STT клипов во времени фильма)."""
import json, os, subprocess, glob
V = os.environ.get("WORK", os.getcwd())   # рабочая папка ролика
K = 1.06
PAD_IN, PAD_OUT = 0.10, 0.22
ORDER = ["A1b"] + ["A%d" % i for i in range(2, 12)]
LAST = {"A5": "надо"}           # хвост после этого слова — отсебятина Omni
os.makedirs(f"{V}/base", exist_ok=True)
def src(n): return sorted(glob.glob(f"{V}/omni*/results/{n}/*.mp4"))[-1]
def words(n):
    r = json.load(open(f"{V}/eval/{n}.json")); r = r.get("result", r)
    ws = [w for w in r["words"] if w.get("type") == "word"]
    if n in LAST:
        k = max(i for i, w in enumerate(ws) if w["text"].strip(".,") == LAST[n]); ws = ws[:k + 1]
    return ws
plan, fw, t = [], [], 0.0
for n in ORDER:
    ws = words(n); f = src(n)
    a = max(0.0, ws[0]["start"] - PAD_IN); b = ws[-1]["end"] + PAD_OUT
    fr = round((b - a) / K * 30); dur = fr / 30; slen = dur * K
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{a:.3f}", "-t", f"{slen + 0.2:.3f}", "-i", f,
                    "-vf", f"setpts=(PTS-STARTPTS)/{K},fps=30,format=yuv420p", "-frames:v", str(fr), "-an",
                    "-c:v", "libx264", "-preset", "fast", "-crf", "15", "-r", "30", "-g", "30", f"{V}/base/{n}.mp4"],
                   check=True, stdin=subprocess.DEVNULL)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{a:.3f}", "-t", f"{slen:.4f}", "-i", f, "-vn", "-ac", "1", "-ar", "44100",
                    "-af", f"afade=t=out:st={max(0, slen - 0.08):.4f}:d=0.08,apad=whole_dur={slen:.4f}", f"{V}/base/{n}.wav"],
                   check=True, stdin=subprocess.DEVNULL)
    plan.append({"id": n, "src": f, "a": round(a, 3), "b": round(a + slen, 3), "film_start": round(t, 4), "film_dur": round(dur, 4), "frames": fr})
    for w in ws:
        fw.append({"text": w["text"], "start": round(t + (w["start"] - a) / K, 3), "end": round(t + (w["end"] - a) / K, 3), "clip": n})
    t += dur
open(f"{V}/base/v.txt", "w").write("".join(f"file '{V}/base/{p['id']}.mp4'\n" for p in plan))
open(f"{V}/base/a.txt", "w").write("".join(f"file '{V}/base/{p['id']}.wav'\n" for p in plan))
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", f"{V}/base/v.txt", "-c", "copy", f"{V}/base/07_talk.mp4"], check=True)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", f"{V}/base/a.txt", "-c:a", "pcm_s16le", f"{V}/base/07_raw_voice.wav"], check=True)
json.dump({"K": K, "duration": round(t, 4), "clips": plan}, open(f"{V}/base/plan.json", "w"), indent=1)
json.dump(fw, open(f"{V}/base/words_clips.json", "w"), ensure_ascii=False, indent=0)
print("film", round(t, 2), "s; raw voice", round(t * K, 2), "s")
for p in plan: print(p["id"], p["film_start"], p["film_dur"])
