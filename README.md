# Muneeb Downloader

Paste a link — download videos in **original quality**, with **no watermark**.
YouTube, TikTok, Instagram, Facebook, X, Dailymotion and 1000+ sites supported (via yt-dlp).

## Run on your own computer (first time only)

**Windows:**
1. Install Python from [python.org](https://www.python.org/downloads/) (during install, make sure **"Add python.exe to PATH"** is ticked).
2. Install ffmpeg from [ffmpeg.org](https://www.ffmpeg.org/download.html) (required for best quality + MP3).
3. Extract the zip, then double-click **start.bat**.
4. It opens in your browser at `http://localhost:5050` — if not, open that address yourself.

**Mac/Linux:**
1. Install Python 3 and ffmpeg.
2. Extract the zip and run in a terminal: `bash start.sh`
3. Open in your browser: `http://localhost:5050`

> First launch can take 1–2 minutes (one-time setup). After that, just run the file and use it.

## How to use

1. Copy a video link, paste it in the box, press **Fetch**.
2. You'll see the thumbnail, title and duration.
3. Pick a quality (**Best / Original quality** = as it was uploaded).
4. Press **Download** — progress shows below.
5. When complete, the **Download File** button appears.

Downloaded files are saved in the `downloads` folder.

## If a video won't download (bot-check / login)

Some sites (especially YouTube) sometimes say "confirm you're not a bot". Fix:

1. Install the **"Get cookies.txt LOCALLY"** extension in Chrome.
2. Open youtube.com (stay logged in to your account).
3. Export **cookies.txt** with the extension.
4. In the downloader page, open the "Login-only / bot-check videos? (cookies)" section, select the file and press **Apply Cookies**.
5. Once applied, all downloads will work.

## Good to know

- No watermark, because the original source file is downloaded directly — nothing is re-encoded.
- **Best / Original quality** gives you exactly the quality that was uploaded.
- Only download videos you have the right to (your own, copyright-free, or permitted). Downloading/re-uploading others' content without permission may violate their terms.
- Cookies may be required for private or login-only videos.

---

## Run it ONLINE (use from anywhere, e.g. your phone)

If you want the tool reachable not just on your home computer but **from anywhere via your phone**, use Cloudflare Tunnel. It's **completely free** and needs no port-forwarding or static IP.

**Bonus:** the link is served from your own computer, so YouTube/TikTok bot-checks usually don't trigger (server company IPs are the ones that get blocked).

### Setup (one time)

1. Download **cloudflared** for your system from:
   https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/
2. Rename the downloaded file:
   - Windows: `cloudflared.exe`
   - Mac/Linux: `cloudflared` (then run `chmod +x cloudflared`)
3. Put it in this folder (next to `tunnel.bat` / `tunnel.sh`).

### Run

- **Windows:** double-click `tunnel.bat`.
- **Mac/Linux:** in a terminal run `bash tunnel.sh`.

After a few seconds a **password** appears on screen (note it down) and below it a link ending in `trycloudflare.com` — **that's your public link**. Open it in your phone's browser, enter the password, done!

**Remember:**
- The link works while this window stays open. To stop, close the window (or Ctrl+C).
- Every run creates a new password and a new link — old links stop working.
- Your computer must stay on and connected while you use it.

### Want 24/7 online (even with your computer off)?

You need a VPS (e.g. Contabo/Hetzner, ~$5/month). Install from `requirements.txt`, set `DOWNLOADER_PASSWORD`, and run the app. One caveat: YouTube often bot-checks VPS IPs, so you may need to apply cookies for YouTube.

---

## Deploy online (free hosting)

### Render (Docker)

This repo includes a `Dockerfile` and `render.yaml`. Create a Blueprint from this repo on Render (free plan) — it sets a generated `DOWNLOADER_PASSWORD` automatically. Note: Render requires card verification even for the free tier (temporary $1 authorization, no charge).

### Hugging Face Spaces (Docker, no card required)

1. Create a new Space with the **Docker** SDK.
2. Upload `app.py`, `requirements.txt`, `Dockerfile` and a Space `README.md` (with `sdk: docker` frontmatter).
3. In Space **Settings → Variables and secrets**, add a secret named `DOWNLOADER_PASSWORD`.
4. The Space builds and gives you a public URL like `https://<user>-muneeb-downloader.hf.space`.

Note: free hosting tiers may sleep after inactivity (first visit wakes them up), and datacenter IPs can trigger YouTube bot-checks — use the in-app cookies feature if that happens.
