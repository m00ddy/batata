# send MAC address as a heartbeat to register
#! hardcoded
# HOST = "192.168.25.150"
# PORT = 1337

# print(f"os environ MAC: {os.environ['MAC']}")

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

def init_hearbeat(discovery_ip:str) -> (socket.socket, str):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((discovery_ip, 1337))
    print("connected to register socket")
    print("starting heartbeat thread...")
    my_mac = os.environ.get('MAC',"ERRROR GETTING MAC")
    return s, my_mac

def start_hearbeat(discovery_ip:str) -> bool:
    s, my_mac = init_hearbeat(discovery_ip)
    echo = beat_wrapper(s, my_mac)
    threading.Thread(target=lambda: every(3, echo)).start()
    return True



if __name__ == "__main__":
    # randomize macs to simulate servers
    mac_list = ["22:22:22:22:22", "33:33:44:33:33"]
    random_mac = mac_list[random.randint(0,len(mac_list))]
    print("beating")    