
class Table:

    def __init__(self, stream):
        self.stream = stream
        for line in self.stream:
            line = line.rstrip("\n")
            self.header = line.split("\t")
            break

    def __iter__(self):
        for line in self.stream:
            line = line.rstrip("\n")
            yield line.split("\t")
