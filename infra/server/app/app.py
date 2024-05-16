import os
import socket
from scapy.all import *
from protocol import *


ID = int(os.environ["ID"])

# my interface
interfaces = socket.if_nameindex()
print(interfaces)

# obtain MAC and IP
my_MAC = os.environ["MAC"]

# br-backend interface MAC
# br-backend is comm channel between server and LB
LB_MAC = os.environ["LB_MAC"] # br-backend
enp0s3_mac  = "08:00:27:69:29:66"

# recieve ethernet packets
s = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(0x0003))
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(('eth0', 0))

while True:
    try:
        raw_data = s.recv(2000)
        ether_data = Ether(raw_data)

        if ARP in ether_data:
            continue
        # if i'm the packet src don't handle it
        if ether_data.src == my_MAC:
            continue
        
        if ether_data.src == enp0s3_mac and ether_data.dst == my_MAC:
            print("received ", ether_data.load, "from: ", enp0s3_mac)

            proto_data = ether_data.load
            reply_data = srv_to_lb(proto_data, ID) 

            print("sending: ", reply_data)

            reply_pkt = Ether(dst=LB_MAC)/Raw(load=reply_data)

            print("sending to ", LB_MAC, "out eth0")
            sendp(reply_pkt, "eth0")
        

        elif b'ping' in ether_data.load:
            print("recieved: ", ether_data.load," from: ", ether_data.src)
            # send to MAC of interface br-backend [this is what connects servers to LB]
            # reply_data = f"pong, regards from {os.environ['id']}"
            reply_data = "pong. regards from server "+ID
            print("sendin: ", reply_data)
            reply_pkt = Ether(dst=SERVER_MAC)/Raw(load=reply_data.encode())


            print("sending to ", SERVER_MAC, "out eth0")
            sendp(reply_pkt, "eth0")
    except Exception as e:
        print("shitty packet recieved")
        print(e)