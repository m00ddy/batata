import os
import socket
from scapy.all import *
from protocol import *
import threading
from heartbeat import start_hearbeat


ID = int(os.environ["ID"])
my_MAC = os.environ["MAC"]
discovery_ip = os.environ["DISCOVERY_IP"]
# br-backend interface MAC
# br-backend is comm channel between server and LB
BR_BACKEND = os.environ["BR_BACKEND"] 
LB_MAC = "00:11:11:11:11:11" 

#TODO: get this dynamically
# lb uses enp0s3 to send frames to server
# enp0s3_mac  = "08:00:27:69:29:66"



# display my interfaces
# interfaces = socket.if_nameindex()
# print(interfaces)

hearbeat_started = threading.Event()


# recieve ethernet packets
s = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(0x0003))
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(('eth0', 0))

#! listen for discovery IP

ok = start_hearbeat(discovery_ip)
if ok:
    hearbeat_started.set()


hearbeat_started.wait()
print("ready to recv packets")

while True:
    try:
        raw_data = s.recv(2000)
        ether_data = Ether(raw_data)

        # don't handle ARP packets
        if ARP in ether_data:
            continue
    
        # if i sent the packet don't handle it
        if ether_data.src == my_MAC:
            continue
        
        if ether_data.src == LB_MAC and ether_data.dst == my_MAC:
            print("--------------------------------------------------------------------")
            print("received ", ether_data.load, "from: ", LB_MAC)

            proto_data = ether_data.load
            reply_data = srv_to_lb(proto_data, ID) 

            print("sending: ", reply_data)

            # send to comm channel, LB will catch it.
            reply_pkt = Ether(dst=BR_BACKEND)/Raw(load=reply_data)

            print("sending to ", BR_BACKEND, "out eth0")
            sendp(reply_pkt, "eth0")
            print("--------------------------------------------------------------------")
        
        # for testing purposes
        # elif b'ping' in ether_data.load:
        #     print("recieved: ", ether_data.load," from: ", ether_data.src)
        #     # send to MAC of interface br-backend [this is what connects servers to LB]
        #     # reply_data = f"pong, regards from {os.environ['id']}"
        #     reply_data = "pong. regards from server "+ID
        #     print("sendin: ", reply_data)
        #     reply_pkt = Ether(dst=SERVER_MAC)/Raw(load=reply_data.encode())
        #     print("sending to ", SERVER_MAC, "out eth0")
        #     sendp(reply_pkt, "eth0")

    except Exception as e:
        print("shitty packet recieved")
        print(e)