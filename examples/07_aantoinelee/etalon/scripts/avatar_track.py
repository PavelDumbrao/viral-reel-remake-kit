#!/usr/bin/env python3
"""p_avatar.py <ver> — видеоряд аватара пробы 07 (первые ~14 с). Реплика L01 — мастер C, L02 — мастер W (одна реплика = одна крупность).
Кроп говорящего клипа ≤ ×1,2, без unsharp; низ сплита — вырезка 1:1 (1080x810) без увеличения."""
import json, os, subprocess, sys
V = os.environ.get("WORK", os.getcwd())   # рабочая папка ролика; ver = sys.argv[1]
T = json.load(open(V + "/om/timing.json")); TALK = V + "/base/07_talk.mp4"
PLAN = json.load(open(V + "/base/plan.json"))
RB = {"hands": V + "/broll_hands.mp4", "laptop": V + "/broll_laptop.mp4"}
import collections
FACE = collections.defaultdict(lambda: (0.506, 0.381))
ENC = ["-c:v", "libx264", "-crf", "16", "-preset", "medium", "-pix_fmt", "yuv420p", "-r", "30", "-g", "30", "-an"]
def clip_at(t):
    for c in PLAN["clips"]:
        if c["film_start"] - 1e-6 <= t < c["film_start"] + c["film_dur"]: return c["id"]
    return PLAN["clips"][-1]["id"]
def zoom(z, fx, fy, place):
    w = 1 / z; x0 = min(max(fx - w / 2, 0), 1 - w); y0 = min(max(fy - place * w, 0), 1 - w)
    return "crop=iw*%.5f:ih*%.5f:iw*%.5f:ih*%.5f,scale=1080:1920:flags=lanczos" % (w, w, x0, y0)
tmp = V + "/avf_" + ver; os.makedirs(tmp, exist_ok=True); segs = []
for k, (sid, v) in enumerate(T["scenes"].items()):
    n = round(v["end"] * 30) - round(v["start"] * 30); f = "%s/%02d_%s.mp4" % (tmp, k, sid); lay = v["layout"]
    cid = clip_at(v["start"] + 0.01); fx, fy = FACE[cid]
    if lay in ("SP", "FW", "FC"):
        if lay == "SP":     # 1:1 без увеличения: окно 1080x810 вокруг головы
            y0 = max(0, int(fy * 1920 - 0.52 * 810)); vf = "crop=1080:810:0:%d,pad=1080:1920:0:1110:black" % y0
        elif lay == "FW":
            vf = "scale=1080:1920"                       # ×1,0
        else:
            vf = zoom(1.2, fx, fy, 0.37)
        cmd = ["ffmpeg", "-v", "error", "-y", "-ss", "%.4f" % v["start"], "-i", TALK, "-vf", "fps=30," + vf + ",tpad=stop_mode=clone:stop_duration=2,setsar=1", "-frames:v", str(n)] + ENC + [f]
    elif lay == "BR":
        r, off, mode = T["broll"][sid]
        cmd = ["ffmpeg", "-v", "error", "-y", "-ss", "%.4f" % off, "-i", RB[r], "-vf", "fps=30,scale=1080:1920:flags=lanczos,setsar=1", "-frames:v", str(n)] + ENC + [f]
    else:
        cmd = ["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "color=c=black:s=1080x1920:r=30", "-frames:v", str(n)] + ENC + [f]
    subprocess.run(cmd, check=True, stdin=subprocess.DEVNULL); segs.append(f)
open(tmp + "/list.txt", "w").write("".join("file '%s'\n" % s for s in segs))
out = V + "/om/proj/assets/07v3/07v3_avatar_%s.mp4" % ver
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", tmp + "/list.txt", "-c", "copy", "-movflags", "+faststart", out], check=True)
print(out, subprocess.check_output(["ffprobe", "-v", "error", "-count_frames", "-select_streams", "v", "-show_entries", "stream=nb_read_frames", "-of", "csv=p=0", out]).decode().strip(), "кадров; ждали", round(T["total"] * 30))
