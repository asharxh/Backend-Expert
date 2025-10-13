import socket

HOST = "127.0.0.1"
PORT = 8080

def http_get(path="/"):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, PORT))

    request = (
        f"GET {path} HTTP/1.1\r\n"
        f"Host: {HOST}\r\n"
        "Connection: close\r\n"
        "\r\n"
    )

    client_socket.sendall(request.encode("utf-8"))

    response_data = b""
    while True:
        chunk = client_socket.recv(1024)
        if not chunk:
            break
        response_data += chunk

    client_socket.close()
    response_text = response_data.decode("utf-8", errors="replace")

    parts = response_text.split("\r\n\r\n", 1)
    headers = parts[0]
    body = parts[1] if len(parts) > 1 else ""
    return headers, body


if __name__ == "__main__":
    path = input("Enter path (e.g. / or /about): ").strip() or "/"
    headers, body = http_get(path)

    print("\n----- HEADERS -----")
    print(headers)
    print("-------------------")

    print("\n----- BODY -----")
    print(body)
    print("-------------------")

    save = input("Save body to file? (y/n): ").lower()
    if save == "y":
        with open("response.html", "w", encoding="utf-8") as f:
            f.write(body)
        print(" Saved as response.html — open it in a browser!")