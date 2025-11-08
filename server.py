import socket
import os

HOST = '127.0.0.1'
PORT = 5000

# Simple XOR encryption key
KEY = 42

def encrypt_decrypt(data: bytes) -> bytes:
    """XOR encrypt/decrypt"""
    return bytes([b ^ KEY for b in data])

# valid credentials
VALID_USER = "admin"
VALID_PASS = "1234"

server_socket = socket.socket()
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((HOST, PORT))
server_socket.listen(1)

print(f"✅ Server started at {HOST}:{PORT}")
conn, addr = server_socket.accept()
print(f"📡 Connected by {addr}")

# ---------------- AUTHENTICATION ----------------
conn.send("Username: ".encode())
username = conn.recv(1024).decode().strip()
conn.send("Password: ".encode())
password = conn.recv(1024).decode().strip()

if username != VALID_USER or password != VALID_PASS:
    conn.send("❌ Authentication failed.".encode())
    conn.close()
    server_socket.close()
    print("❌ Connection closed due to invalid login.")
    exit()
else:
    conn.send("✅ Authentication successful.\n".encode())
    print(f"🔐 {username} logged in successfully.")

# ---------------- MAIN LOOP ----------------
while True:
    command = conn.recv(1024).decode()
    if not command:
        break

    if command.lower() == "list":
        files = os.listdir(".")
        conn.send(("\n".join(files) if files else "(No files)").encode())

    elif command.lower().startswith("download "):
        filename = command.split(" ", 1)[1]
        if os.path.exists(filename):
            conn.send("FOUND".encode())
            with open(filename, "rb") as f:
                data = f.read()
                conn.sendall(encrypt_decrypt(data))
            print(f"📤 Sent encrypted file: {filename}")
        else:
            conn.send("NOTFOUND".encode())

    elif command.lower().startswith("upload "):
        raw_filename = command.split(" ", 1)[1]
        filename = os.path.basename(raw_filename)  # ✅ only keep the file name
        conn.send("READY".encode())

        with open(f"uploaded_{filename}", "wb") as f:
            data = conn.recv(10_000_000)
            f.write(encrypt_decrypt(data))
        conn.send(f"✅ File '{filename}' uploaded (decrypted) successfully.".encode())
        print(f"📥 Received & decrypted file: uploaded_{filename}")


    elif command.lower() == "exit":
        print("❌ Client disconnected.")
        break

    else:
        conn.send("Invalid command.".encode())

conn.close()
server_socket.close()
print("🔒 Server closed.")
