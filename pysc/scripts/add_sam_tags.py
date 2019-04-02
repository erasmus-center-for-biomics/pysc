import sys
import os
import os.path
import gzip
import pyngs.sam as sam
from pysc import read_well_list


class Annotate:

    def __init__(self, expected):
        self.expected = expected
        self.wbcidx = 7
        self.umiidx = -1

    def add_tags(self, instream, outstream):
        """."""
        reader = sam.Reader(instream)
        writer = sam.Writer(outstream, reader.header)
        for alignment in reader:

            # get the well barcode
            fields = alignment.name.split(":")
            wbc = fields[self.wbcidx].replace("wbc=", "", 1)

            # add the well barcode
            tags = [("bc", "Z", wbc)]

            # add the UMI if specified
            if self.umiidx >= 0:
                umi = fields[self.umiidx].replace("umi=", "", 1)
                tags.append(("um", "Z", umi))

            # get the well list information
            if wbc in self.expected.keys():
                anno = self.expected[wbc]
                tags.extend([
                    ("sm", "Z", anno["sample"]),
                    ("rw", "Z", anno["row"]),
                    ("cl", "Z", anno["column"])])
            else:
                tags.extend([
                    ("sm", "Z", "unassigned"),
                    ("rw", "Z", "-1"),
                    ("cl", "Z", "-1")])
            # add the tags to the
            alignment.tags.extend(tags)
            writer.write(alignment)


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

    # Annotate the alignments
    annotater = Annotate(wells)
    annotater.wbcidx = args.barcode_field
    annotater.umiidx = args.umi_field
    annotater.add_tags(instream, outstream)

    # close the input files
    if instream is not sys.stdin:
        instream.close()
    if outstream is not sys.stdout:
        outstream.close()
