#!/usr/bin/env python3
"""Вклеить новый дубль фразы в голосовую дорожку ролика вместо испорченной.

  python3 scripts/fix_phrase.py track.wav take.mp3 T0 T1 out.wav [--clear A B]

track.wav — голос ролика; take.mp3 — та же фраза заново (ваш клон в ElevenLabs, ударение можно поставить знаком U+0301:
«рефере́нсы»); T0–T1 — где фраза звучит в ролике (секунды, от начала первого слова до конца последнего);
--clear A B — что заглушить в старой дорожке (по умолчанию T0−0,06 … T1+0,15, края — в тишине).
Дубль обрезается по тишине, растягивается под слот (не больше чем на ±8–10 %, иначе слышно), громкость — как у речи
перед фразой. Длинную фразу с паузами лучше вклеивать кусками по её паузам. Нужны ffmpeg и numpy.
"""
import argparse, subprocess, numpy as np
SR = 44100
def load(p):
    o = subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-i", p, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(o, np.float32).copy()
def tempo(x, r):
    ch = []
    while r > 2: ch.append("atempo=2"); r /= 2
    while r < 0.5: ch.append("atempo=0.5"); r /= 0.5
    ch.append(f"atempo={r:.5f}")
    o = subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-", "-af", ",".join(ch), "-f", "f32le", "-"],
                       input=x.astype(np.float32).tobytes(), capture_output=True, check=True).stdout
    return np.frombuffer(o, np.float32).copy()
def vr(x):
    v = x[np.abs(x) > 0.02]; return float(np.sqrt(np.mean(v ** 2))) if len(v) else 1e-9
ap = argparse.ArgumentParser(); ap.add_argument("track"); ap.add_argument("take"); ap.add_argument("t0", type=float); ap.add_argument("t1", type=float)
ap.add_argument("out"); ap.add_argument("--clear", nargs=2, type=float); ap.add_argument("--max-stretch", type=float, default=0.10)
a = ap.parse_args()
V, T = load(a.track), load(a.take)
nz = np.where(np.abs(T) > 0.01)[0]; T = T[max(0, nz[0] - int(0.07 * SR)):nz[-1] + int(0.12 * SR)]
r = min(1 + a.max_stretch, max(1 - a.max_stretch, len(T) / SR / (a.t1 - a.t0)))
T = tempo(T, r); T *= vr(V[int((a.t0 - 3) * SR):int(a.t0 * SR)]) / vr(T)
c0, c1 = a.clear or (a.t0 - 0.06, a.t1 + 0.15); f = int(0.012 * SR)
i0, i1 = int(c0 * SR), int(c1 * SR)
V[i0:i0 + f] *= np.linspace(1, 0, f); V[i0 + f:i1 - f] = 0; V[i1 - f:i1] *= np.linspace(0, 1, f)
s = int(a.t0 * SR); n = min(len(T), len(V) - s); T = T[:n]; T[:f] *= np.linspace(0, 1, f); T[-f:] *= np.linspace(1, 0, f)
V[s:s + n] += T
subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-", a.out], input=np.clip(V, -1, 1).tobytes(), check=True)
print(f"вклеено: растяжение {r:.3f}, слот {a.t0}–{a.t1} с → {a.out}")
