import json
import os
import urllib.request
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path


class TTSProxyHandler(SimpleHTTPRequestHandler):
    def do_OPTIONS(self):
        self._set_cors()
        self.send_response(204)
        self.end_headers()

    def do_POST(self):
        if self.path == "/api/tts":
            content_len = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_len)
            data = json.loads(body)

            endpoint_id = os.environ.get("RUNPOD_ENDPOINT_ID", "")
            api_key = os.environ.get("RUNPOD_API_KEY", "")

            if not endpoint_id or not api_key:
                self._send_json(
                    {"error": "RUNPOD_ENDPOINT_ID and RUNPOD_API_KEY must be set"},
                    status=400,
                )
                return

            url = f"https://api.runpod.ai/v2/{endpoint_id}/runsync"
            req = urllib.request.Request(
                url,
                data=json.dumps({"input": data}).encode(),
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {api_key}",
                },
                method="POST",
            )

            try:
                with urllib.request.urlopen(req, timeout=120) as resp:
                    result = json.loads(resp.read())
                self._send_json(result)
            except urllib.error.HTTPError as e:
                self._send_json(
                    {"error": f"RunPod API error: {e.code} {e.read().decode()}"},
                    status=e.code,
                )
            except urllib.error.URLError as e:
                self._send_json({"error": str(e.reason)}, status=502)
        else:
            super().do_POST()

    def _send_json(self, data, status=200):
        self.send_response(status)
        self._set_cors()
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def _set_cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header(
            "Access-Control-Allow-Methods", "GET, POST, OPTIONS"
        )
        self.send_header(
            "Access-Control-Allow-Headers", "Content-Type, Authorization"
        )


def main():
    port = int(os.environ.get("PORT", 8080))
    serve_dir = Path(__file__).parent.resolve()
    os.chdir(serve_dir)

    server = HTTPServer(("0.0.0.0", port), TTSProxyHandler)
    print(f"Serving TTS playground at http://localhost:{port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
