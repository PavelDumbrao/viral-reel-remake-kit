#!/usr/bin/env python3
"""Выровнять тембр куска голоса под весь ролик (когда слова верные, но кусок звучит «другим человеком»).

  python3 scripts/timbre_match.py track.wav T0 T1 out.wav [--ref A B]

Считает средний спектр голоса в эталонном отрезке (--ref, по умолчанию весь ролик кроме куска) и в куске T0–T1,
подбирает поправку по третьоктавам (предел ±9 дБ, ниже 80 Гц не трогает), выравнивает громкость и вклеивает с плавными
краями. Края T0/T1 ставьте в паузы. Нужны ffmpeg и numpy.
"""
import argparse, subprocess, numpy as np
SR, N, H = 44100, 2048, 512
def load(p):
    o = subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-i", p, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(o, np.float32).astype(float)
win = np.hanning(N)
def stft(x): return np.array([np.fft.rfft(win * x[i:i + N]) for i in range(0, len(x) - N, H)])
def istft(S, L):
    y = np.zeros(L + N); w = np.zeros(L + N)
    for k, s in enumerate(S): i = k * H; y[i:i + N] += win * np.fft.irfft(s, N); w[i:i + N] += win ** 2
    return (y / np.maximum(w, 1e-6))[:L]
def ltas(x):
    S = np.abs(stft(x)); e = (S ** 2).sum(1); S = S[e > np.percentile(e, 40)]; return np.sqrt((S ** 2).mean(0))
def vr(x):
    v = x[np.abs(x) > 0.02]; return float(np.sqrt(np.mean(v ** 2))) if len(v) else 1e-9
ap = argparse.ArgumentParser(); ap.add_argument("track"); ap.add_argument("t0", type=float); ap.add_argument("t1", type=float); ap.add_argument("out")
ap.add_argument("--ref", nargs=2, type=float)
a = ap.parse_args()
V = load(a.track); i0, i1 = int(a.t0 * SR), int(a.t1 * SR)
ref = V[int(a.ref[0] * SR):int(a.ref[1] * SR)] if a.ref else np.concatenate([V[:i0], V[i1:]])
seg = V[i0:i1]; f = np.fft.rfftfreq(N, 1 / SR); ratio = ltas(ref) / np.maximum(ltas(seg), 1e-9); sm = np.ones_like(ratio)
for i, fc in enumerate(f):
    if fc >= 80:
        m = (f > fc / 2 ** (1 / 6)) & (f < fc * 2 ** (1 / 6)); sm[i] = np.exp(np.mean(np.log(ratio[m])))
sm = np.clip(sm, 10 ** (-9 / 20), 10 ** (9 / 20))
y = istft(stft(seg) * sm, len(seg)); y *= vr(V[max(0, i0 - 4 * SR):i0]) / vr(y)
fd = int(0.015 * SR); w = np.ones(i1 - i0); w[:fd] = np.linspace(0, 1, fd); w[-fd:] = np.linspace(1, 0, fd)
V[i0:i1] = V[i0:i1] * (1 - w) + y * w
subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-", a.out],
               input=np.clip(V, -1, 1).astype(np.float32).tobytes(), check=True)
print("поправка, дБ:", {fc: round(float(20 * np.log10(sm[np.argmin(abs(f - fc))])), 1) for fc in (150, 300, 600, 1200, 2500, 5000, 8000)})
