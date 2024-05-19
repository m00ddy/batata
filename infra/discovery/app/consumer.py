# query the register on an interval, update local list, print it
import threading
import socket
import traceback
import time
import json

local_list = []

def every(delay, callback:callable):
    next_time = time.time() + delay
    while True:
        time.sleep(max(0, next_time - time.time()))

        try:
            local_list = callback()
            print("[local list updated]")
            print(local_list)

        except Exception as e:
            traceback.print_exc()

        next_time += (time.time() - next_time) // delay*delay + delay

def grabber(conn:socket.socket):
    def grab():
       # recieve a LIST
       print("[grabber] sending ready")
       conn.send(b'ready')
       msg = conn.recv(2000) 
       msg = json.loads(msg.decode())
       
       return msg.get("list")
    return grab

# connect to register
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('localhost', 9999))

f = grabber(s)

print("[main] starting thread")
threading.Thread(target=lambda: every(3, f)).start()