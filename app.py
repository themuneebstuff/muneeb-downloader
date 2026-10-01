#!/usr/bin/env python3
"""
Muneeb Downloader — link paste karo, video download karo.
- 1000+ sites (YouTube, TikTok, Instagram, Facebook, X, Dailymotion...)
- Original quality, koi watermark nahi (source file direct download hoti hai)
"""
import glob
import os
import threading
import uuid

from flask import Flask, jsonify, redirect, render_template_string, request, send_file, session
from yt_dlp.utils import sanitize_filename
import yt_dlp

BASE = os.path.dirname(os.path.abspath(__file__))
DL_DIR = os.path.join(BASE, "downloads")
COOKIE_FILE = os.path.join(BASE, "cookies.txt")
os.makedirs(DL_DIR, exist_ok=True)

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "muneeb-downloader-local-secret")
jobs = {}  # job_id -> {status, percent, speed, eta, title, file, error}

APP_PASSWORD = os.environ.get("DOWNLOADER_PASSWORD", "")


@app.before_request
def check_auth():
    if not APP_PASSWORD:
        return
    if request.path == "/login":
        return
    if session.get("authed"):
        return
    if request.path.startswith("/api/") and request.path != "/api/login":
        return jsonify({"ok": False, "error": "login required"}), 401
    return redirect("/login")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        data = request.get_json(silent=True) or {}
        pw = request.form.get("pw") or data.get("pw") or ""
        if pw == APP_PASSWORD:
            session["authed"] = True
            if request.is_json:
                return jsonify({"ok": True})
            return redirect("/")
        err = "Ghalat password."
    else:
        err = ""
    return render_template_string(LOGIN_PAGE, err=err)


@app.route("/api/login", methods=["POST"])
def api_login():
    if (request.json or {}).get("pw") == APP_PASSWORD and APP_PASSWORD:
        session["authed"] = True
        return jsonify({"ok": True})
    return jsonify({"ok": False}), 401


def base_opts(extra=None):
    opts = {"quiet": True, "no_warnings": True, "noplaylist": True}
    if os.path.exists(COOKIE_FILE):
        opts["cookiefile"] = COOKIE_FILE
    if extra:
        opts.update(extra)
    return opts

QUALITY_MAP = {
    "best":  ("Best / Original quality", "bv*+ba/b", None),
    "1080":  ("1080p HD", "bv*[height<=1080]+ba/b[height<=1080]/b", None),
    "720":   ("720p HD", "bv*[height<=720]+ba/b[height<=720]/b", None),
    "480":   ("480p", "bv*[height<=480]+ba/b[height<=480]/b", None),
    "audio": ("Sirf Audio (MP3)", "ba/b", "mp3"),
}


def fmt_duration(sec):
    if not sec:
        return ""
    m, s = divmod(int(sec), 60)
    h, m = divmod(m, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"


@app.route("/")
def index():
    return render_template_string(PAGE)


@app.route("/api/info", methods=["POST"])
def api_info():
    url = (request.json or {}).get("url", "").strip()
    if not url.startswith("http"):
        return jsonify({"ok": False, "error": "Sahi link paste karein (http/https)."}), 400
    try:
        with yt_dlp.YoutubeDL(base_opts({"skip_download": True})) as ydl:
            info = ydl.extract_info(url, download=False)
        return jsonify({"ok": True, "info": {
            "title": info.get("title", "Video"),
            "uploader": info.get("uploader") or info.get("channel") or "",
            "duration": fmt_duration(info.get("duration")),
            "thumbnail": info.get("thumbnail") or "",
            "site": info.get("extractor_key", ""),
        }})
    except Exception as e:
        return jsonify({"ok": False, "error": f"Video info nahi mil saki: {e}"}), 400


def download_worker(job_id, url, quality):
    label, fmt, audio_only = QUALITY_MAP.get(quality, QUALITY_MAP["best"])
    job = jobs[job_id]

    def hook(d):
        if d["status"] == "downloading":
            total = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
            done = d.get("downloaded_bytes", 0)
            job["percent"] = round(done / total * 100, 1) if total else 0
            job["speed"] = d.get("_speed_str", "").strip()
            job["eta"] = d.get("_eta_str", "").strip()
        elif d["status"] == "finished":
            job["percent"] = 100
            job["status"] = "processing"

    outtmpl = os.path.join(DL_DIR, job_id + ".%(ext)s")
    opts = base_opts({"format": fmt, "outtmpl": outtmpl,
                      "progress_hooks": [hook]})
    if audio_only:
        opts["postprocessors"] = [{"key": "FFmpegExtractAudio",
                                   "preferredcodec": "mp3",
                                   "preferredquality": "192"}]
    else:
        opts["merge_output_format"] = "mp4"

    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            title = info.get("title", "video")
        # job_id prefix hata kar asal naam lagao
        ext = ".mp3" if audio_only else ""
        if not ext:
            matches = sorted(glob.glob(os.path.join(DL_DIR, job_id + ".*")),
                             key=os.path.getmtime)
            if not matches:
                raise RuntimeError("Downloaded file nahi mili.")
            ext = os.path.splitext(matches[0])[1]
            src = matches[0]
        else:
            src = os.path.join(DL_DIR, job_id + ext)
        final = sanitize_filename(title, restricted=False)[:120] + ext
        final = final or (job_id + ext)
        os.replace(src, os.path.join(DL_DIR, final))
        job.update(status="done", file=final, percent=100)
    except Exception as e:
        job.update(status="error", error=str(e))


@app.route("/api/download", methods=["POST"])
def api_download():
    data = request.json or {}
    url = data.get("url", "").strip()
    quality = data.get("quality", "best")
    if not url.startswith("http"):
        return jsonify({"ok": False, "error": "Sahi link paste karein."}), 400
    if quality not in QUALITY_MAP:
        quality = "best"
    job_id = uuid.uuid4().hex[:12]
    jobs[job_id] = {"status": "starting", "percent": 0, "speed": "",
                    "eta": "", "title": "", "file": "", "error": ""}
    threading.Thread(target=download_worker, args=(job_id, url, quality),
                     daemon=True).start()
    return jsonify({"ok": True, "job_id": job_id})


@app.route("/api/progress/<job_id>")
def api_progress(job_id):
    job = jobs.get(job_id)
    if not job:
        return jsonify({"ok": False}), 404
    return jsonify({"ok": True, "job": job})


@app.route("/api/file/<job_id>")
def api_file(job_id):
    job = jobs.get(job_id)
    if not job or job.get("status") != "done" or not job.get("file"):
        return jsonify({"ok": False}), 404
    return send_file(os.path.join(DL_DIR, job["file"]), as_attachment=True)


@app.route("/api/cookies", methods=["POST"])
def api_cookies():
    f = request.files.get("file")
    if not f or not f.filename.endswith(".txt"):
        return jsonify({"ok": False, "error": "cookies.txt file select karein."}), 400
    f.save(COOKIE_FILE)
    return jsonify({"ok": True})


@app.route("/api/cookies", methods=["DELETE"])
def api_cookies_del():
    if os.path.exists(COOKIE_FILE):
        os.remove(COOKIE_FILE)
    return jsonify({"ok": True})


LOGIN_PAGE = """<!DOCTYPE html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Login — Muneeb Downloader</title>
<style>*{box-sizing:border-box;font-family:system-ui,sans-serif}
body{background:#0f1115;color:#e8eaf0;margin:0;min-height:100vh;display:flex;justify-content:center;align-items:center;padding:16px}
.card{background:#171a21;border:1px solid #262b36;border-radius:16px;padding:28px;max-width:360px;width:100%}
h2{margin:0 0 6px}p{color:#9aa0b0;font-size:14px}
input{width:100%;background:#0f1115;border:1px solid #2c313d;border-radius:10px;color:#fff;padding:12px;font-size:15px;margin:12px 0}
button{width:100%;background:#7c5cff;color:#fff;border:0;border-radius:10px;padding:12px;font-size:15px;cursor:pointer;font-weight:600}
.err{color:#ff6b6b;font-size:14px;min-height:20px}</style></head>
<body><div class="card"><h2>🔒 Muneeb Downloader</h2><p>Password likho:</p>
<form method="post"><input type="password" name="pw" placeholder="Password" autofocus>
<div class="err">{{ err }}</div><button type="submit">Kholo</button></form></div></body></html>"""

PAGE = """<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Muneeb Downloader</title>
<style>
*{box-sizing:border-box;font-family:system-ui,-apple-system,sans-serif}
body{background:#0f1115;color:#e8eaf0;margin:0;min-height:100vh;display:flex;justify-content:center;padding:32px 16px}
.card{background:#171a21;border:1px solid #262b36;border-radius:16px;padding:28px;max-width:560px;width:100%;height:fit-content}
h1{margin:0 0 4px;font-size:24px}h1 span{color:#7c5cff}
.sub{color:#9aa0b0;font-size:14px;margin-bottom:20px}
.row{display:flex;gap:8px}
input[type=text]{flex:1;background:#0f1115;border:1px solid #2c313d;border-radius:10px;color:#fff;padding:12px;font-size:15px}
input:focus{outline:none;border-color:#7c5cff}
button{background:#7c5cff;color:#fff;border:0;border-radius:10px;padding:12px 20px;font-size:15px;cursor:pointer;font-weight:600}
button:disabled{opacity:.5;cursor:wait}
button.ghost{background:#23262f}
#info{display:none;margin-top:20px;background:#0f1115;border:1px solid #262b36;border-radius:12px;padding:14px}
#info img{width:100%;border-radius:8px;max-height:220px;object-fit:cover}
#info h3{margin:10px 0 4px;font-size:16px}
#info p{margin:0;color:#9aa0b0;font-size:13px}
.qrow{display:flex;gap:8px;margin-top:14px}
select{flex:1;background:#0f1115;border:1px solid #2c313d;border-radius:10px;color:#fff;padding:12px;font-size:14px}
#prog{display:none;margin-top:18px}
.bar{height:10px;background:#23262f;border-radius:6px;overflow:hidden}
.bar>div{height:100%;width:0;background:#7c5cff;transition:width .3s}
#ptext{font-size:13px;color:#9aa0b0;margin-top:8px}
#done{display:none;margin-top:18px;text-align:center}
#done a{display:inline-block;background:#22c55e;color:#04120a;text-decoration:none;font-weight:700;padding:12px 28px;border-radius:10px;margin-top:8px}
.err{color:#ff6b6b;font-size:14px;margin-top:12px;display:none}
.note{margin-top:22px;font-size:12px;color:#6b7280;line-height:1.6}
</style></head><body><div class="card">
<h1><span>Muneeb</span> Downloader</h1>
<div class="sub">Link paste karein — video original quality mein, bina watermark ke download karein.</div>
<div class="row">
<input id="url" type="text" placeholder="Video ka link yahan paste karein...">
<button id="go" onclick="getInfo()">Dekho</button>
</div>
<div id="info">
<img id="thumb" src=""><h3 id="title"></h3><p id="meta"></p>
<div class="qrow">
<select id="q">
<option value="best">Best / Original quality</option>
<option value="1080">1080p HD</option>
<option value="720">720p HD</option>
<option value="480">480p</option>
<option value="audio">Sirf Audio (MP3)</option>
</select>
<button onclick="startDl()">Download</button>
</div></div>
<div id="prog"><div class="bar"><div id="fill"></div></div><div id="ptext"></div></div>
<div id="done"><div>✅ Download complete!</div><a id="dlink" href="#">File Download Karein</a>
<div style="margin-top:12px"><button class="ghost" onclick="location.reload()">Nayi Video</button></div></div>
<div class="err" id="err"></div>
<div class="note">1000+ sites supported: YouTube, TikTok, Instagram, Facebook, X, Dailymotion aur bohat si.<br>
Watermark is liye nahi aata kyunke original source file download hoti hai.</div>
<details style="margin-top:14px;font-size:13px;color:#9aa0b0">
<summary style="cursor:pointer;color:#c9cdd8">Login wali / bot-check wali videos? (cookies)</summary>
<div style="margin-top:8px;line-height:1.7">
Agar YouTube "sign in to confirm you're not a bot" kahe ya Instagram private video ho, to apne browser se cookies export karke yahan lagao:<br>
1. Chrome mein <b>"Get cookies.txt LOCALLY"</b> extension install karo<br>
2. youtube.com kholo (logged in), extension se <b>cookies.txt</b> export karo<br>
3. Neeche file select karke <b>Cookies Lagao</b> dabao — ek dafa lagane ke baad sab downloads isi se honge.
<div class="row" style="margin-top:8px">
<input id="ck" type="file" accept=".txt" style="font-size:13px">
<button onclick="upCk()" style="padding:10px 14px;font-size:13px">Cookies Lagao</button>
<button class="ghost" onclick="delCk()" style="padding:10px 14px;font-size:13px">Hatao</button>
</div><div id="ckmsg" style="margin-top:6px"></div></div></details>
<script>
async function upCk(){const f=document.getElementById('ck').files[0];if(!f)return;
 const fd=new FormData();fd.append('file',f);
 const r=await fetch('/api/cookies',{method:'POST',body:fd});const d=await r.json();
 document.getElementById('ckmsg').textContent=d.ok?'✅ Cookies lag gayi!':'❌ '+d.error;}
async function delCk(){await fetch('/api/cookies',{method:'DELETE'});
 document.getElementById('ckmsg').textContent='Cookies hata di gayin.';}
</script>
</div>
<script>
let jobId=null,timer=null;
async function getInfo(){
 const url=document.getElementById('url').value.trim(),err=document.getElementById('err');
 err.style.display='none';document.getElementById('go').disabled=true;
 try{const r=await fetch('/api/info',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({url})});
 const d=await r.json();if(!d.ok)throw new Error(d.error);
 document.getElementById('thumb').src=d.info.thumbnail;document.getElementById('title').textContent=d.info.title;
 document.getElementById('meta').textContent=(d.info.uploader?d.info.uploader+' • ':'')+(d.info.duration||'');
 document.getElementById('info').style.display='block';
 }catch(e){err.textContent=e.message;err.style.display='block';}
 document.getElementById('go').disabled=false;}
async function startDl(){
 const url=document.getElementById('url').value.trim(),q=document.getElementById('q').value;
 const r=await fetch('/api/download',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({url,quality:q})});
 const d=await r.json();if(!d.ok){const e=document.getElementById('err');e.textContent=d.error;e.style.display='block';return;}
 jobId=d.job_id;document.getElementById('prog').style.display='block';
 timer=setInterval(poll,800);}
async function poll(){
 const r=await fetch('/api/progress/'+jobId);const d=await r.json();if(!d.ok)return;
 const j=d.job;document.getElementById('fill').style.width=j.percent+'%';
 document.getElementById('ptext').textContent=j.status==='processing'?'File taiyaar ho rahi hai...':(j.percent+'% • '+(j.speed||'')+' • '+(j.eta||''));
 if(j.status==='done'){clearInterval(timer);document.getElementById('prog').style.display='none';
  document.getElementById('done').style.display='block';document.getElementById('dlink').href='/api/file/'+jobId;}
 if(j.status==='error'){clearInterval(timer);const e=document.getElementById('err');e.textContent='Error: '+j.error;e.style.display='block';}}
</script></body></html>"""

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5050))
    print(f"Muneeb Downloader chal raha hai: http://localhost:{port}")
    if APP_PASSWORD:
        print("Password protection ON hai.")
    app.run(host="0.0.0.0", port=port)
