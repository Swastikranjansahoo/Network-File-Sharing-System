import socket
import os

HOST = '127.0.0.1'
PORT = 5000
KEY = 42

def encrypt_decrypt(data: bytes) -> bytes:
    return bytes([b ^ KEY for b in data])

client_socket = socket.socket()
client_socket.connect((HOST, PORT))

# ---------------- AUTHENTICATION ----------------
print(client_socket.recv(1024).decode(), end="")
username = input().strip()
client_socket.send(username.encode())

print(client_socket.recv(1024).decode(), end="")
password = input().strip()
client_socket.send(password.encode())

auth_msg = client_socket.recv(1024).decode()
print(auth_msg)
if "failed" in auth_msg.lower():
    client_socket.close()
    exit()

print("Commands: list | download <filename> | upload <filepath> | exit")

# ---------------- MAIN LOOP ----------------
while True:
    command = input("\nEnter command: ").strip()
    client_socket.send(command.encode())

    if command.lower() == "exit":
        print("🔒 Connection closed.")
        break

    elif command.lower() == "list":
        data = client_socket.recv(4096).decode()
        print("\n--- Server Files ---")
        print(data)

    elif command.lower().startswith("download "):
        filename = command.split(" ", 1)[1]
        status = client_socket.recv(1024).decode()
        if status == "FOUND":
            with open(f"downloaded_{filename}", "wb") as f:
                enc_data = client_socket.recv(10_000_000)
                f.write(encrypt_decrypt(enc_data))
            print(f"✅ File '{filename}' downloaded & decrypted successfully.")
        else:
            print(f"❌ File '{filename}' not found on the server.")

    elif command.lower().startswith("upload "):
        path = command.split(" ", 1)[1].strip('"')
        if not os.path.isfile(path):
            print(f"❌ File '{path}' not found.")
            continue
        filename = os.path.basename(path)
        status = client_socket.recv(1024).decode()
        if status == "READY":
            with open(path, "rb") as f:
                data = f.read()
                client_socket.sendall(encrypt_decrypt(data))
            msg = client_socket.recv(1024).decode()
            print(msg)
        else:
            print("⚠️ Server not ready.")

    else:
        msg = client_socket.recv(1024).decode()
        print(msg)

client_socket.close()
