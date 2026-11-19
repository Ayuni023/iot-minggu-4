import os
import time
import json
import random
import socket

def run_windows_socket_simulator(host="0.0.0.0", port=5555):
    """Simulator serial virtual menggunakan TCP Loopback Socket untuk Windows."""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((host, port))
    server.listen(1)

    port_url = f"socket://{host}:{port}"
    print(f"[SIMULATOR] Port serial virtual siap pada: {port_url}")
    print("[SIMULATOR] Gunakan nama port di atas pada skrip gateway Anda!")
    print("[SIMULATOR] Menunggu koneksi dari gateway_service.py...\n")

    seq = 0
    while True:
        conn, addr = server.accept()
        print(f"[SIMULATOR] Gateway terhubung dari {addr}\n")
        try:
            while True:
                seq += 1
                payload = {
                    "node_id": "ESP32_VIRTUAL_01",
                    "timestamp": int(time.time()),
                    "seq": seq,
                    "temp": round(random.uniform(26.0, 31.5), 2),
                    "hum": round(random.uniform(70.0, 85.0), 1),
                    "lux": random.randint(250, 950),
                    "battery": round(random.uniform(3.75, 4.15), 2),
                    "status": "ONLINE"
                }
                json_bytes = (json.dumps(payload) + "\n").encode("utf-8")
                conn.sendall(json_bytes)
                print(f"[SIMULATOR -> TX] {payload}")
                time.sleep(2.0)
        except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError, OSError):
            print("[SIMULATOR] Koneksi gateway terputus. Menunggu koneksi ulang...\n")
            conn.close()

def run_posix_pty_simulator():
    """Simulator serial virtual menggunakan pseudo-terminal (pty) untuk Linux/macOS."""
    import pty
    master, slave = pty.openpty()
    slave_name = os.ttyname(slave)
    print(f"[SIMULATOR] Port serial virtual siap pada: {slave_name}")
    print("[SIMULATOR] Gunakan nama port di atas pada skrip gateway Anda!\n")

    seq = 0
    while True:
        seq += 1
        payload = {
            "node_id": "ESP32_VIRTUAL_01",
            "timestamp": int(time.time()),
            "seq": seq,
            "temp": round(random.uniform(26.0, 31.5), 2),
            "hum": round(random.uniform(70.0, 85.0), 1),
            "lux": random.randint(250, 950),
            "battery": round(random.uniform(3.75, 4.15), 2),
            "status": "ONLINE"
        }
        json_bytes = (json.dumps(payload) + "\n").encode("utf-8")
        os.write(master, json_bytes)
        print(f"[SIMULATOR -> TX] {payload}")
        time.sleep(2.0)

if __name__ == "__main__":
    if os.name == "nt":
        run_windows_socket_simulator()
    else:
        run_posix_pty_simulator()