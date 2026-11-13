import csv
import socket
from pathlib import Path

CSV_PATH = Path(__file__).resolve().parents[1] / "mock_data" / "sample_ticks.csv"
HOST = "localhost"
PORT = 9002

with CSV_PATH.open("r", encoding="utf-8") as f:
    reader = csv.reader(f)
    for row in reader:
        payload = ",".join(row)
        with socket.create_connection((HOST, PORT), timeout=5) as sock:
            sock.sendall((payload + "\n").encode())
            try:
                print(sock.recv(4096).decode().strip())
            except socket.timeout:
                print("TIMEOUT")
