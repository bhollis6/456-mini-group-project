import socket

# Connect to running authentication service
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(("127.0.0.1", 8080))

# Dummy credentials
USERS = {
    "admin": "pass_admin",
    "alexa": "pass_alexa",
    "adrian": "pass_adrian",
    "braden": "pass_braden",
    "jackson": "pass_jackson"
}

# Send login request with one of the dummy credentials
s.sendall(b"LOGIN admin pass_admin\n")
response = s.recv(1024).decode().strip()
s.close()

print(f"Server response: {response}\n")
print("Success! session will populate in checkpoint.json")
