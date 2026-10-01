import json
import subprocess
from http.server import HTTPServer, BaseHTTPRequestHandler

PORT = 8766  # Dedicated physical alert listener port

class AlertHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == "/alert":
            try:
                data = json.loads(self.rfile.read(int(self.headers.get('Content-Length', 0))).decode('utf-8'))
                title = data.get("title", "Alert")
                message = data.get("message", "System event triggered.")
                
                print(f"[PHYSICAL ALERT] [{title}] {message}")
                
                # Trigger physical device feedback via Termux API
                subprocess.run(["termux-vibrate", "-d", "500"], capture_output=True)
                if "ERROR" in title.upper() or "WARNING" in title.upper():
                    subprocess.run(["termux-tts-speak", f"Attention Operator. {title}: {message}"], capture_output=True)
                
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b'{"status": "alert_dispatched"}')
            except Exception as e:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(f'{{"error": "{str(e)}"}}'.encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()
            
    def log_message(self, format, *args): pass

if __name__ == "__main__":
    print(f"[ALERT AGENT] Physical telemetry bridge active on port {PORT}")
    HTTPServer(('127.0.0.1', PORT), AlertHandler).serve_forever()
