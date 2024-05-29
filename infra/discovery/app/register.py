import socket
import threading
import json


conn_to_mac = {}


# returns a new tcp socket bound to ip, port
def prepare_tcp_socket(port: int, ip:str="0.0.0.0") -> socket.socket:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((ip, port))

    return s


# listen for heartbeats from servers, and maintain a local list of live servers MAC addresses
def generic_listener(port:int, target_func:callable, name:str="generic"):
    # live servers send their MACs here
    s = prepare_tcp_socket(port=port)
    s.listen(5)

    thread_list = []

    try:
        while True:
            print(f"[{name}] waiting on new client to dial")
            conn, addr = s.accept()
            print(f"[{name}] dispatching thread to serve client")
            t = threading.Thread(target=target_func, args=(conn,addr)) 
            t.start()
            thread_list.append(t)

    except KeyboardInterrupt :
        print("program stopped by ctrl+C")

    finally:
        if s:
            s.close()
        for t in thread_list:
            t.join()




def main():

    listener_port = 1337
    heartbeat_listener = generic_listener

    # lb uses this to query live server list
    producer_port = 9999
    mac_producer = generic_listener

    t1 = threading.Thread(target=heartbeat_listener, args=(listener_port, heartbeat_handler, "heartbeat_listener"))
    t2 = threading.Thread(target=mac_producer, args=(producer_port, wait_for_lb_ready, "producer"))

    t1.start()
    t2.start()
    
#? wait_for_lb_ready and heartbeat handler conform to an interface [idk what to call it]

def wait_for_lb_ready(conn:socket.socket, addr):
    while True:
        msg = conn.recv(2000)
        if msg.decode() == "ready" or msg.decode() == "init":
            print("[handler] client is ready for new list")
            data = json.dumps({"list": list(conn_to_mac.values())})
            print("sending", data)
            conn.send(data.encode())


def heartbeat_handler(conn:socket.socket , addr):
    print(f"handling client {addr} heartbeats -----------")
    alive  = True
    while alive:
        msg = conn.recv(2000)
        if not msg:
            print("connection closed by ", addr)
            handle_closed_conn(conn)
            alive = False

        elif msg:
            print(msg.decode())
            conn_to_mac[conn.fileno()] = msg.decode()
            print(conn_to_mac)

    print("end---------------")

def handle_closed_conn(conn: socket.socket):
    print("handling a closed connection from ", conn.fileno())
    del conn_to_mac[conn.fileno()]
    print(conn_to_mac)
    conn.close()




if __name__ == "__main__":
    main()
