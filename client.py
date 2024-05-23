# client code goes here
# import sys
import socket
import time

# SERVER = input("enter server ip (default localhost): ")
# if SERVER == "":
#     SERVER = "localhost"
# PORT = 8080
# ADDR = (SERVER, PORT)

hostname, port = input("enter service hostname (example.com:1337): ").split(":") 
addr_list, = socket.getaddrinfo(hostname, port, type=socket.SOCK_DGRAM)
*_, ADDR = addr_list
print(f"[DNS] resolved {hostname}:{port} to {ADDR}")

# UDP socket
with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
    s.settimeout(5)
    sdata_list = [
        "500+500",
        "1337*3",
        "1+2",
        "0+4",
        "10000+2",
        "5*-2",
        "-5*-2"
    ]
    for i in range(len(sdata_list)):
        time.sleep(2)
        sdata = sdata_list[i]
        s.sendto(sdata.encode(), ADDR)
        print("sending ", sdata)
        data, addr = s.recvfrom(2000)
        print(">> ", data)

# usage_string = "usage:\n\tcalc.py add 4 5\n\tcalc.py mult 5 6"

# try:
#     op = sys.argv[1]
#     if op not in ["add", "mult"]:
#         raise ValueError("invalid operation")
#     if op == None:
#         raise ValueError("missing operation")
    
# except ValueError as err:
#     print(err)
# except IndexError as err:
#     print("please provide an operation")
# finally:
#         print(usage_string)


# # TODO: enforce each numbber is only 4 bytes
