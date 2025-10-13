import socket
import json
import time

HOST = "127.0.0.1"
PORT = 5050

RATE_LIMIT = 1         
TIME_WINDOW = 10

client_requests = {}

def build_response(status_code, data=None, message=None):
    status_messages = {
        200: "OK",
        400: "Bad Request",
        404: "Not Found",
        405: "Method Not Allowed",
        429: "Too Many Requests",
        500: "Internal Server Error"
    }

    status_line = f"HTTP/1.1 {status_code} {status_messages.get(status_code, '')}"

    if data is not None:
        body = json.dumps(data)
    else:
        body = json.dumps({"error": message or status_messages.get(status_code, "")})

    headers = [
        status_line,
        "Content-Type: application/json",
        f"Content-Length: {len(body)}",
        "Connection: close",
        "",
        ""
    ]
    return "\r\n".join(headers) + body


def is_rate_limited(client_ip):
    now = time.time()
    request_times = client_requests.get(client_ip, [])

    request_times = [t for t in request_times if now - t < TIME_WINDOW]

    if len(request_times) >= RATE_LIMIT:
        client_requests[client_ip] = request_times 
        return True

    request_times.append(now)
    client_requests[client_ip] = request_times
    return False


def handle_request(client_socket, client_ip):
    try:
        request = client_socket.recv(1024).decode("utf-8")
        if not request:
            return

        request_line = request.splitlines()[0]
        parts = request_line.split(" ")

        if len(parts) < 3:
            response = build_response(400)
        else:
            method, path, _ = parts
            print(f"→ {method} {path} from {client_ip}")

            if method != "GET":
                response = build_response(405)
            else:
                if is_rate_limited(client_ip):
                    response = build_response(429, {"error": "Rate limit exceeded. Try again later."})
                else:
                    data = {
                        "message": "Request successful!",
                        "time": time.strftime("%H:%M:%S"),
                        "client_ip": client_ip
                    }
                    response = build_response(200, data)

        client_socket.sendall(response.encode("utf-8"))

    except Exception as e:
        print(f"Error: {e}")
        response = build_response(500, message=str(e))
        client_socket.sendall(response.encode("utf-8"))
    finally:
        client_socket.close()


def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)
    server_socket.settimeout(1.0)

    print(f"🚦 Rate-Limited API Server running on http://{HOST}:{PORT}")
    print(f"→ Limit: {RATE_LIMIT} requests per {TIME_WINDOW} seconds")
    print("Press Ctrl+C to stop.\n")

    try:
        while True:
            try:
                client_conn, client_addr = server_socket.accept()
                client_ip = client_addr[0]
                handle_request(client_conn, client_ip)
            except socket.timeout:
                continue
    except KeyboardInterrupt:
        print("\nServer shutting down...")
    finally:
        server_socket.close()
        print("Server closed.")


if __name__ == "__main__":
    start_server()