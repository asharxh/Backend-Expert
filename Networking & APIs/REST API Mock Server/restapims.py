import socket
import json

HOST = "127.0.0.1"
PORT = 5000

mock_data = {
    "/users": [
        {"id": 1, "name": "Alice"},
        {"id": 2, "name": "Bob"},
        {"id": 3, "name": "Charlie"}
    ],
    "/posts": [
        {"id": 1, "title": "Hello World", "author": "Alice"},
        {"id": 2, "title": "REST API with Python", "author": "Bob"}
    ]
}

def build_response(status_code, data=None, message=None):
    status_messages = {
        200: "OK",
        400: "Bad Request",
        404: "Not Found",
        405: "Method Not Allowed",
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


def handle_request(client_socket):
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
            print(f"→ {method} {path}")

            if method == "GET":
                if path == "/":
                    response = build_response(200, {"message": "Welcome to the Mock REST API!"})
                elif path == "/favicon.ico":
                    response = build_response(200, {"favicon": None})
                elif path in mock_data:
                    response = build_response(200, mock_data[path])
                else:
                    response = build_response(404)
            else:
                response = build_response(405)

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

    print(f"Mock REST API Server running on http://{HOST}:{PORT}")
    print("Available endpoints:")
    for endpoint in mock_data.keys():
        print(f"  GET {endpoint}")
    print("Also available: GET / (welcome)\nPress Ctrl+C to stop.\n")

    try:
        while True:
            try:
                client_conn, client_addr = server_socket.accept()
                handle_request(client_conn)
            except socket.timeout:
                continue
    except KeyboardInterrupt:
        print("\nShutting down server...")
    finally:
        server_socket.close()
        print(" Server closed.")


if __name__ == "__main__":
    start_server()