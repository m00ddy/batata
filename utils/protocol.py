# the 8 byte calculator protocol !

# give me 2 numbers i'll craft a packet
# but app must be able to handle it

import struct
from sys import getsizeof
from re import findall

OP_char_to_code = {
    "+": 1,
    "*": 2
}

OP_code_to_operation = {
    1: lambda x, y :x+y,
    2: lambda x, y: x*y,
}

def lb_to_srv(client_data:str) -> bytes:
    # handle udp load coming from client, prepare it for server
    # data: 1+2
    op = None
    try:
        op, = findall(r'\d+(\*|\+)\d+', client_data)
    except Exception as e:
        print("invalid operation, ", e)
        raise ValueError("operand not permitted")

    math_exp = client_data.split(op)
    print("[proto] ", math_exp)
    x, y = math_exp
    print(x, y, op)
    op_code = OP_char_to_code[op]

    return struct.pack("!iiB", int(x), int(y), op_code)



def srv_to_lb(encoded_client_data:bytes, srv_id:int) -> bytes:
    # prepare packet on server for LB
    x, y, op = struct.unpack("!iiB", encoded_client_data)
    result = OP_code_to_operation[op](x, y)
    return struct.pack("!qB", result, srv_id)


if __name__ == "__main__":
    encodedbla = udp_to_proto("5*9")
    print(encodedbla)
    result = srv_to_lb(encodedbla)
    finresult, = struct.unpack("!q", result)
    print(getsizeof(finresult))