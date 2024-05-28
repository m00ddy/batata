# the 8 byte calculator protocol !

import struct
from sys import getsizeof
from re import findall

OP_char_to_code = {
    "+": 1,
    "*": 2
}

OP_code_to_function = {
    1: lambda x, y :x+y,
    2: lambda x, y: x*y,
}

def lb_to_srv(client_data:bytes) -> bytes:
    # handle udp load coming from client, prepare it for server.
    # 1+2  --> b'\x00\x00\x00\x01\x00\x00\x00\x02\x01'
    client_data = client_data.decode()
    # extract operator
    op = None
    try:
        op, = findall(r'\d+(\*|\+)\d+', client_data)
    except Exception as e:
        print("invalid operation, ", e)
        raise ValueError("operator not permitted")


    math_exp = client_data.split(op)
    # print("[proto] ", math_exp)
    x, y = math_exp
    print(x, y, op)
    op_code = OP_char_to_code[op]

    # i - 4 byte int
    # B - 1 unsigned byte (used to identify operation)
    return struct.pack("!iiB", int(x), int(y), op_code)



def srv_to_lb(packed_client_data:bytes, srv_id:int=None) -> bytes:
    # prepare packet on server for LB
    x, y, op = struct.unpack("!iiB", packed_client_data)

    # when server doesn't provide ID, set it to 0.
    if not srv_id:
        srv_id = 0

    # compute result and pack it with server ID
    result = OP_code_to_function[op](x, y)

    # q - 8 byte long
    return struct.pack("!qB", result, srv_id)

def lb_to_client(packed_result:bytes) -> bytes:
    res, srv_id= struct.unpack("!qB", packed_result)
    client_string = f"result: {res}"
    
    if srv_id!=0:
        client_string+=f"; from server {srv_id}"
    
    return client_string.encode()

if __name__ == "__main__":
    # *** for testing purposes *** 

    encodedbla = lb_to_srv("5*9")
    print(encodedbla)
    result = srv_to_lb(encodedbla, 8)
    finresult, = struct.unpack("!q", result)
    print(getsizeof(finresult))