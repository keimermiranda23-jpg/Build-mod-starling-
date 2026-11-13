import os
import http.server
import json
import requests

PORT = int(os.environ.get("PORT", 10000))
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
GITHUB_REPOSITORY = os.environ.get("GITHUB_REPOSITORY")

class SimpleHandler(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.read_json(content_length)
            
            url = f"https://api.github.com/repos/{GITHUB_REPOSITORY}/dispatches"
            headers = {
                "Authorization": f"Bearer {GITHUB_TOKEN}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28"
            }
            data = {"event_type": "build-mod", "client_payload": body}
            
            print(f"Enviando solicitud a GitHub para el repositorio: {GITHUB_REPOSITORY}")
            response = requests.post(url, headers=headers, json=data)
            print(f"Respuesta de GitHub - Código: {response.status_code}, Cuerpo: {response.text}")
            
            self.send_response(200 if response.status_code == 204 else 500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            
            if response.status_code == 204:
                response_data = {"status": "success", "message": "Build triggered successfully"}
            else:
                response_data = {"status": "error", "message": f"GitHub rejected: {response.text}"}
                
            self.wfile.write(json.dumps(response_data).encode('utf-8'))
        except Exception as e:
            print(f"Error interno en el servidor: {str(e)}")
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "error", "message": str(e)}).encode('utf-8'))

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({"status": "active", "message": "Starling Build Gateway is active!"}).encode('utf-8'))

    def read_json(self, length):
        if length == 0:
            return {}
        try:
            raw_data = self.rfile.read(length).decode('utf-8')
            return json.loads(raw_data) if raw_data else {}
        except Exception as e:
            print(f"Error leyendo JSON de Starling: {e}")
            return {}

if __name__ == "__main__":
    server = http.server.HTTPServer(("0.0.0.0", PORT), SimpleHandler)
    print(f"Iniciando servidor en puerto {PORT}...")
    server.serve_forever()
    
