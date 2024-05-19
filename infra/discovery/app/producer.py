import json
import socket
import threading
import random

matrix  = [
    [1, 2, 3, 4],
    [2, 4],
    [1, 2, 3]
]

def client_handler(conn: socket.socket):
    while True:
        msg = conn.recv(2000)
        if msg.decode() == "ready":
            print("[handler] client is ready for new list")
            data = json.dumps({"list": matrix[random.randint(0,2)]})
            print("sending", data)
            conn.send(data.encode())




s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('localhost', 9999))
s.listen(1)
while True:
    print("[main] waiting on new connection")
    conn, addr = s.accept()
    print(f"[main] conncection {addr} dispatched to thread")
    threading.Thread(target=client_handler(conn)).start()