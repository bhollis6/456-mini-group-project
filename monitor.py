import socket 
import hmac
import time

UDP_IP = "127.0.0.1"
PORT = 9999
T = 5 # 5 second frequency for heartbeat period
N = 3 # 3 missed beats for timeout
SECRET = b"cs456-minigroup1-secret"

# Left it here just in case
def send_payload(action: str, secret: bytes) -> bytes:
    ts = str(int(time.time() * 1000))
    message = f"{action}|{ts}".encode()
    mac = hmac.digest(secret, message, "sha256").hex()
    return message + b"|" + mac.encode()

# Left it here just in case
def verify_payload(raw_data: bytes, secret: bytes) -> tuple[bool, str]:
    try:
        decoded_data = raw_data.decode().split("|")
        message = f"{decoded_data[0]}|{decoded_data[1]}".encode()
        expected_mac = hmac.digest(secret, message, "sha256").hex()
        if hmac.compare_digest(expected_mac, decoded_data[2]):
            return True, decoded_data[0]
    except Exception:
        pass
    return False, ""

def log(msg: str) -> None:
    ts = time.strftime("%H:%M:%S")
    print(f"[monitor {ts}] {msg}", flush=True)

def main() -> None:
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((UDP_IP, PORT))
    last_beat = None
    awaiting_failover = False

    log(f"Heartbeat monitor started on {UDP_IP}:{PORT}....")
    server_socket.settimeout(T + 1.0)

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

            elif decoded_data[0] == "ACTIVATED":
                activated_acknowledgement = time.strftime("%Y-%m-%d %H:%M:%S")
                log(f"Valid ACTIVATED response received at {activated_acknowledgement}. Resuming normal operations.")
                last_beat = time.time()
                awaiting_failover = False

            else:
                log("INVALID BEAT")

        except socket.timeout:
            if last_beat is None:
                continue # We haven't received the very first heartbeat yet. Keep waiting and don't count as a miss.
            time_since_last_beat = time.time() - last_beat
            missed_beats = int(time_since_last_beat // T)

            if missed_beats >= N:
                error_occurrence_time = time.strftime("%Y-%m-%d %H:%M:%S")

                if not awaiting_failover:

                    log(f"CRITICAL: Auth Service is Down! Missed {missed_beats} consecutive beats in {T * missed_beats} seconds! Occurred at {error_occurrence_time}.")
                    with open("error.txt", "a") as f:
                        f.write(f"ERROR: Auth Service went silent on {error_occurrence_time}\n")

                    awaiting_failover = True

                    packet_sent_time = time.strftime("%Y-%m-%d %H:%M:%S")
                    payload_message = send_payload("SERVICE_CRASHED", SECRET)
                    server_socket.sendto(payload_message, (UDP_IP, 9998)) 

                    log(f"Promotional signal has been sent to the failover process at {packet_sent_time}. Waiting for confirmation.")

            else:
                log(f"WARNING: Missed {missed_beats} beat(s)")

        except ConnectionResetError:
            log("CRITICAL: No failover process has been detected.")

if __name__ == "__main__":
    main()
