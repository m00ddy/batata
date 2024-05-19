import socket
import traceback
import time
import threading
import os

def every(delay, callback:callable):
    next_time = time.time() + delay
    while True:
        time.sleep(max(0, next_time - time.time()))

        try:
            callback()
        except Exception as e:
            traceback.print_exc()

        next_time += (time.time() - next_time) // delay*delay + delay


def beat_wrapper(conn: socket.socket, my_mac: str):
    def beat():
        print("--|/\/--")
        conn.send(my_mac.encode())
    return beat

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('localhost', 1337))
print("connected to register socket")
print("starting heartbeat thread...")

my_mac = os.environ.get('MAC', "11:11:11:11:11")
echo = beat_wrapper(s, my_mac)

threading.Thread(target=lambda: every(3, echo)).start()