from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
import json
import logging
from backend import start_process, stop_process, status_process, list_processes

HOST, PORT = "localhost", 8080

class ProcessHandler(BaseHTTPRequestHandler):
    def _set_headers(self, code=200):
        self.send_response(code)
        self.send_header("Content-type", "application/json")
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        query = parse_qs(parsed.query)
        path = parsed.path
        response = {}

        if path == "/start":
            cmd = query.get("cmd", [None])[0]
            if not cmd:
                response = {"error": "Missing ?cmd= parameter"}
                self._set_headers(400)
            else:
                response = start_process(cmd)
                self._set_headers(200)

        elif path == "/stop":
            pid = query.get("pid", [None])[0]
            if not pid:
                response = {"error": "Missing ?pid= parameter"}
                self._set_headers(400)
            else:
                response = stop_process(int(pid))
                self._set_headers(200)

        elif path == "/status":
            pid = query.get("pid", [None])[0]
            if not pid:
                response = {"error": "Missing ?pid= parameter"}
                self._set_headers(400)
            else:
                response = status_process(int(pid))
                self._set_headers(200)

        elif path == "/list":
            response = list_processes()
            self._set_headers(200)

        else:
            self._set_headers(404)
            response = {"error": "Unknown endpoint"}

        self.wfile.write(json.dumps(response, indent=4).encode())

def run_server():
    logging.basicConfig(level=logging.INFO)
    server = HTTPServer((HOST, PORT), ProcessHandler)
    logging.info(f"Process Manager API running at http://{HOST}:{PORT}")
    print(f"Process Manager API running at http://{HOST}:{PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        logging.info("Server stopped manually")
        server.server_close()

if __name__ == "__main__":
    run_server()
