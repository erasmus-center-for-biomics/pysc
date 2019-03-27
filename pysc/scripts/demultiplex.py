import sys
import gzip
from pysc import read_well_list
from pysc.demultiplex import SRDemultiplexer, PEDemultiplexer


def demultiplex(args):
    """Demultiplex the data."""
    if args.read2:
        if args.read1.endswith(".gz"):
            streama = gzip.open(args.read1, "rt")
        else:
            streama = open(args.read1, "rt")

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
    else:
        with open(args.welllist, "rt") as stream:
            wells = read_well_list(stream)

        if args.read1.endswith(".gz"):
            instream = gzip.open(args.read1, "rt")
        else:
            instream = open(args.read1, "rt")

        # run the single read demultiplexing
        demultiplexer = SRDemultiplexer()
        demultiplexer.expected = wells
        demultiplexer.wbc_start = args.wbc_start
        demultiplexer.wbc_end = args.wbc_end
        demultiplexer.data_start = args.data_start
        demultiplexer.read_fname = args.output_read_1
        demultiplexer.batchsize = args.nitems

        # demultiplex the data
        print(demultiplexer.option_report())
        demultiplexer.process(instream)
