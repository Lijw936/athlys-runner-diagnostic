"""Best-effort public YouTube audio capture. Spoken text must be verified before publication."""
from __future__ import annotations
import datetime as dt
import json
import os
from pathlib import Path
import subprocess
import sys
import traceback

OUTPUT=Path("output")
OUTPUT.mkdir(exist_ok=True)
URL=os.getenv("VIDEO_URL","https://www.youtube.com/watch?v=6NS1eB8Agsg")
SECONDS=max(30,min(1500,int(os.getenv("CAPTURE_SECONDS","600"))))
MODEL=os.getenv("WHISPER_MODEL","base")
if MODEL not in {"tiny","base","small"}: raise ValueError("Invalid model")
STAMP=dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
LOG=OUTPUT/f"status-{STAMP}.json"
REPORT=OUTPUT/f"report-{STAMP}.md"
AUDIO=OUTPUT/f"audio-{STAMP}.wav"
status={"video":URL,"checked_utc":STAMP,"capture_seconds":SECONDS,"audio_captured":False,"transcript_available":False,"errors":[]}

def call(args,timeout):
    return subprocess.run(args,text=True,capture_output=True,timeout=timeout,check=False)

def main():
    fetch=call(["yt-dlp","--no-playlist","--no-warnings","-f","bestaudio/best","--get-url",URL],90)
    if fetch.returncode or not fetch.stdout.strip():
        raise RuntimeError("yt-dlp failed: "+fetch.stderr[-1200:])
    stream=fetch.stdout.strip().splitlines()[-1]
    ff=call(["ffmpeg","-nostdin","-hide_banner","-loglevel","error","-y","-i",stream,"-t",str(SECONDS),"-vn","-ac","1","-ar","16000",str(AUDIO)],SECONDS+120)
    if ff.returncode or not AUDIO.exists() or AUDIO.stat().st_size<32000:
        raise RuntimeError("ffmpeg failed: "+ff.stderr[-1200:])
    status["audio_captured"]=True
    from faster_whisper import WhisperModel
    engine=WhisperModel(MODEL,device="cpu",compute_type="int8")
    segments,_=engine.transcribe(str(AUDIO),language="fr",beam_size=5,vad_filter=True,condition_on_previous_text=False)
    rows=[{"start_s":round(s.start,2),"end_s":round(s.end,2),"text":s.text.strip()} for s in segments if s.text.strip()]
    status["transcript_available"]=bool(rows)
    (OUTPUT/f"transcript-{STAMP}.json").write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding="utf-8")
    (OUTPUT/f"transcript-{STAMP}.txt").write_text("\n".join(f"[{int(s['start_s']//60):02d}:{int(s['start_s']%60):02d}] {s['text']}" for s in rows),encoding="utf-8")
    REPORT.write_text("# Transcription provisoire - vérification éditoriale obligatoire\n\nSource : "+URL+"\n\nCapture UTC : "+STAMP+"\n\nLes horodatages sont relatifs à la capture et non au début de la conférence. La reconnaissance vocale peut se tromper ; aucune identité d'intervenant ni citation n'est vérifiée.\n\n"+"\n".join(f"- [{int(s['start_s']//60):02d}:{int(s['start_s']%60):02d}] {s['text']}" for s in rows)+"\n",encoding="utf-8")

try: main()
except Exception as e:
    status["errors"].append(str(e))
    REPORT.write_text("# Capture infructueuse\n\nAucun propos vérifiable recueilli.\n\nErreur : "+str(e)+"\n",encoding="utf-8")
    traceback.print_exc(file=sys.stderr)
    sys.exit(1)
finally:
    LOG.write_text(json.dumps(status,ensure_ascii=False,indent=2),encoding="utf-8")
