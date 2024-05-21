import random
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

# randomize macs to simulate servers
mac_list = ["22:22:22:22:22:22","33:33:33:33:33:33", "00:00:00:00:00:00", "44:44:44:44:44:44"]
random_mac = mac_list[random.randint(0,len(mac_list)-1)]

my_mac = os.environ.get('MAC',random_mac)
echo = beat_wrapper(s, my_mac)

threading.Thread(target=lambda: every(3, echo)).start()