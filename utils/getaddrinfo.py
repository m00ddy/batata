import socket

def resolve(hostname, port, type):
    ADDR = None
    try:
        addr_list, = socket.getaddrinfo(hostname, port, type=type)
        *_, ADDR = addr_list
    except Exception as e:
        print(e)
    finally:
        print(f"[DNS] resolved {hostname}:{port} to {ADDR}")

    return ADDR