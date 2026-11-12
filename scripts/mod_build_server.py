import os
import http.server
import json
import requests

PORT = int(os.environ.get("PORT", 10000))
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
GITHUB_REPOSITORY = os.environ.get("GITHUB_REPOSITORY")

class SimpleHandler(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.read_json(content_length)
        
        url = f"https://api.github.com/repos/{GITHUB_REPOSITORY}/dispatches"
        headers = {
            "Authorization": f"Bearer {GITHUB_TOKEN}",
            "Accept": "application/vnd.github+json"
        }
        data = {"event_type": "build-mod", "client_payload": body}
        
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 204:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Build triggered successfully")
        else:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(f"Failed to trigger GitHub: {response.text}".encode())

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Starling Build Gateway is active!")

    def read_json(self, length):
        if length == 0:
            return {}
        try:
            return json.loads(self.rfile.read(length).decode('utf-8'))
        except:
            return {}

if __name__ == "__main__":
    server = http.server.HTTPServer(("0.0.0.0", PORT), SimpleHandler)
    print(f"Starting server on port {PORT}...")
    server.serve_forever()
