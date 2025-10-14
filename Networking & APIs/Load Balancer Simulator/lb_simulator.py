
import socket
import threading
import time
import select
import sys
from urllib.parse import urlparse
from http.server import BaseHTTPRequestHandler, HTTPServer
from io import BytesIO


class SimpleBackendHandler(BaseHTTPRequestHandler):
    server_id = "backend-unknown"

    def do_GET(self):
        if self.path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.send_header("Content-Length", "2")
            self.end_headers()
            self.wfile.write(b"OK")
            return

        body = f"Hello from {self.server_id}! You requested {self.path}\n".encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("X-Backend-ID", self.server_id)
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        length = int(self.headers.get("Content-Length", "0"))
        data = self.rfile.read(length) if length > 0 else b""
        body = f"POST to {self.server_id}: got {len(data)} bytes\n".encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        pass

def start_test_backend(bind_host, bind_port, server_id):
    class Handler(SimpleBackendHandler):
        pass
    Handler.server_id = server_id
    httpd = HTTPServer((bind_host, bind_port), Handler)
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()
    print(f"[backend {server_id}] started at {bind_host}:{bind_port}")
    return httpd


class Backend:
    def __init__(self, host, port, name=None):
        self.host = host
        self.port = port
        self.name = name or f"{host}:{port}"
        self.lock = threading.Lock()
        self.active_connections = 0
        self.healthy = True
        self.last_checked = 0.0

    def __repr__(self):
        return f"<Backend {self.name} healthy={self.healthy} active={self.active_connections}>"

class HealthChecker(threading.Thread):
    def __init__(self, backends, interval=5.0, timeout=2.0, use_http_health=True):
        super().__init__(daemon=True)
        self.backends = backends
        self.interval = interval
        self.timeout = timeout
        self.use_http_health = use_http_health
        self._stop = threading.Event()

    def run(self):
        while not self._stop.is_set():
            for b in self.backends:
                self.check_backend(b)
            time.sleep(self.interval)

    def stop(self):
        self._stop.set()

    def check_backend(self, backend: Backend):
        addr = (backend.host, backend.port)
        success = False
        try:
            if self.use_http_health:
                s = socket.create_connection(addr, timeout=self.timeout)
                s.settimeout(self.timeout)
                req = b"GET /health HTTP/1.1\r\nHost: %b:%d\r\nConnection: close\r\n\r\n" % (backend.host.encode(), backend.port)
                s.sendall(req)
                resp = b""
                try:
                    resp = s.recv(1024)
                except Exception:
                    resp = b""
                s.close()
                if b"200" in resp and b"OK" in resp:
                    success = True
            else:
                s = socket.create_connection(addr, timeout=self.timeout)
                s.close()
                success = True
        except Exception:
            success = False
        backend.healthy = success
        backend.last_checked = time.time()
        status = "UP" if success else "DOWN"
        print(f"[health] {backend.name} -> {status}")

class LoadBalancer:
    def __init__(self, listen_host, listen_port, backends,
                 algo="roundrobin", sticky_by_ip=False,
                 conn_timeout=10.0, backend_timeout=10.0):
        """
        backends: list of Backend objects
        algo: 'roundrobin' or 'leastconn'
        sticky_by_ip: boolean
        """
        self.listen_host = listen_host
        self.listen_port = listen_port
        self.backends = backends[:]  
        self.algo = algo
        self.sticky_by_ip = sticky_by_ip
        self.conn_timeout = conn_timeout
        self.backend_timeout = backend_timeout

        self._rr_index = 0
        self._sticky_map = {} 
        self._lock = threading.Lock()
        self._stop = threading.Event()

    def start(self):
        t = threading.Thread(target=self.serve_forever, daemon=True)
        t.start()
        print(f"[lb] listening on {self.listen_host}:{self.listen_port} (algo={self.algo}, sticky_by_ip={self.sticky_by_ip})")

    def stop(self):
        self._stop.set()

    def serve_forever(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((self.listen_host, self.listen_port))
            s.listen(200)
            s.settimeout(1.0)
            while not self._stop.is_set():
                try:
                    client_sock, client_addr = s.accept()
                except socket.timeout:
                    continue
                t = threading.Thread(target=self.handle_client, args=(client_sock, client_addr), daemon=True)
                t.start()

    def choose_backend(self, client_ip):
        healthy = [b for b in self.backends if b.healthy]
        if not healthy:
            healthy = self.backends[:]


        if self.sticky_by_ip:
            mapped = self._sticky_map.get(client_ip)
            if mapped:
                for b in healthy:
                    if b.name == mapped:
                        return b

        if self.algo == "roundrobin":
            with self._lock:
                idx = self._rr_index % len(healthy)
                sel = healthy[idx]
                self._rr_index += 1
        elif self.algo == "leastconn":
            sel = min(healthy, key=lambda b: b.active_connections)
        else:
            sel = healthy[0]

        if self.sticky_by_ip:
            self._sticky_map[client_ip] = sel.name
        return sel

    def handle_client(self, client_sock: socket.socket, client_addr):
        client_ip, client_port = client_addr[0], client_addr[1]
        client_sock.settimeout(self.conn_timeout)
        try:

            request = self._recv_http_request(client_sock)
            if not request:
                client_sock.close()
                return
            backend = self.choose_backend(client_ip)
            if not backend:
                client_sock.sendall(b"HTTP/1.1 503 Service Unavailable\r\nContent-Length: 13\r\n\r\nService Unavailable")
                client_sock.close()
                return

            with backend.lock:
                backend.active_connections += 1

            try:
                response = self._forward_to_backend(backend, request)
                if response is None:

                    client_sock.sendall(b"HTTP/1.1 502 Bad Gateway\r\nContent-Length: 11\r\n\r\nBad Gateway")
                else:
     
                    client_sock.sendall(response)
            finally:
                with backend.lock:
                    backend.active_connections = max(0, backend.active_connections - 1)
        except Exception as e:
          
            try:
                client_sock.sendall(b"HTTP/1.1 500 Internal Server Error\r\nContent-Length: 21\r\n\r\nInternal Server Error")
            except Exception:
                pass
            print(f"[lb] error handling client {client_ip}:{client_port} -> {e}")
        finally:
            try:
                client_sock.close()
            except Exception:
                pass

    def _recv_http_request(self, sock: socket.socket):
        sock.settimeout(self.conn_timeout)
        data = b""
        headers = b""
  
        while True:
            try:
                chunk = sock.recv(4096)
            except socket.timeout:
                break
            except Exception:
                return None
            if not chunk:
                break
            data += chunk
            if b"\r\n\r\n" in data:
                headers, rest = data.split(b"\r\n\r\n", 1)
                headers += b"\r\n\r\n"
                break
         
            if len(data) > 65536:
                
                return None
        if not headers:
            return None

        header_text = headers.decode("iso-8859-1")
        cl = 0
        for line in header_text.split("\r\n"):
            if line.lower().startswith("content-length:"):
                try:
                    cl = int(line.split(":",1)[1].strip())
                except Exception:
                    cl = 0
                break
        body = rest if 'rest' in locals() else b''
        to_read = cl - len(body)
        while to_read > 0:
            try:
                chunk = sock.recv(4096)
            except socket.timeout:
                break
            except Exception:
                return None
            if not chunk:
                break
            body += chunk
            to_read = cl - len(body)
        return headers + body

    def _forward_to_backend(self, backend: Backend, request_bytes: bytes):
        addr = (backend.host, backend.port)
        try:
            s = socket.create_connection(addr, timeout=self.backend_timeout)
            s.settimeout(self.backend_timeout)
          
            s.sendall(request_bytes)
            response = b""
            last_recv = time.time()
            while True:
                ready = select.select([s], [], [], 0.5)
                if ready[0]:
                    chunk = s.recv(8192)
                    if not chunk:
                        break
                    response += chunk
                    last_recv = time.time()
                else:
                    if time.time() - last_recv > 1.0:
                        break
            s.close()
            return response
        except Exception as e:
            print(f"[lb] forward error to {backend.name}: {e}")
            backend.healthy = False 
            return None

def create_backends(num=3, start_port=9001, host="127.0.0.1"):
    backends = []
    servers = []
    for i in range(num):
        port = start_port + i
        srv = start_test_backend(host, port, server_id=f"BE-{i+1}")
        servers.append(srv)
        backends.append(Backend(host=host, port=port, name=f"BE-{i+1}"))
    return backends, servers

def main():
    backends, backend_servers = create_backends(num=3, start_port=9001, host="127.0.0.1")
    hc = HealthChecker(backends, interval=5.0, timeout=2.0, use_http_health=True)
    hc.start()
    lb = LoadBalancer(listen_host="127.0.0.1", listen_port=8080,
                      backends=backends,
                      algo="roundrobin",  
                      sticky_by_ip=False,
                      conn_timeout=10.0,
                      backend_timeout=5.0)
    lb.start()

    print("\nSimulator running. Try: curl http://127.0.0.1:8080/\n")
    print("Commands:\n  q     quit\n  mode rr|least   switch algorithm\n  sticky on|off   toggle sticky-by-ip\n  status          print backend status\n")
    try:
        while True:
            cmd = input("> ").strip().lower()
            if not cmd:
                continue
            if cmd in ("q", "quit", "exit"):
                break
            if cmd.startswith("mode"):
                parts = cmd.split()
                if len(parts) >= 2:
                    if parts[1] in ("rr", "roundrobin"):
                        lb.algo = "roundrobin"
                    elif parts[1] in ("least", "leastconn"):
                        lb.algo = "leastconn"
                    print(f"[cli] algorithm set to {lb.algo}")
                continue
            if cmd.startswith("sticky"):
                parts = cmd.split()
                if len(parts) >= 2:
                    if parts[1] in ("on", "true", "1"):
                        lb.sticky_by_ip = True
                    else:
                        lb.sticky_by_ip = False
                    print(f"[cli] sticky_by_ip = {lb.sticky_by_ip}")
                continue
            if cmd == "status":
                for b in backends:
                    print(f"  {b.name}: healthy={b.healthy} active={b.active_connections} last_checked={time.ctime(b.last_checked)}")
                continue
            print("unknown command")
    except KeyboardInterrupt:
        pass
    finally:
        print("shutting down...")
        hc.stop()
        lb.stop()
        for s in backend_servers:
            s.shutdown()
        print("done.")

if __name__ == "__main__":
    main()