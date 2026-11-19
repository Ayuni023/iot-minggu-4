FROM python:3.11-slim

# Pasang dependensi kompilator C untuk pustaka serial jika diperlukan
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Manfaatkan caching layer Docker untuk file requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Salin kode aplikasi
COPY gateway_service.py .
COPY telemetry_pb2.py .

# Akses grup dialout untuk membaca port serial fisik
RUN usermod -a -G dialout root

CMD ["python", "-u", "gateway_service.py"]