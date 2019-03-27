
class Table:

    def __init__(self, stream):
        self.stream = stream
        self.header = []
        for line in self.stream:
            line = line.rstrip("\n")
            self.header = line.split("\t")
            break

    def __iter__(self):
        for line in self.stream:
            line = line.rstrip("\n")
            yield line.split("\t")


def read_well_list(stream):
    """Read the well-list."""
    retval = {}
    for line in stream:
        line = line.rstrip()
        if line.startswith("Row"):
            continue
        tokens = line.split("\t")
        wbc = tokens[5]
        retval[wbc] = {
            "row": tokens[0],
            "column": tokens[1],
            "sample": tokens[4].replace(" ", "_")}
    return retval