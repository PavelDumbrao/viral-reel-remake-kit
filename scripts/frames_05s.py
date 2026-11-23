#!/usr/bin/env python3
"""Watch a video the way Pavel asked: a frame every 0.5 s, each labelled with its time and the
word being spoken at that instant, tiled into contact sheets.

  python3 -I frames_05s.py video.mp4 out_dir [--words transcript.json] [--start S] [--end E]
                           [--step 0.5] [--width 270] [--cols 4] [--rows 3]

--words accepts {"words":[{text,start,end}]} (WhisperX / HyperFrames), a bare list of the same,
or a video-editing *.takes.tsv (start, end, status, text: the island's text is shown).
Writes out_dir/sheet_NN.jpg (cols x rows frames each) and out_dir/index.tsv (t, words, frame).
"""
import argparse, glob, json, os, shutil, subprocess, sys, tempfile

ap = argparse.ArgumentParser()
ap.add_argument('video')
ap.add_argument('out')
ap.add_argument('--words')
ap.add_argument('--start', type=float, default=0.0)
ap.add_argument('--end', type=float)
ap.add_argument('--step', type=float, default=0.5)
ap.add_argument('--width', type=int, default=270)
ap.add_argument('--cols', type=int, default=4)
ap.add_argument('--rows', type=int, default=3)
a = ap.parse_args()

FONT = next((f for f in ('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
                         '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
                         '/System/Library/Fonts/Supplemental/Arial Bold.ttf',
                         '/Library/Fonts/Arial Unicode.ttf') if os.path.exists(f)), None)


def run(cmd):
    subprocess.run(cmd, check=True, capture_output=True)


def load_words(path):
    if not path:
        return []
    if path.endswith('.tsv'):
        out = []
        for line in open(path, encoding='utf-8'):
            p = line.rstrip('\n').split('\t')
            if len(p) >= 4 and not line.startswith('#') and p[2] != '-':
                try:
                    out.append((float(p[0]), float(p[1]), f'[{p[2]}] {p[3]}'))
                except ValueError:
                    pass
        return out
    d = json.load(open(path, encoding='utf-8'))
    ws = d['words'] if isinstance(d, dict) else d
    return [(float(w['start']), float(w['end']), w['text']) for w in ws if 'start' in w]


words = load_words(a.words)
dur = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0',
                            a.video], capture_output=True, text=True, check=True).stdout.strip())
end = min(a.end or dur, dur)
os.makedirs(a.out, exist_ok=True)
tmp = tempfile.mkdtemp(prefix='f05-')
try:
    times, t = [], a.start
    while t < end - 1e-6:
        times.append(round(t, 3))
        t += a.step
    rows = []
    # Один проход ffmpeg вместо запуска на каждый кадр: 611 кадров 1,5 мин против 18 мин (08.11)
    run(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-ss', f'{a.start}', '-t', f'{end - a.start}', '-i', a.video,
         '-vf', f'fps=fps=1/{a.step}:round=near,scale={a.width}:-2', '-q:v', '3', os.path.join(tmp, 'r%05d.jpg')])
    from PIL import Image, ImageDraw, ImageFont
    font = ImageFont.truetype(FONT, 15) if FONT else None
    raw = sorted(glob.glob(os.path.join(tmp, 'r*.jpg')))
    if abs(len(raw) - len(times)) > 1:
        sys.exit(f'кадров {len(raw)}, ожидалось {len(times)}')
    times = times[:len(raw)]
    for i, t in enumerate(times):
        spoken = [w for s, e, w in words if s - 0.05 <= t <= e + 0.05]
        label = f'{t:6.2f}s' + (('  ' + ' '.join(spoken))[:34] if spoken else ('  —' if words else ''))
        im = Image.open(raw[i]).convert('RGB')
        if font:
            d = ImageDraw.Draw(im, 'RGBA')
            d.rectangle([0, im.height - 28, im.width, im.height], fill=(0, 0, 0, 184))
            d.text((6, im.height - 22), label, font=font, fill=(255, 255, 255, 255))
        im.save(os.path.join(tmp, f'f{i:05d}.jpg'), quality=88)
        rows.append((t, ' '.join(spoken), f'f{i:05d}.jpg'))
    per = a.cols * a.rows
    for old in glob.glob(os.path.join(a.out, 'sheet_*.jpg')):
        os.remove(old)
    for n in range(0, len(times), per):
        batch = sorted(glob.glob(os.path.join(tmp, 'f*.jpg')))[n:n + per]
        sub = os.path.join(tmp, f'b{n}')
        os.makedirs(sub)
        for k, f in enumerate(batch):
            shutil.copy(f, os.path.join(sub, f'{k:03d}.jpg'))
        run(['ffmpeg', '-v', 'error', '-y', '-framerate', '1', '-i', os.path.join(sub, '%03d.jpg'),
             '-vf', f'tile={a.cols}x{a.rows}:padding=4:color=black', '-frames:v', '1',
             os.path.join(a.out, f'sheet_{n // per:02d}.jpg')])
    with open(os.path.join(a.out, 'index.tsv'), 'w', encoding='utf-8') as f:
        f.write('t\twords\tframe\n')
        for t, w, fr in rows:
            f.write(f'{t:.2f}\t{w}\t{fr}\n')
    print(f'{len(times)} frames every {a.step}s ({a.start:.1f}-{end:.1f}s) -> '
          f'{(len(times) + per - 1) // per} sheet(s) in {a.out}' + ('' if FONT else ' (no font: unlabelled)'))
finally:
    shutil.rmtree(tmp, ignore_errors=True)
