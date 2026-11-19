import json
import time
import cbor2
import telemetry_pb2

# Data uji standar telemetri stasiun cuaca
data_dict = {
    "node_id": "ESP32_UNIB_01",
    "timestamp": 1794212500,
    "seq": 1024,
    "temp": 29.85,
    "hum": 78.4,
    "lux": 650,
    "battery": 3.95,
    "status": "ONLINE"
}

ITERATIONS = 10000

# 1. Evaluasi JSON
t0 = time.perf_counter()
for _ in range(ITERATIONS):
    json_str = json.dumps(data_dict)
    json_bytes = json_str.encode('utf-8')
t_json = (time.perf_counter() - t0) / ITERATIONS * 1e6  # microsecond

# 2. Evaluasi CBOR
t0 = time.perf_counter()
for _ in range(ITERATIONS):
    cbor_bytes = cbor2.dumps(data_dict)
t_cbor = (time.perf_counter() - t0) / ITERATIONS * 1e6

# 3. Evaluasi Protocol Buffers
proto_obj = telemetry_pb2.TelemetryPacket(
    node_id=data_dict["node_id"],
    timestamp=data_dict["timestamp"],
    seq=data_dict["seq"],
    temp=data_dict["temp"],
    hum=data_dict["hum"],
    lux=data_dict["lux"],
    battery=data_dict["battery"],
    status=data_dict["status"]
)
t0 = time.perf_counter()
for _ in range(ITERATIONS):
    proto_bytes = proto_obj.SerializeToString()
t_proto = (time.perf_counter() - t0) / ITERATIONS * 1e6

len_json = len(json_bytes)
len_cbor = len(cbor_bytes)
len_proto = len(proto_bytes)

print("\n================ HASIL BENCHMARK SERIALISASI IOT ================")
print(f"Format JSON    : {len_json:3d} Byte | Encode: {t_json:6.2f} us | Reduksi:   0.0%")
print(f"Format CBOR    : {len_cbor:3d} Byte | Encode: {t_cbor:6.2f} us | Reduksi: {(len_json-len_cbor)/len_json*100:5.1f}%")
print(f"Format Protobuf: {len_proto:3d} Byte | Encode: {t_proto:6.2f} us | Reduksi: {(len_json-len_proto)/len_json*100:5.1f}%")
print("=================================================================\n")