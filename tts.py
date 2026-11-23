#!/usr/bin/env python3
"""Legge jobs.json {"batch": ..., "jobs": [{"name": "a-xxx.mp3", "text": "..."}]} e scrive out/*.mp3 + out/durations.json."""
import json, subprocess, sys, wave
from pathlib import Path
from piper import PiperVoice

jobs = json.loads(Path(sys.argv[1]).read_text())
out = Path(sys.argv[2]); out.mkdir(exist_ok=True)
voice = PiperVoice.load("voci/it_IT-paola-medium.onnx")
durs = {}
for j in jobs.get("jobs", []):
    wav = out / (j["name"] + ".wav")
    try:
        with wave.open(str(wav), "wb") as w:
            voice.synthesize_wav(j["text"], w)
        with wave.open(str(wav), "rb") as w:
            dur = w.getnframes() / w.getframerate()
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(wav), "-ac", "1", "-ar", "22050",
                        "-codec:a", "libmp3lame", "-b:a", "32k", str(out / j["name"])], check=True)
        durs[j["name"]] = round(dur, 1)
    except Exception as e:
        print("non riuscito:", j["name"], e, file=sys.stderr)
    finally:
        wav.unlink(missing_ok=True)
(out / "durations.json").write_text(json.dumps({"batch": jobs.get("batch"), "durations": durs}))
print(f"{len(durs)} audio generati")
