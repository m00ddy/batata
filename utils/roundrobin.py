class RoundRobin:
    def __init__(self, addrs:list):
        self.addrs = addrs
        self.buffer = []
        self.idx = 0
    
    def __iter__(self):
        return self
    
    def __next__(self): 
        # if not self.addrs and not self.buffer:
        #     return
        try:
            addr = self.addrs[self.idx]
        except IndexError:
            addr = self.addrs[0]
        self.idx = (self.idx+1) % len(self.addrs)

        # check if at list's end, update list
        if self.idx == 0 and self.buffer:
            self.addrs = self.buffer
            self.buffer = []

        return addr

    def update(self, new_list:list):
        self.buffer = new_list
        if self.idx == 0:
            self.addrs = self.buffer
        # if init to an empty list, make buffer main list
        if not self.addrs:
            self.addrs = self.buffer


    def cycle(self, new_list):
        saved = []
        for i in new_list:
            yield i
            saved.append(i)
        while saved:
            for i in saved:
                yield i
            if hasattr(new_list, "__iter__") and new_list != saved:
                saved = new_list
