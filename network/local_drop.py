import http.server
import json
import os
import socket
import urllib.parse
from pathlib import Path
from typing import Optional

try:
    from PySide6.QtCore import QThread, Signal
except ImportError:
    class SignalInstance:
        def __init__(self):
            self._callbacks = []
        def emit(self, *args, **kwargs):
            for cb in list(self._callbacks):
                cb(*args, **kwargs)
        def connect(self, fn):
            self._callbacks.append(fn)

    class Signal:
        def __init__(self, *args):
            pass
        def __get__(self, instance, owner):
            if instance is None:
                return self
            if not hasattr(instance, '_signal_instances'):
                instance._signal_instances = {}
            if id(self) not in instance._signal_instances:
                instance._signal_instances[id(self)] = SignalInstance()
            return instance._signal_instances[id(self)]

    class QThread:
        def __init__(self): pass
        def start(self): self.run()

MOBILE_HTML_PAGE = """<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
  <title>Photo & Video Organizer Drop</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; }
    body { background-color: #0E121E; color: #E2E8F0; min-height: 100vh; padding: 20px; display: flex; flex-direction: column; align-items: center; }
    .card { background: #1B2135; border: 1px solid #2B3454; border-radius: 24px; padding: 24px 20px; width: 100%; max-width: 480px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); text-align: center; }
    .badge { display: inline-block; background: #000; color: #60A5FA; border: 1px solid #2B3454; font-size: 11px; font-weight: 700; letter-spacing: 1px; padding: 4px 14px; border-radius: 20px; margin-bottom: 14px; }
    h1 { font-size: 22px; font-weight: 800; color: #FFFFFF; margin-bottom: 6px; }
    p.subtitle { font-size: 13px; color: #94A3B8; margin-bottom: 24px; line-height: 1.4; }
    .dropzone { border: 2px dashed #3B82F6; background: rgba(59, 130, 246, 0.08); border-radius: 20px; padding: 32px 16px; cursor: pointer; transition: all 0.2s; margin-bottom: 20px; }
    .dropzone:active { transform: scale(0.98); background: rgba(59, 130, 246, 0.15); }
    .dropzone-icon { font-size: 44px; margin-bottom: 10px; }
    .dropzone-title { font-size: 16px; font-weight: 700; color: #FFFFFF; margin-bottom: 4px; }
    .dropzone-hint { font-size: 12px; color: #94A3B8; }
    input[type="file"] { display: none; }
    .btn-submit { display: none; width: 100%; padding: 16px; border: none; border-radius: 16px; background: linear-gradient(135deg, #3B82F6 0%, #1D4ED8 100%); color: #FFF; font-size: 16px; font-weight: 700; cursor: pointer; box-shadow: 0 8px 20px rgba(37, 99, 235, 0.4); margin-bottom: 20px; }
    .btn-submit:active { transform: scale(0.98); }
    .progress-box { display: none; margin-bottom: 20px; text-align: left; }
    .progress-bar-bg { width: 100%; height: 8px; background: #2B3454; border-radius: 4px; overflow: hidden; margin-top: 8px; }
    .progress-bar-fill { width: 0%; height: 100%; background: linear-gradient(90deg, #3B82F6, #10B981); border-radius: 4px; transition: width 0.15s; }
    .progress-text { display: flex; justify-content: space-between; font-size: 12px; color: #94A3B8; font-weight: 600; }
    .file-list { width: 100%; max-height: 240px; overflow-y: auto; text-align: left; margin-top: 10px; }
    .file-item { display: flex; align-items: center; justify-content: space-between; padding: 10px 14px; background: #131726; border-radius: 12px; margin-bottom: 8px; font-size: 13px; }
    .file-name { color: #E2E8F0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; max-width: 75%; }
    .file-status { font-weight: 700; font-size: 12px; }
    .file-status.success { color: #10B981; }
    .file-status.uploading { color: #60A5FA; }
    .footer { margin-top: 20px; font-size: 11px; color: #64748B; text-align: center; }
  </style>
</head>
<body>
  <div class="card">
    <div class="badge">WI-FI DIRECT DROP</div>
    <h1>Перенос на компьютер</h1>
    <p class="subtitle">Выберите фото и видео на телефоне для прямой беспроводной передачи на ПК</p>

    <div class="dropzone" id="dropzone">
      <div class="dropzone-icon">📷</div>
      <div class="dropzone-title">Выбрать фото и видео</div>
      <div class="dropzone-hint">Нажмите сюда для выбора из медиатеки</div>
    </div>
    <input type="file" id="filePicker" multiple accept="image/*,video/*">

    <div class="progress-box" id="progressBox">
      <div class="progress-text">
        <span id="progressLabel">Отправка...</span>
        <span id="progressPercent">0%</span>
      </div>
      <div class="progress-bar-bg">
        <div class="progress-bar-fill" id="progressBar"></div>
      </div>
    </div>

    <button class="btn-submit" id="btnSubmit">Отправить выбранные файлы</button>

    <div class="file-list" id="fileList"></div>
  </div>

  <div class="footer">100% Локально • 0 байт в облако • Домашний Wi-Fi</div>

  <script>
    const dropzone = document.getElementById('dropzone');
    const filePicker = document.getElementById('filePicker');
    const btnSubmit = document.getElementById('btnSubmit');
    const progressBox = document.getElementById('progressBox');
    const progressBar = document.getElementById('progressBar');
    const progressLabel = document.getElementById('progressLabel');
    const progressPercent = document.getElementById('progressPercent');
    const fileList = document.getElementById('fileList');

    let selectedFiles = [];

    dropzone.addEventListener('click', () => filePicker.click());

    filePicker.addEventListener('change', (e) => {
      selectedFiles = Array.from(e.target.files);
      if (selectedFiles.length > 0) {
        btnSubmit.style.display = 'block';
        btnSubmit.textContent = `Отправить (${selectedFiles.length} шт.)`;
        renderFileList(selectedFiles);
      }
    });

    function renderFileList(files) {
      fileList.innerHTML = '';
      files.forEach((f, idx) => {
        const item = document.createElement('div');
        item.className = 'file-item';
        item.id = 'file-' + idx;
        item.innerHTML = `
          <div class="file-name">${f.name}</div>
          <div class="file-status" id="status-${idx}">Готов</div>
        `;
        fileList.appendChild(item);
      });
    }

    btnSubmit.addEventListener('click', async () => {
      if (selectedFiles.length === 0) return;
      btnSubmit.disabled = true;
      btnSubmit.style.opacity = '0.5';
      progressBox.style.display = 'block';

      let total = selectedFiles.length;
      let completed = 0;

      for (let i = 0; i < total; i++) {
        const file = selectedFiles[i];
        const statusEl = document.getElementById('status-' + i);
        statusEl.className = 'file-status uploading';
        statusEl.textContent = 'Передача...';

        try {
          await uploadFile(file);
          statusEl.className = 'file-status success';
          statusEl.textContent = '✅ Загружен';
        } catch (err) {
          statusEl.className = 'file-status';
          statusEl.style.color = '#EF4444';
          statusEl.textContent = '❌ Ошибка';
        }

        completed++;
        let pct = Math.round((completed / total) * 100);
        progressBar.style.width = pct + '%';
        progressPercent.textContent = pct + '%';
        progressLabel.textContent = `Отправлено ${completed} из ${total}`;
      }

      btnSubmit.style.display = 'none';
      progressLabel.textContent = '🎉 Все файлы успешно отправлены!';
    });

    function uploadFile(file) {
      return new Promise((resolve, reject) => {
        const xhr = new XMLHttpRequest();
        xhr.open('POST', '/upload?filename=' + encodeURIComponent(file.name), true);
        xhr.onload = () => {
          if (xhr.status >= 200 && xhr.status < 300) {
            resolve();
          } else {
            reject(new Error('Status ' + xhr.status));
          }
        };
        xhr.onerror = () => reject(new Error('Network error'));
        xhr.send(file);
      });
    }
  </script>
</body>
</html>
"""

def get_local_ip() -> str:
    """Discovers the computer's primary LAN IP address."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Connecting to public IP without sending packets resolves active LAN interface
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        try:
            ip = socket.gethostbyname(socket.gethostname())
        except Exception:
            ip = "127.0.0.1"
    finally:
        s.close()
    return ip

class LocalDropRequestHandler(http.server.BaseHTTPRequestHandler):
    target_dir: Path = None
    server_thread: Optional["LocalDropServer"] = None

    def log_message(self, format, *args):
        # Suppress noisy standard console logging
        pass

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path in ("/", "/index.html"):
            content = MOBILE_HTML_PAGE.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
        elif parsed.path == "/ping":
            resp = json.dumps({"status": "active"}).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(resp)))
            self.end_headers()
            self.wfile.write(resp)
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/upload":
            params = urllib.parse.parse_qs(parsed.query)
            filename = params.get("filename", ["uploaded_media.jpg"])[0]
            # Clean filename
            filename = os.path.basename(filename)

            content_len = int(self.headers.get("Content-Length", 0))
            if not self.target_dir:
                self.target_dir = Path.home() / "Downloads" / "PhoneDrop"

            self.target_dir.mkdir(parents=True, exist_ok=True)
            dest = self.target_dir / filename

            # Auto-rename if file exists
            base, ext = os.path.splitext(filename)
            counter = 1
            while dest.exists():
                dest = self.target_dir / f"{base}_{counter}{ext}"
                counter += 1

            # Stream chunks directly to disk
            remaining = content_len
            try:
                with open(dest, "wb") as f:
                    while remaining > 0:
                        chunk_size = min(remaining, 65536)
                        chunk = self.rfile.read(chunk_size)
                        if not chunk:
                            break
                        f.write(chunk)
                        remaining -= len(chunk)

                if self.server_thread:
                    self.server_thread.file_received.emit(dest.name, content_len)

                resp = json.dumps({"success": True, "filename": dest.name, "bytes": content_len}).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(resp)))
                self.end_headers()
                self.wfile.write(resp)
            except Exception as e:
                self.send_response(500)
                self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()

class LocalDropServer(QThread):
    server_started = Signal(str, int)  # ip, port
    file_received = Signal(str, int)   # filename, bytes
    server_stopped = Signal()
    server_error = Signal(str)

    def __init__(self, target_dir: Path, preferred_port: int = 8080):
        super().__init__()
        self.target_dir = Path(target_dir)
        self.preferred_port = preferred_port
        self.httpd: Optional[http.server.HTTPServer] = None
        self._is_running = False

    def run(self):
        LocalDropRequestHandler.target_dir = self.target_dir
        LocalDropRequestHandler.server_thread = self

        ip = get_local_ip()
        port = self.preferred_port

        # Try preferred port, fallback to auto-assigned port if busy
        bound = False
        for p in [port, 8081, 8082, 8888, 0]:
            try:
                self.httpd = http.server.HTTPServer(("0.0.0.0", p), LocalDropRequestHandler)
                port = self.httpd.server_address[1]
                bound = True
                break
            except OSError:
                continue

        if not bound or not self.httpd:
            self.server_error.emit("Could not bind local network port for Wi-Fi Drop.")
            return

        self._is_running = True
        self.server_started.emit(ip, port)

        try:
            self.httpd.serve_forever()
        except Exception:
            pass
        finally:
            self._is_running = False
            self.server_stopped.emit()

    def stop(self):
        if self.httpd:
            self.httpd.shutdown()
            self.httpd.server_close()
