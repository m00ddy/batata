# open tcp connection to LB and send hardware address
import socket
import os

#! hardcoded
# HOST = "192.168.25.150"
# PORT = 1337

# get my MAC address to send to LB for *self registration*
#! THIS IS STUPID
# my_MAC = None
# if_name = "eth0"
# mac_addresses = psutil.net_if_addrs()[if_name]
# for item in mac_addresses:
#     if item.family == socket.AF_PACKET:
#         print("interface MAC", item.address)
#         my_MAC = item.address
#         #TODO use this later in healthcheck
#         os.environ["MAC"] = my_MAC

# print(my_MAC)
# print(f"os environ MAC: {os.environ['MAC']}")

# try:
#     s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     s.connect((HOST, PORT))
#     s.send(my_MAC.encode())
# except Exception as e:
#     print(e)