import sys
import os
import os.path
import gzip
import pyngs.sam as sam
from pysc import read_well_list


def add_sam_tags(args):
    """Add single cell sam tags."""
    # open the input sam file
    instream = sys.stdin
    if args.input != "stdin":
        if args.input.endswith(".gz"):
            instream = gzip.open(args.input, "rt")
        else:
            instream = open(args.input, "rt")

    # open the output sam file
    outstream = sys.stdout
    if args.output != "stdout":
        if args.output.endswith(".gz"):
            outstream = gzip.open(args.output, "wt")
        else:
            outstream = open(args.output, "wt")

    # get the well-list
    stream = open(args.welllist, "rt")
    wells = read_well_list(stream)
    stream.close()


    # close the input files
    if instream is not sys.stdin:
        instream.close()
    if outstream is not sys.stdout:
        outstream.close()