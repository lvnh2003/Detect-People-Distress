class Train:
    def __init__(self, name, start, end):
        self.name = name
        self.start = start
        self.end = end
    def __repr__(self):
        return "Time: {} ~ {}".format(self.start ,self.end)

