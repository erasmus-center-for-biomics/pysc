import sys
import os
import os.path
import gzip
from pysc import Table


def filter_mixcr(args):
    """."""
    instream = sys.stdout
    if args.input != "stdin":
        if args.input.endswith(".gz"):
            instream = gzip.open(args.input, "rt")
        else:
            instream = open(args.input, "rt")

    outstream = sys.stdout
    if args.output != "stdout":
        if args.output.endswith(".gz"):
            outstream = gzip.open(args.output, "wt")
        else:
            outstream = open(args.output, "wt")

    table = Table(instream)
    outstream.write("{0}\n".format("\t".join(table.header)))
    for row in table:

        if float(row[6]) < args.min_reads:
            continue
        if float(row[2]) < args.min_total:
            continue
        if float(row[3]) < args.min_type:
            continue
        if float(row[4]) < args.min_max:
            continue
        outstream.write("{0}\n".format("\t".join(row)))

    if instream is not sys.stdin:
        instream.close()
    if outstream is not sys.stdout:
        outstream.close()