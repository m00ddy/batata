# consume discovery service to fetch mac address list
import socket
import traceback
import time
import json
import threading
from utils.roundrobin import RoundRobin
from utils.getaddrinfo import resolve

lock = threading.Lock()
init_complete = threading.Event()

DISCOVERY_HOSTNAME = "discovery.batata"
DISCOVERY_PORT = 9999
DISCOVERY_SOCKTYPE = socket.SOCK_STREAM
DISCOVERY_ADDR = resolve(DISCOVERY_HOSTNAME, DISCOVERY_PORT, DISCOVERY_SOCKTYPE)


def every(delay:int,  callback:callable, rr:RoundRobin, server_macs:list):
    next_time = time.time() + delay
    while True:
        time.sleep(max(0, next_time - time.time()))

        try:
            print("**************************************")
            print("DISCVERY CONSUMER UPDATE")
            fresh_list = callback()
            with lock:
                server_macs.clear()
                server_macs.extend(fresh_list)
                rr.update(server_macs)

                print("[DC] local list updated: ", server_macs)
                print("[DC] updated RR")
                print(rr, rr.addrs)
                print("**************************************")
                print()

        except Exception as e:
            traceback.print_exc()
        
        # skip task if behind schedule
        next_time += (time.time() - next_time) // delay*delay + delay

def fetch_mac_list_from_register(s:socket.socket) -> callable:
    def fetch():
       print("[DC] sending ready")
       # ready -->
       # <-- MAC address list
       s.send(b'ready')
       msg = s.recv(2000) 
       msg = json.loads(msg.decode())
       
       return msg.get("list")
    return fetch

def init_mac_list(s: socket.socket) -> list:
    print("[DC] sending init")
    time.sleep(3)
    s.send(b'init')
    msg = s.recv(2000) 
    msg = json.loads(msg.decode())
    print("[DC] mac list initialized to: ", msg.get("list")) 
    if not msg.get("list"):
        time.sleep(1)
        init_mac_list(s)
    return msg.get("list")

def create_mac_fetcher(s: socket.socket, rr:RoundRobin, server_macs:list) -> callable:

    callback = fetch_mac_list_from_register(s)
    interval = 5  #! 5 for testing, 60 in prod

    print(f"register socket ready; fetch interval = {interval} seconds")

    return lambda: every(interval, callback, rr, server_macs)

def init_consumer(rr:RoundRobin, server_macs:list) -> (socket.socket, list, object,bool):
    # connect to register
    print("[DC init] creating register socket...")

    # socket to discovery service
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(DISCOVERY_ADDR)
    print("[DC init] connected to discovery service")
    server_macs.clear() 
    server_macs.extend(list(init_mac_list(s)))
    rr.update(server_macs)

    try:
        print("[DC init]", server_macs)
        print("[DC init]", rr, rr.addrs)
    except Exception as e:
        print("[DC init EXCEPTION]", e)

    
    return s, True

def consume_discovery_service(rr:RoundRobin, server_macs:list) -> (bool):
    s, ok = init_consumer(rr, server_macs)
    if ok:
        print("discovery consumer init complete") 
        init_complete.set()
    
    mac_fetcher = create_mac_fetcher(s, rr, server_macs)
    t = threading.Thread(target=mac_fetcher)

    init_complete.wait() 
    print("--- launching discovery consumer thread ---")
    t.start()

    return True


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