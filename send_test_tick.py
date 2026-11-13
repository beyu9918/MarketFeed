import socket

payload = '{"symbol":"AAPL","timestamp":"2026-11-04T09:30:00Z","price":210.35,"volume":1500,"bid_price":210.20,"ask_price":210.50,"source":"simulated"}'

with socket.create_connection(("localhost", 9002), timeout=5) as sock:
    sock.sendall((payload + "\n").encode())
    print(sock.recv(4096).decode())
