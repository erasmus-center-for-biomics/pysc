import argparse
import sys
import gzip
from operator import attrgetter
from collections import namedtuple
from pyngs.bases import fasta


class MaybeCompressed:
    """A context manager to open files based on the extension."""

    def __init__(self, filename, mode):
        """Initialize the manager."""
        self.filename = filename
        self.mode = mode

    def __enter__(self):
        """Open the file based on the extension."""
        if self.filename == "stdin":
            self.opened = sys.stdin
        elif self.filename == "stdout":
            self.opened = sys.stdout
        elif self.filename == "stderr":
            self.opened = sys.stderr
        elif self.filename.endswith(".gz"):
            self.opened = gzip.open(self.filename, self.mode)
        else:
            self.opened = open(self.filename, self.mode)
        return self.opened

    def __exit__(self, *args):
        """Close the input file."""
        if self.opened is not sys.stdin and \
            self.opened is not sys.stdout and \
                self.opened is not sys.stderr:
            self.opened.close()


def deduplicate(iterable, key=lambda x: x):
    """Deduplicate an iterable."""
    iterable.sort(key=key)
    first = True
    last = None
    last_key = None
    for entry in iterable:
        cur_key = key(entry)
        if not first and cur_key != last_key:
            yield last
            last = entry
            last_key = cur_key
            continue
        elif first:
            first = False
            last = entry
            last_key = cur_key
    if not first:
        yield last


def deduplicate_fasta(args):
    """Deduplicata a fasta file."""
    # get the number of genes per cluster
    with MaybeCompressed(args.fasta, "rt") as stream:
        fbuffer = []
        ftuple = namedtuple("FTUPLE", ["name", "sequence"])
        for name, sequence in fasta(stream, toupper=False, fullnames=True):
            fbuffer.append(ftuple(name, sequence))

    # deduplicate the FastA the fasta
    dbuffer = [ft for ft in deduplicate(fbuffer)]
    with MaybeCompressed(args.output, "wt") as stream:
        for entry in dbuffer:
            stream.write(">{0}\n{1}\n".format(entry.name, entry.sequence))


if __name__ == "__main__":
    sparser = argparse.ArgumentParser(
        prog="cluster counts",
        description=""".""")
    sparser.add_argument(
        "-o", "--output", dest="output",
        type=str, nargs="?", default="stdout",
        help="A deduplicated FastA file.")
    sparser.add_argument(
        "-f", "--fasta", dest="fasta",
        type=str, nargs="?", default="stdin",
        help="A FastA file with the clusters.")

    sparser.set_defaults(func=deduplicate_fasta)

    # parse the arguments
    args = sparser.parse_args()
    args.func(args)