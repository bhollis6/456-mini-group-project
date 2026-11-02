import socket
import sys

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

if len(sys.argv) >= 3 and sys.argv[1].lower() == "verify":
    token = sys.argv[2]
    s.sendall(f"VERIFY {token}\n".encode())
    response = s.recv(1024).decode().strip()
    s.close()
    print(f"Server response: {response}")
else:
    # Send login request with one of the dummy credentials
    s.sendall(b"LOGIN admin pass_admin\n")
    response = s.recv(1024).decode().strip()
    s.close()
    print(f"Server response: {response}")
    if response.startswith("SUCCESS"):
        print("Login succeeded. Session saved to checkpoint.json")
    else:
        print("Login failed.")
