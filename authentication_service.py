import os
import time
import socket
import random
import threading
import hmac

# For Task 2, we chose the Authentication/Ticket Service for our security domain
MONITOR_HOST = "127.0.0.1"
MONITOR_PORT = 9999
AUTH_HOST = "0.0.0.0"
AUTH_PORT = 8080
T = 1.0  # 1 second frequency for heartbeat period
N = 3  # 3 missed beats for timeout
SECRET = b"cs456-minigroup1-secret"

# Dummy credentials
USERS = {
    "admin": "pass_admin",
    "alexa": "pass_alexa",
    "adrian": "pass_adrian",
    "braden": "pass_braden",
    "jackson": "pass_jackson"
}

# Crash mechanisms
RANDOM_PROB_REQ = 0.10
BACKGROUND_FAULT_TRIG = 0.005

# Timestamps and log
def log(msg: str) -> None:
    ts = time.strftime("%H:%M:%S")
    print(f"[auth {ts}] {msg}", flush=True)

# Building the hearbeat
def make_heartbeat(seq: int) -> bytes:
    ts = str(int(time.time() * 1000))  # timestamp in milliseconds
    message = f"{seq}|{ts}".encode()
    mac = hmac.digest(SECRET, message, "sha256").hex()
    return message + b"|" + mac.encode()

# Sending the hearbeats
def send_heartbeat(stop_event: threading.Event) -> None:
    sequence = 0
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    while not stop_event.is_set():
        sequence += 1
        sock.sendto(make_heartbeat(sequence), (MONITOR_HOST, MONITOR_PORT))
        log(f"beat {MONITOR_HOST}:{MONITOR_PORT} seq={sequence}")
        stop_event.wait(T)
    sock.close()

# Fault injection thread
def fault_injection() -> None:
    while True:
        time.sleep(0.5)
        if random.random() < BACKGROUND_FAULT_TRIG:
            log("Background fault injected!")
            os._exit(1)  # terminating completely

# Validation and simulated failure
def validate_client(conn: socket.socket, address) -> None:
    try:
        data = conn.recv(1024).decode(errors="ignore").strip()
        if not data:
            return
        if random.random() < RANDOM_PROB_REQ:
            log("Crash on request!")
            os._exit(1)
        # Splitting client request
        splitting_request = data.split(maxsplit=2)
        if len(splitting_request) != 3 or splitting_request[0] != "LOGIN":
            conn.sendall(b"FAILURE! Bad request.\n")
            return
        _, user, password = splitting_request
        if USERS.get(user) == password:
            token = f"token-{user}-{random.randint(1000, 9999)}"
            conn.sendall(f"SUCCESS {token}\n".encode())
            log(f"LOGIN {user} SUCCESS! ({token})")
        else:
            conn.sendall(b"FAILURE wrong credentials\n")
            log(f"LOGIN {user} FAIL!")
    except Exception:
        log("Validation error.")
    finally:
        conn.close()


def main() -> None:
    stop_event = threading.Event()
    threading.Thread(target=send_heartbeat, args=(
        stop_event,), daemon=True).start()
    threading.Thread(target=fault_injection, daemon=True).start()

    # Open TCP listener
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((AUTH_HOST, AUTH_PORT))
    server.listen(10)

    log(f"Auth service listening on... {AUTH_HOST}:{AUTH_PORT}")
    log(f"Heartbeat {MONITOR_HOST}:{MONITOR_PORT} every {T}s")

    try:
        while True:
            conn, address = server.accept()
            threading.Thread(target=validate_client, args=(
                conn, address), daemon=True).start()
    except KeyboardInterrupt:
        log("Shutting down....")
        stop_event.set()
    finally:
        server.close()


if __name__ == "__main__":
    main()
