class RoundRobin:
    def __init__(self, addrs:list):
        self.addrs = addrs
        self.buffer = []
        self.idx = 0
    
    def __iter__(self):
        return self
    
    def __next__(self): 
        if not self.addrs:
            return -1
        addr = self.addrs[self.idx]
        self.idx = (self.idx+1) % len(self.addrs)

        # check if at list's end, update list
        if self.idx == 0 and self.buffer:
            self.addrs = self.buffer
            self.buffer = []

        return addr

    def update(self, new_list:list):
        self.buffer = new_list


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
