
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
from urllib.parse import urlparse, parse_qs
import sqlite3, json, time, threading, re, os, ssl, base64, html

DB_FILE = "urls.db"
HOST = "127.0.0.1"
PORT = 8443
SSL_CERT = "cert.pem" 
SSL_KEY = "key.pem"

ADMIN_USER = "admin"
ADMIN_PASS = "secret"

RATE_LIMIT_WINDOW = 60  
RATE_LIMIT_MAX = 30     

BASE62 = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"


_db_lock = threading.Lock()
rate_lock = threading.Lock()
rate_table = {} 


def base62_encode(n: int) -> str:
    if n == 0:
        return BASE62[0]
    s = []
    while n:
        n, r = divmod(n, 62)
        s.append(BASE62[r])
    return ''.join(reversed(s))


def valid_alias(a: str):
    return re.fullmatch(r"[A-Za-z0-9_-]{1,64}", a)


def is_valid_url(u: str):
    from urllib.parse import urlparse
    p = urlparse(u)
    return p.scheme in ("http", "https") and bool(p.netloc)


def init_db():
    need = not os.path.exists(DB_FILE)
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    if need:
        with conn:
            conn.executescript("""
            CREATE TABLE urls(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT UNIQUE,
                url TEXT,
                created_at INTEGER,
                clicks INTEGER DEFAULT 0
            );
            """)
    return conn


DB = init_db()


def insert_url(u, custom=None):
    with _db_lock:
        c = DB.cursor()
        if custom:
            c.execute("INSERT INTO urls(code, url, created_at) VALUES(?,?,?)", (custom, u, int(time.time())))
            DB.commit()
            return custom
        c.execute("INSERT INTO urls(url, created_at) VALUES(?,?)", (u, int(time.time())))
        rowid = c.lastrowid
        code = base62_encode(rowid)
        c.execute("UPDATE urls SET code=? WHERE id=?", (code, rowid))
        DB.commit()
        return code


def get_url(code):
    with _db_lock:
        cur = DB.execute("SELECT * FROM urls WHERE code=?", (code,))
        return cur.fetchone()


def increment_click(code):
    with _db_lock:
        DB.execute("UPDATE urls SET clicks=clicks+1 WHERE code=?", (code,))
        DB.commit()


def delete_url(code):
    with _db_lock:
        cur = DB.execute("DELETE FROM urls WHERE code=?", (code,))
        DB.commit()
        return cur.rowcount > 0


def check_auth(header):
    if not header or not header.startswith("Basic "):
        return False
    try:
        decoded = base64.b64decode(header.split(" ")[1]).decode()
        user, pw = decoded.split(":", 1)
        return (user == ADMIN_USER and pw == ADMIN_PASS)
    except Exception:
        return False


def enforce_rate_limit(ip):
    now = time.time()
    with rate_lock:
        timestamps = rate_table.get(ip, [])
        timestamps = [t for t in timestamps if now - t < RATE_LIMIT_WINDOW]
        if len(timestamps) >= RATE_LIMIT_MAX:
            return False
        timestamps.append(now)
        rate_table[ip] = timestamps
        return True


class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True


class Handler(BaseHTTPRequestHandler):

    def _json(self, obj, status=200):
        data = json.dumps(obj).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _html(self, html_text, status=200):
        data = html_text.encode()
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def rate_check(self):
        ip = self.client_address[0]
        if not enforce_rate_limit(ip):
            self._json({"error": "rate limit exceeded"}, 429)
            return False
        return True

    def do_GET(self):
        if not self.rate_check():
            return
        path = urlparse(self.path).path
        if path == "/":
            return self.page_form()
        if path.startswith("/api/stats/"):
            return self.api_stats(path[len("/api/stats/"):])
        if path.startswith("/api/delete/"):
            return self.api_delete(path[len("/api/delete/"):])
        code = path.lstrip("/")
        row = get_url(code)
        if not row:
            return self._html("<h1>404 Not Found</h1>", 404)
        increment_click(code)
        self.send_response(302)
        self.send_header("Location", row["url"])
        self.end_headers()

    def do_POST(self):
        if not self.rate_check():
            return
        path = urlparse(self.path).path
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode()
        if path == "/api/shorten":
            try:
                data = json.loads(body)
            except Exception:
                return self._json({"error": "invalid JSON"}, 400)
            url = data.get("url")
            custom = data.get("custom")
            if not url or not is_valid_url(url):
                return self._json({"error": "invalid URL"}, 400)
            if custom and not valid_alias(custom):
                return self._json({"error": "invalid custom alias"}, 400)
            try:
                code = insert_url(url, custom)
            except sqlite3.IntegrityError:
                return self._json({"error": "alias already exists"}, 409)
            short = f"https://{self.headers.get('Host')}/{code}"
            return self._json({"success": True, "short_url": short})
        elif path == "/create": 
            qs = parse_qs(body)
            url = qs.get("url", [""])[0]
            custom = qs.get("custom", [""])[0] or None
            if not is_valid_url(url):
                return self._html("<h2>Invalid URL</h2>", 400)
            try:
                code = insert_url(url, custom)
                short = f"https://{self.headers.get('Host')}/{code}"
                return self._html(f"<h3>Short URL: <a href='{short}'>{short}</a></h3>")
            except sqlite3.IntegrityError:
                return self._html("<h2>Alias already exists</h2>", 409)
        else:
            return self._html("404", 404)

    def page_form(self):
        html_text = f"""
        <html><head><title>URL Shortener</title></head>
        <body>
        <h2>Create Short URL</h2>
        <form method='POST' action='/create'>
          <label>URL: <input type='text' name='url' size='50' required></label><br><br>
          <label>Custom Alias (optional): <input type='text' name='custom'></label><br><br>
          <input type='submit' value='Shorten'>
        </form>
        <hr>
        <p>Admin endpoints (require Basic Auth): /api/delete/&lt;code&gt;, /api/stats/&lt;code&gt;</p>
        </body></html>
        """
        return self._html(html_text)

    def api_stats(self, code):
        if not check_auth(self.headers.get("Authorization")):
            self.send_response(401)
            self.send_header("WWW-Authenticate", 'Basic realm="Admin"')
            self.end_headers()
            return
        row = get_url(code)
        if not row:
            return self._json({"error": "not found"}, 404)
        return self._json({
            "code": row["code"],
            "url": row["url"],
            "created_at": row["created_at"],
            "clicks": row["clicks"]
        })

    def api_delete(self, code):
        if not check_auth(self.headers.get("Authorization")):
            self.send_response(401)
            self.send_header("WWW-Authenticate", 'Basic realm="Admin"')
            self.end_headers()
            return
        ok = delete_url(code)
        if not ok:
            return self._json({"error": "not found"}, 404)
        return self._json({"success": True})

    def log_message(self, fmt, *args):
        print("[%s] %s %s" % (self.client_address[0], self.command, self.path))


def run():
    httpd = ThreadingHTTPServer((HOST, PORT), Handler)

    if os.path.exists(SSL_CERT) and os.path.exists(SSL_KEY):
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ctx.load_cert_chain(certfile=SSL_CERT, keyfile=SSL_KEY)
        httpd.socket = ctx.wrap_socket(httpd.socket, server_side=True)
        print(f"HTTPS enabled with {SSL_CERT}, listening at https://{HOST}:{PORT}/")
    else:
        print(f"SSL files not found, running HTTP only at http://{HOST}:{PORT}/")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        httpd.server_close()


if __name__ == "__main__":
    run()