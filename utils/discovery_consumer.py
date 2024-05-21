# consume discovery service to fetch mac address list
import socket
import traceback
import time
import json
import threading
from utils.roundrobin import RoundRobin

lock = threading.Lock()
init_complete = threading.Event()

DISCOVERY_IP = "172.16.238.100"
DISCOVERY_PORT = 9999
DISCOVERY_ADDR = (DISCOVERY_IP, DISCOVERY_PORT)

with lock:
    # MAAAAAAAAAAAAACS
    SERVER_MACS = None

    # roundrobinrevolver object
    RR = None



def every(delay:int,  callback:callable):
    global SERVER_MACS
    global RR

    next_time = time.time() + delay
    while True:
        time.sleep(max(0, next_time - time.time()))

        try:
            with lock:
                SERVER_MACS = callback()
                RR.update(SERVER_MACS)

                print("[fetcher] local list updated")
                print(SERVER_MACS)
                print("NEXT RR", next(RR))
                print()

        except Exception as e:
            traceback.print_exc()
        
        # skip task if behind schedule
        next_time += (time.time() - next_time) // delay*delay + delay

def fetch_mac_list_from_register(s:socket.socket) -> callable:
    def fetch():
       print("[fetcher] sending ready")
       # ready -->
       # <-- MAC address list
       s.send(b'ready')
       msg = s.recv(2000) 
       msg = json.loads(msg.decode())
       
       return msg.get("list")
    return fetch

def init_mac_list(s: socket.socket) -> list:
    print("[fetcher] sending init")

    #! backhanded approach
    # time.sleep(2)

    s.send(b'init')
    msg = s.recv(2000) 
    msg = json.loads(msg.decode())
    print("[fetcher] mac list initialized to: ", msg.get("list")) 
    return msg.get("list")

def create_mac_fetcher(s: socket.socket) -> callable:

    f = fetch_mac_list_from_register(s)
    interval = 5  #! 5 for testing, 60 in prod

    print(f"register socket ready; fetch interval = {interval} seconds")

    return lambda: every(interval, f)

def init_consumer() -> (socket.socket, list, object,bool):

    # connect to register
    print("creating register socket...")

    # socket to discovery service
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(DISCOVERY_ADDR)


    server_macs = list(init_mac_list(s))
    rr = RoundRobin(server_macs)

    try:
        print(next(rr))
        print("[consumer]", server_macs)
        print("[consumer]", rr)
        print("[consumer] next rr", next(rr))
    except Exception as e:
        print("[consumer]", e)

    
    return s, server_macs, rr, True

def consume_discovery_service() -> (bool, object, list):
    s, server_macs, rr, ok = init_consumer()
    if ok:
        print("discovery consumer init complete") 
        global SERVER_MACS
        SERVER_MACS = server_macs
        global RR
        RR = rr
        init_complete.set()
    
    init_complete.wait()
    
    print("--- launching discovery consumer thread ---")
    mac_fetcher = create_mac_fetcher(s)
    threading.Thread(target=mac_fetcher).start()
    return True, RR, SERVER_MACS


if __name__ == "__main__":
    try:
        consume_discovery_service()
    except Exception as e:
        print("error consuming discovery service")
        print(e)
    
    while True:
        time.sleep(1)
        with lock:
            print(next(RR))