from roundrobin import RoundRobin
import threading
import random
import time
macs = ["00:22:22:22:22:22","00:33:33:33:33:33"]
possible_macs = ["00:22:22:22:22:22","00:33:33:33:33:33", "00:00:00:00:00:00", "44:44:44:44:44:44"]
lock = threading.Lock()

def mac_changer(rr:RoundRobin):
    time.sleep(2)
    while True:
        time.sleep(random.randint(2, 4))
        global macs
        with lock:
            macs = [possible_macs[random.randint(0,len(possible_macs)-1)] for i in range(3)] 
            print("mac list changed, new list: ", macs)
            rr.update(macs)


# def cycler():
#     while True:
#         time.sleep(1)
#         print(*rr.cycle(macs))

if __name__ == "__main__":

    # for i in range(10):
    #     print(next(rr))

    rr = RoundRobin(macs)
    print("original: ", macs)

    threading.Thread(target=mac_changer, args=(rr,)).start()

    while True:
        time.sleep(1)
        with lock:
            print(next(rr))



