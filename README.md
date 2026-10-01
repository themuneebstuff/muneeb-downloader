# Muneeb Downloader

Link paste karo — video **original quality** mein, **bina watermark** ke download karo.
YouTube, TikTok, Instagram, Facebook, X, Dailymotion aur 1000+ sites supported.

## Apne computer par kaise chalana hai (sirf pehli dafa)

**Windows:**
1. [python.org](https://www.python.org/downloads/) se Python install karo (install ke waqt **"Add python.exe to PATH"** tick zaroor karna).
2. [ffmpeg.org](https://www.ffmpeg.org/download.html) se ffmpeg install karo (best quality + MP3 ke liye zaroori hai).
3. Is zip ko extract karo, phir **start.bat** par double-click karo.
4. Browser mein khud khul jayega: `http://localhost:5050` — agar na khule to khud ye address likh kar kholo.

**Mac/Linux:**
1. Python 3 aur ffmpeg install karo.
2. Zip extract karke terminal mein: `bash start.sh`
3. Browser mein kholo: `http://localhost:5050`

> Pehli dafa start hone mein 1-2 minute lag sakte hain (setup hota hai). Uske baad bas file chalao aur use karo.

## Kaise use karna hai

1. Video ka link copy karke box mein paste karo, **Dekho** dabao.
2. Video ki photo, naam aur duration nazar aayegi.
3. Quality select karo (**Best / Original quality** = jaisi upload hui thi waisi).
4. **Download** dabao — neeche progress nazar aayegi.
5. Complete hote hi **File Download Karein** ka button aayega.

Download ki hui files `downloads` folder mein save hoti hain.

## Agar koi video download na ho (bot-check / login)

Kuch sites (khaas taur par YouTube) kabhi "confirm you're not a bot" kehti hain. Iska hal:

1. Chrome mein **"Get cookies.txt LOCALLY"** extension install karo.
2. youtube.com kholo (apne account se logged in raho).
3. Extension se **cookies.txt** export karo.
4. Downloader page par neeche "Login wali / bot-check wali videos?" wala section kholo, file select karke **Cookies Lagao** dabao.
5. Ek dafa lagane ke baad sab downloads theek honge.

## Zaroori baatein

- Watermark is liye nahi aata kyunke original source file download hoti hai — koi dobara encoding nahi hoti.
- **Best / Original quality** select karne par wohi quality milegi jo upload hui thi.
- Sirf wohi videos download karo jinka tumhe haq hai (apni videos, copyright-free ya ijazat wali). Dosron ka content bina ijazat download/re-upload karna unki terms ke khilaf ho sakta hai.
- Private ya login-only videos ke liye cookies lagana zaroori ho sakta hai.


---

## Internet par ONLINE chalana (kahin se bhi use karo)

Agar tum chahte ho ke tool sirf ghar ke computer par nahi, balkay **phone se kahin se bhi** khul jaye, to Cloudflare Tunnel use karo. Ye **bilkul free** hai aur koi port-forwarding ya static IP nahi chahiye.

**Faida:** Link tumhare apne computer se banegi, is liye YouTube/TikTok ka bot-check bhi nahi aayega (server companies ke IPs par aksar block lagta hai).

### Tareeqa (ek dafa setup)

1. Is page se apne system ke hisab se **cloudflared** download karo:
   https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/
2. Download ki hui file ka naam badal kar rakho:
   - Windows: `cloudflared.exe`
   - Mac/Linux: `cloudflared` (phir `chmod +x cloudflared` chalao)
3. Us file ko isi folder mein rakho (jahan `tunnel.bat` / `tunnel.sh` hai).

### Chalana

- **Windows:** `tunnel.bat` par double-click karo.
- **Mac/Linux:** terminal mein `bash tunnel.sh` chalao.

Kuch second mein ek **password** screen par nazar aayega (us ko note kar lo) aur us ke neeche ek link aayegi jo `trycloudflare.com` par khatam hogi — **yehi tumhari public link hai**. Usay phone ke browser mein kholo, password likho, bas!

**Yaad rakho:**
- Jab tak ye window khuli hai, link kaam karegi. Band karne ke liye window close kar do (ya Ctrl+C).
- Har dafa naya password aur nayi link banti hai — purani link dobara kaam nahi karegi.
- Computer on aur internet se connected rehna chahiye jab use karna ho.

### 24/7 online chahiye (computer band ho tab bhi)?

Us ke liye VPS lena parega (jaise Contabo/Hetzner, taqreeban $5/month). Us par `requirements.txt` se install karke `DOWNLOADER_PASSWORD` set karke app chalao. Ek baat zehan mein rakho: VPS ke IP par YouTube aksar bot-check lagata hai, to YouTube ke liye cookies lagana par sakti hain.
