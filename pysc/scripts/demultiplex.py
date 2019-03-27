import sys
import gzip
from pysc.demultiplex import PEDemultiplexer


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


def demultiplex(args):
    """Demultiplex the data."""
    if args.read1.endswith(".gz"):
        streama = gzip.open(args.read1, "rt")
    else:
        streama = open(args.read1, "rt")

    if args.read2:
        if args.read2.endswith(".gz"):
            streamb = gzip.open(args.read2, "rt")
        else:
            streamb = open(args.read1, "rt")

    with open(args.welllist, "rt") as stream:
        wells = read_well_list(stream)

    demultiplexer = PEDemultiplexer()
    demultiplexer.expected = wells
    demultiplexer.wbc_read = args.wbc_read
    demultiplexer.wbc_start = args.wbc_start
    demultiplexer.wbc_end = args.wbc_end
    demultiplexer.data_start = args.data_start
    demultiplexer.reada_fname = args.output_read_1
    demultiplexer.readb_fname = args.output_read_2
    demultiplexer.batchsize = args.nitems

    print(demultiplexer.option_report())
    # demultiplex the data
    demultiplexer.process(streama, streamb)

    # close the input streams
    streama.close()
    streamb.close()