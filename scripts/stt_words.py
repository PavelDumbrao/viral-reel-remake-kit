#!/usr/bin/env python3
"""Речь ролика → слова с таймингами (ElevenLabs Scribe v2).

  python3 scripts/stt_words.py <аудио или видео> <out.json> [--lang ru|en]

Пишет {"text": "...", "words": [{"text", "start", "end"}]} — этот файл понимает
scripts/frames_05s.py --words. Ключ берётся из ELEVENLABS_API_KEY (.env или окружение).
Видео сначала превращается в mp3 через ffmpeg (только звук).
Только стандартная библиотека Python + ffmpeg.
"""
import argparse, json, os, subprocess, sys, tempfile, urllib.request, uuid

API = "https://api.elevenlabs.io/v1/speech-to-text"


def load_env(path=".env"):
    if os.path.exists(path):
        for line in open(path, encoding="utf-8"):
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def to_mp3(src, tmpdir):
    if src.lower().endswith((".mp3", ".wav", ".m4a")):
        return src
    out = os.path.join(tmpdir, "audio.mp3")
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", src, "-vn", "-ac", "1",
                    "-ar", "44100", "-b:a", "128k", out], check=True)
    return out


def multipart(fields, file_field, file_path):
    boundary = uuid.uuid4().hex
    parts = []
    for k, v in fields.items():
        parts.append(f'--{boundary}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode())
    name = os.path.basename(file_path)
    parts.append(f'--{boundary}\r\nContent-Disposition: form-data; name="{file_field}"; filename="{name}"\r\n'
                 f'Content-Type: application/octet-stream\r\n\r\n'.encode())
    parts.append(open(file_path, "rb").read())
    parts.append(f"\r\n--{boundary}--\r\n".encode())
    return b"".join(parts), boundary


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("out")
    ap.add_argument("--lang", default="ru", help="язык речи: ru, en …")
    a = ap.parse_args()
    load_env()
    key = os.environ.get("ELEVENLABS_API_KEY")
    if not key:
        sys.exit("Нет ELEVENLABS_API_KEY в .env")
    with tempfile.TemporaryDirectory() as tmp:
        audio = to_mp3(a.src, tmp)
        body, boundary = multipart({"model_id": "scribe_v2", "language_code": a.lang,
                                    "timestamps_granularity": "word"}, "file", audio)
        req = urllib.request.Request(API, data=body, method="POST", headers={
            "xi-api-key": key, "Content-Type": f"multipart/form-data; boundary={boundary}"})
        try:
            with urllib.request.urlopen(req, timeout=600) as r:
                data = json.load(r)
        except urllib.error.HTTPError as e:
            sys.exit(f"ElevenLabs ответил {e.code}: {e.read()[:300].decode('utf-8', 'replace')}")
    words = [{"text": w["text"], "start": round(w["start"], 3), "end": round(w["end"], 3)}
             for w in data.get("words", []) if w.get("type", "word") == "word"]
    json.dump({"text": data.get("text", ""), "words": words}, open(a.out, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print(f"слов: {len(words)}, длина речи: {words[-1]['end'] if words else 0} с → {a.out}")


if __name__ == "__main__":
    main()
