import socket

HOST = "127.0.0.1"
PORT = 8080

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(5)
server_socket.settimeout(1.0)  

print(f"Server running on http://{HOST}:{PORT}")
print("Press Ctrl+C to stop.\n")

def handle_request(client_socket):
    try:
        request_data = client_socket.recv(1024).decode("utf-8")
        if not request_data:
            return

        request_line = request_data.splitlines()[0]
        method, path, version = request_line.split(" ")

        if path == "/":
            body = "<html><body><h1>Hello from Python!</h1></body></html>"
            status_line = "HTTP/1.1 200 OK"
        else:
            body = "<html><body><h1>404 Not Found</h1></body></html>"
            status_line = "HTTP/1.1 404 Not Found"

        headers = [
            status_line,
            f"Content-Length: {len(body)}",
            "Content-Type: text/html; charset=utf-8",
            "Connection: close",
            "",
            ""
        ]
        response = "\r\n".join(headers) + body
        client_socket.sendall(response.encode("utf-8"))

    finally:
        client_socket.close()

try:
    while True:
        try:
            client_conn, client_addr = server_socket.accept()
            print(f"Connection from {client_addr}")
            handle_request(client_conn)
        except socket.timeout:
            continue  
except KeyboardInterrupt:
    print("\nStopping server...")
finally:
    server_socket.close()
    print("Server closed successfully.")