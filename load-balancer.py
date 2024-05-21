import socket
import psutil
from scapy.all import *
from utils.protocol import *
from utils.discovery_consumer import *
import select
import threading


HOST = "0.0.0.0"
UDP_SOCK_PORT = 8080
TCP_SOCK_PORT = 7070
UDP_ADDR = (HOST, UDP_SOCK_PORT)
TCP_ADDR = (HOST, TCP_SOCK_PORT)
TIMEOUT = 3

ETH_P_ALL = 3  # raw socket protocol prevent kernel processing on packets

read_addr_lock = threading.Lock()
discovery_consumed_event = threading.Event()


# UDP socket: client <--> load balancer
client_socket  = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
client_socket.bind(UDP_ADDR)


# check if br-backend in interfaces
interfaces = socket.if_nameindex()
print(interfaces)
for (i, name) in interfaces:
    if name == "br-backend":
        print(f"interface {name} is up")

# obtain MAC and IP
try:
    my_MAC = None
    my_IP = None
    my_if_addrs = psutil.net_if_addrs()['br-backend']
    for item in my_if_addrs:
        if item.family == socket.AF_INET:
            print("interface IP", item.address)
            my_IP = item.address
        if item.family == socket.AF_PACKET:
            print("interface MAC", item.address)
            my_MAC = item.address

    # RAW socket: load balancer <--> servers
    srv_socket = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(ETH_P_ALL))
    srv_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv_socket.settimeout(TIMEOUT)
    srv_socket.bind(('br-backend', 0))
except KeyError as e:
    print("interface not found")
    print(e)


# takes care of fetching and updating server address list; just call next(RR) to get next server addr
ok, RR, SERVER_MACS = consume_discovery_service()
if ok:
    discovery_consumed_event.set()
    print("OK")


# discovery_consumed_event.wait()
# while True:
#     time.sleep(1)
#     print("LOADBALACNER MACLIST", SERVER_MACS)
#     next_addr = next(RR)
#     print(next_addr) 

def event_loop():
    discovery_consumed_event.wait()
    while True:
        print("======================")
        # recv data from client
        client_data, client_addr = client_socket.recvfrom(2000)

        # we assume data coming from client follows protocol format: b'4+5'
        print("received: ", client_data, "from: ", client_addr)

        try:
            proto_bytes = lb_to_srv(client_data.decode()) 
        except Exception as e:
            print(e)
            client_socket.sendto(str(e).encode(), client_addr)
            continue

        # select a server
        server_ether_addr = None
        with lock:
            server_ether_addr = next(RR)
            print("next server: ", server_ether_addr)
        
        print("sending to ", server_ether_addr)

        # send to server
        ether_frame = Ether(dst=server_ether_addr)/Raw(load=proto_bytes)
        sendp(ether_frame, 'br-backend')

        # reply from server
        rcv_data = None
        pkt = None
        try:
        # filter for only packets coming from server, because raw socket gets all packets
            while rcv_data is None or pkt is None:
                # read before timeout
                ready, _, _ = select.select([srv_socket], [], [], TIMEOUT)
                if srv_socket in ready:
                    data = srv_socket.recv(2000)
                    current_pkt = Ether(data)
                    
                    if current_pkt.src == server_ether_addr :
                        rcv_data = data
                        pkt = current_pkt
                else:
                    raise TimeoutError(f"[TIMEOUT] packet not recieved in {TIMEOUT} seconds")
        except TimeoutError as err:
            print(err)
            client_socket.sendto("timeout, server seems to be offline. please try again".encode(), client_addr)
            continue

        print(pkt)
        print(pkt.load)
        print("unpacking result")
        res, srv_id= struct.unpack("!qB", pkt.load)
        print(srv_id)
        print(f"redirecting {res} to client...")

        client_socket.sendto((str(res)+" from server: "+str(srv_id)).encode(), client_addr)

event_loop()