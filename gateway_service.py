import os
import sys
import time
import json
import serial
import cbor2

DEFAULT_PORT = "socket://127.0.0.1:5555" if os.name == "nt" else "/dev/ttyUSB0"
SERIAL_PORT = os.getenv("SERIAL_PORT", DEFAULT_PORT)
BAUD_RATE = 115200
RETRY_DELAY_SEC = 5

ARCHIVE_FILE = "telemetry_archive.cbor"
MAX_ARCHIVE_BYTES = 1024 * 1024  # Rotasi file otomatis jika mencapai 1 MB

def init_serial_connection(port, baudrate):
    """Membuka koneksi serial dengan mekanisme retry tak terhingga."""
    while True:
        try:
            ser = serial.serial_for_url(port, baudrate=baudrate, timeout=2.0)
            ser.reset_input_buffer()
            print(f"[GATEWAY] Berhasil terhubung ke port {port} @ {baudrate} bps.")
            return ser
        except serial.SerialException as err:
            print(f"[WARN] Port {port} tidak tersedia ({err}). Menunggu {RETRY_DELAY_SEC} dtk...")
            time.sleep(RETRY_DELAY_SEC)

def process_telemetry(raw_line):
    """Memvalidasi integritas pesan JSON dan mengekstrak field telemetri."""
    try:
        data = json.loads(raw_line)
        required_fields = ["node_id", "timestamp", "temp", "hum"]
        if not all(field in data for field in required_fields):
            print(f"[REJECT] Field telemetri tidak lengkap: {raw_line}")
            return None
        return data
    except json.JSONDecodeError as err:
        print(f"[ERROR] Bingkai data korup / bukan format JSON valid: {err}")
        return None

def save_cbor_archive(payload, filename=ARCHIVE_FILE):
    """(a) Konversi payload JSON ke CBOR & (b) Simpan ke file log biner terotasi."""
    record = {
        "local_timestamp": int(time.time()),
        "telemetry": payload
    }
    cbor_bytes = cbor2.dumps(record)

    if os.path.exists(filename) and os.path.getsize(filename) >= MAX_ARCHIVE_BYTES:
        os.rename(filename, f"{filename}.{int(time.time())}.bak")

    with open(filename, "ab") as f:
        f.write(cbor_bytes)

    return len(cbor_bytes)

def main():
    ser = init_serial_connection(SERIAL_PORT, BAUD_RATE)
    while True:
        try:
            if ser.in_waiting > 0:
                raw_bytes = ser.readline()
                line = raw_bytes.decode("utf-8", errors="ignore").strip()
                if not line:
                    continue

                payload = process_telemetry(line)
                if payload:
                    cbor_len = save_cbor_archive(payload)
                    print(
                        f"[INGEST] Node: {payload['node_id']} | "
                        f"Temp: {payload['temp']:.2f} C | "
                        f"Hum: {payload['hum']:.1f}% | "
                        f"Saved CBOR: {cbor_len} Byte -> {ARCHIVE_FILE}"
                    )
            time.sleep(0.01)
        except serial.SerialException:
            print("[CRIT] Sambungan serial terputus secara mendadak! Memulai inisialisasi ulang...")
            ser.close()
            ser = init_serial_connection(SERIAL_PORT, BAUD_RATE)
        except KeyboardInterrupt:
            print("[INFO] Mematikan layanan gateway...")
            ser.close()
            sys.exit(0)

if __name__ == "__main__":
    main()