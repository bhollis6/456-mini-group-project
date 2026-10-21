import socket 
import hmac
import time

UDP_IP = "127.0.0.1"
PORT = 9999
T = 1.0 # 1 second frequency for heartbeat period
N = 3 # 3 missed beats for timeout
SECRET = b"cs456-minigroup1-secret"

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

server_socket.bind((UDP_IP, PORT))

server_socket.settimeout(T)
last_beat = time.time()

print("Heartbeat monitor started....\n")

while True:
    try:
        data, client_address = server_socket.recvfrom(1024)

        decoded_data = data.decode().split("|")

        if len(decoded_data) == 3:
            seq_str, ts_str, received_mac = decoded_data

            message = f"{seq_str}|{ts_str}".encode()
            expected_mac = hmac.digest(SECRET, message, "sha256").hex()
            if (hmac.compare_digest(expected_mac, received_mac)):
                print("Valid Heartbeat!")
                last_beat = time.time()
        else:
            print("INVALID BEAT")

    except socket.timeout:
        time_since_last_beat = time.time() - last_beat
        missed_beats = int(time_since_last_beat // T)

        if missed_beats >= N:
            error_occurrence_time = time.time()
            print(f"Critical! Auth Service is Down! Missed {missed_beats} consecutives beats in 3 seconds! Occurred at {error_occurrence_time}.")
            with ("error.txt", "a") as f:
                f.write(f"ERROR: Auth Service went silent on {error_occurrence_time}\n")
        else:
            print(f"Warning! Missed {missed_beats} beat(s)")