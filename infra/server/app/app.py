import os
import socket
from scapy.all import *
import psutil
from protocol import *

# later OP[opcode](x, y)
OP = {
    1: lambda x, y :x+y,
    2: lambda x, y: x*y,
}

ID = int(os.environ["ID"])

# my interface
interfaces = socket.if_nameindex()
print(interfaces)

# obtain MAC and IP
my_MAC = None
if_name = 'eth0'
mac_addresses = psutil.net_if_addrs()[if_name]
for item in mac_addresses:
    if item.family == socket.AF_PACKET:
        print("interface MAC", item.address)
        my_MAC = item.address

print(my_MAC)

# br-backend interface MAC
# br-backend is comm channel between server and LB
# TODO: make LB advertise this to server
LB_MAC = "02:42:e1:c1:e2:80"  # br-backend
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