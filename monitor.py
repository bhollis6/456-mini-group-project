import socket 
import hmac
import time

UDP_IP = "127.0.0.1"
PORT = 9999
T = 5 # 5 second frequency for heartbeat period
N = 3 # 3 missed beats for timeout
SECRET = b"cs456-minigroup1-secret"

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

server_socket.bind((UDP_IP, PORT))

server_socket.settimeout(T)
last_beat = None

print("Heartbeat monitor started....\n")

while True:
    try:
        data, client_address = server_socket.recvfrom(1024)

        try:
            decoded_data = data.decode().split("|")
        except Exception as e:
            print(f"Malformed packet from {client_address}: {e}")
            continue # discard malformed packet and wait for the next datagram

        if len(decoded_data) == 3:
            seq_str, ts_str, received_mac = decoded_data

            message = f"{seq_str}|{ts_str}".encode()
            expected_mac = hmac.digest(SECRET, message, "sha256").hex()
            if (hmac.compare_digest(expected_mac, received_mac)):
                print("Valid Heartbeat!")
                last_beat = time.time()
            else:
                print("WARNING: Heartbeat MAC verification failed (Possible spoofing attempt)!")
        else:
            print("INVALID BEAT")

    except socket.timeout:
        if last_beat is None:
            continue # We haven't recieved the very first heartbeat yet. Keep waiting and don't count as a miss.
        time_since_last_beat = time.time() - last_beat
        missed_beats = int(time_since_last_beat // T)

        if missed_beats >= N:
            error_occurrence_time = time.strftime("%Y-%m-%d %H:%M:%S")
            print(f"CRITICAL: Auth Service is Down! Missed {missed_beats} consecutives beats in {T * missed_beats} seconds! Occurred at {error_occurrence_time}.")
            with open("error.txt", "a") as f:
                f.write(f"ERROR: Auth Service went silent on {error_occurrence_time}\n")
        else:
            print(f"WARNING: Missed {missed_beats} beat(s)")