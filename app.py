from flask import Flask, request, send_file, render_template_string
import yt_dlp
import os

app = Flask(__name__)

# Your exact HTML
HTML = '''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>A Product Of • VIKKI</title>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.6.0/css/all.min.css">
  <style>
    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }

    body {
      background: #0b1a1e;
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      font-family: 'Segoe UI', Roboto, system-ui, -apple-system, sans-serif;
      padding: 1.5rem;
      background-image: radial-gradient(circle at 20% 30%, rgba(255, 215, 0, 0.08) 0%, transparent 50%),
                        radial-gradient(circle at 80% 70%, rgba(200, 30, 30, 0.10) 0%, transparent 50%);
    }

    .tvk-card {
      width: 100%;
      max-width: 720px;
      background: rgba(0, 0, 0, 0.65);
      backdrop-filter: blur(16px);
      border-radius: 48px 48px 48px 48px;
      padding: 2.5rem 2rem;
      box-shadow: 0 30px 80px rgba(0, 0, 0, 0.8), 0 0 0 2px #b8860b, 0 0 0 6px #8b0000, 0 0 0 10px #f5c542;
      border: 2px solid #f5c542;
      transition: all 0.2s ease;
      position: relative;
    }

    .tvk-card::before {
      content: '';
      position: absolute;
      top: -12px;
      left: 20%;
      right: 20%;
      height: 6px;
      background: linear-gradient(90deg, #8b0000 0%, #8b0000 33%, #f5c542 33%, #f5c542 66%, #8b0000 66%, #8b0000 100%);
      border-radius: 12px;
      filter: drop-shadow(0 0 6px #f5c542);
    }

    .tvk-card::after {
      content: '';
      position: absolute;
      bottom: -12px;
      left: 20%;
      right: 20%;
      height: 6px;
      background: linear-gradient(90deg, #f5c542 0%, #f5c542 33%, #8b0000 33%, #8b0000 66%, #f5c542 66%, #f5c542 100%);
      border-radius: 12px;
      filter: drop-shadow(0 0 6px #f5c542);
    }

    .tvk-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 2.5rem;
      border-bottom: 2px solid rgba(245, 197, 66, 0.3);
      padding-bottom: 1rem;
    }

    .tvk-title {
      display: flex;
      align-items: center;
      gap: 0.75rem;
    }

    .tvk-title h1 {
      font-size: 2.6rem;
      font-weight: 700;
      letter-spacing: 3px;
      background: linear-gradient(135deg, #f5c542 20%, #ffdd77 80%);
      -webkit-background-clip: text;
      background-clip: text;
      color: transparent;
      text-shadow: 0 0 18px rgba(245, 197, 66, 0.5);
    }

    .tvk-title i {
      color: #f5c542;
      font-size: 2.4rem;
      filter: drop-shadow(0 0 6px #f5c542);
    }

    .tvk-badge {
      background: #8b0000;
      padding: 0.4rem 1.2rem;
      border-radius: 40px;
      font-weight: 600;
      font-size: 0.9rem;
      letter-spacing: 1px;
      color: #f5c542;
      border: 1px solid #f5c542;
      box-shadow: inset 0 0 8px rgba(245, 197, 66, 0.3);
      text-transform: uppercase;
    }

    .tvk-input {
      width: 100%;
      background: rgba(255, 255, 255, 0.06);
      border: 2px solid #f5c542;
      border-radius: 60px;
      padding: 1rem 1.8rem;
      font-size: 1.1rem;
      color: #f5f0e0;
      outline: none;
      transition: all 0.2s;
      backdrop-filter: blur(4px);
      letter-spacing: 0.3px;
      margin-bottom: 1rem;
    }

    .tvk-btn {
      background: linear-gradient(145deg, #f5c542, #dba22e);
      border: none;
      border-radius: 60px;
      padding: 1.1rem 1.8rem;
      font-weight: 700;
      font-size: 1.4rem;
      color: #1a1e1b;
      width: 100%;
      cursor: pointer;
      transition: all 0.25s;
      box-shadow: 0 6px 0 #7a4f1a, 0 8px 24px rgba(245, 197, 66, 0.3);
      letter-spacing: 1.5px;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 12px;
      border: 1px solid #ffea9a;
    }

    .tvk-btn:hover {
      transform: translateY(-4px);
      box-shadow: 0 10px 0 #7a4f1a, 0 18px 40px rgba(245, 197, 66, 0.5);
      background: linear-gradient(145deg, #ffdd77, #e8b53a);
    }

    .format-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 1rem;
      margin-top: 1.5rem;
    }

    .format-btn {
      background: rgba(245, 197, 66, 0.12);
      border: 2px solid #f5c542;
      border-radius: 40px;
      padding: 0.9rem 0.5rem;
      color: #f5e7c8;
      font-weight: 600;
      transition: all 0.2s;
      cursor: pointer;
      display: flex;
      flex-direction: column;
      align-items: center;
      box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    }

    .format-btn:hover {
      background: #f5c542;
      color: #0b1a1e;
      transform: scale(1.02);
    }
  </style>
</head>
<body>
  <div class="tvk-card">

    <div class="tvk-header">
      <div class="tvk-title">
        <i class="fas fa-flag"></i>
        <h1>YT_Download</h1>
      </div>
      <div class="tvk-badge">
        <i class="fas fa-shield-alt"></i> VIKKI
      </div>
    </div>

    <div id="loginPanel">
      <input id="user" value="test" class="tvk-input" placeholder="Username">
      <input id="pass" type="password" value="test" class="tvk-input" placeholder="Password">
      <button onclick="handleLogin()" class="tvk-btn">உள் நுழை</button>
    </div>

    <div id="appPanel" class="hidden">
      <input id="url" class="tvk-input" placeholder="YouTube URL ஐ ஒட்டவும்">
      <button onclick="fetchVideoInfo()" class="tvk-btn">வீடியோ தகவல்</button>
      <div id="result" class="hidden"></div>
    </div>
  </div>

  <script>
    let currentUrl = '';

    async function handleLogin() {
      const res = await fetch('/login', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({username: document.getElementById('user').value, password: document.getElementById('pass').value})
      });
      if ((await res.json()).success) {
        document.getElementById('loginPanel').classList.add('hidden');
        document.getElementById('appPanel').classList.remove('hidden');
      }
    }

    async function fetchVideoInfo() {
      currentUrl = document.getElementById('url').value.trim();
      const res = await fetch(`/info?url=${encodeURIComponent(currentUrl)}`);
      const data = await res.json();
      if (data.error) return alert(data.error);

      let html = `<h3 style="margin:1rem 0;color:#f5c542;">${data.title}</h3>
                  <img src="${data.thumbnail}" style="width:100%;border-radius:20px;border:3px solid #f5c542;">`;
      html += `<div class="format-grid" id="formats"></div>`;
      document.getElementById('result').innerHTML = html;
      document.getElementById('result').classList.remove('hidden');

      const container = document.getElementById('formats');
      data.formats.filter(f => f.hasVideo).forEach(f => {
        const btn = document.createElement('div');
        btn.className = 'format-btn';
        btn.innerHTML = `<strong>${f.quality}</strong><br><small>${f.container} • ${f.size}</small>`;
        btn.onclick = () => download(f.itag, 'video');
        container.appendChild(btn);
      });
    }

    function download(itag, type) {
      let url = `/download?url=${encodeURIComponent(currentUrl)}&format=${type}`;
      if (itag) url += `&itag=${itag}`;
      window.location.href = url;
    }
  </script>
</body>
</html>'''

@app.route('/')
def home():
  return render_template_string(HTML)

@app.route('/login', methods=['POST'])
def login():
  return {'success': True}

@app.route('/info')
def info():
  url = request.args.get('url')
  ydl_opts = {'quiet': True}
  with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    info = ydl.extract_info(url, download=False)
  return {'title': info['title'], 'thumbnail': info.get('thumbnail', ''), 'formats': []}

@app.route('/download')
def download():
  url = request.args.get('url')
  type_ = request.args.get('type', 'video')
  ydl_opts = {
    'outtmpl': 'downloads/%(title)s.%(ext)s',
  }
  if type_ == 'audio':
    ydl_opts['format'] = 'bestaudio/best'
    ydl_opts['postprocessors'] = [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3'}]
  else:
    ydl_opts['format'] = 'bestvideo+bestaudio/best'

  with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    info = ydl.extract_info(url, download=True)
    filename = ydl.prepare_filename(info)
  return send_file(filename, as_attachment=True)

if __name__ == '__main__':
  os.makedirs('downloads', exist_ok=True)
  app.run(debug=True, port=5000)