import socket 
import hmac
import time

UDP_IP = "127.0.0.1"
PORT = 9999
T = 5 # 5 second frequency for heartbeat period
N = 3 # 3 missed beats for timeout
SECRET = b"cs456-minigroup1-secret"

def log(msg: str) -> None:
    ts = time.strftime("%H:%M:%S")
    print(f"[monitor {ts}] {msg}", flush=True)

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((UDP_IP, PORT))
server_socket.settimeout(T)
last_beat = None

log(f"Heartbeat monitor started on {UDP_IP}:{PORT}....")

while True:
    try:
        data, client_address = server_socket.recvfrom(1024)

        try:
            decoded_data = data.decode().split("|")
        except Exception as e:
            log(f"Malformed packet from {client_address}: {e}")
            continue # discard malformed packet and wait for the next datagram

        if len(decoded_data) == 3:
            seq_str, ts_str, received_mac = decoded_data

            message = f"{seq_str}|{ts_str}".encode()
            expected_mac = hmac.digest(SECRET, message, "sha256").hex()
            if (hmac.compare_digest(expected_mac, received_mac)):
                log(f"Valid Heartbeat! (seq={seq_str})")
                last_beat = time.time()
            else:
                log("WARNING: Heartbeat MAC verification failed (Possible spoofing attempt)!")
        else:
            log("INVALID BEAT")

    except socket.timeout:
        if last_beat is None:
            continue # We haven't recieved the very first heartbeat yet. Keep waiting and don't count as a miss.
        time_since_last_beat = time.time() - last_beat
        missed_beats = int(time_since_last_beat // T)

        if missed_beats >= N:
            error_occurrence_time = time.strftime("%Y-%m-%d %H:%M:%S")
            log(f"CRITICAL: Auth Service is Down! Missed {missed_beats} consecutive beats in {T * missed_beats} seconds! Occurred at {error_occurrence_time}.")
            with open("error.txt", "a") as f:
                f.write(f"ERROR: Auth Service went silent on {error_occurrence_time}\n")
        else:
            log(f"WARNING: Missed {missed_beats} beat(s)")
