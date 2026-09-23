import socket

HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT = 65432        # Update this to match the EA's port

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    print('Waiting for connection from MT4...')
    conn, addr = s.accept()
    with conn:
        print('Connected by', addr)
        data = conn.recv(1024)
        print("Received from MT4:", data.decode())
        # Send "BUY_1_LOT" command to the EA
        conn.sendall(b'BUY_1_LOT')
