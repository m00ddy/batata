class RoundRobin:
    def __init__(self, addrs):
        self.addrs = addrs
        self.idx = 0
    
    def __iter__(self):
        return self
    
    def __next__(self):
        addr = self.addrs[self.idx]
        self.idx = (self.idx+1) % len(self.addrs)
        return addr

if __name__ == "__main__":
    macs = ["00:22:22:22:22:22","00:33:33:33:33:33"]
    rr = RoundRobin(macs)

    for i in range(10):
        print(next(rr))