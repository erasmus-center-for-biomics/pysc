import sys
import os
import os.path
import gzip
from pysc import Table


def assemble_mixcr(args):
    """Assemble MIXCR reports."""
    outstream = sys.stdout
    if args.output != "stdout":
        if args.output.endswith(".gz"):
            outstream = gzip.open(args.output, "wt")
        else:
            outstream = open(args.output, "wt")

    # process the reports
    for pidx, path in enumerate(args.reports):

        # check if the file is present
        if not os.path.exists(path):
            sys.stderr.write("Error: could not find file {0}\n".format(path))
            continue

        # get the data from the file
        stream = open(path, "rt")
        table = Table(stream)
        data = [row for row in table]
        stream.close()

        # just concatenate the files and skip all the processing steps
        if args.no_processing:
            if pidx == 0:
                outstream.write("{0}\n".format("\t".join(table.header)))
            for row in data:
                outstream.write("{0}\n".format("\t".join(row)))
            continue

        # add the file name
        fname = os.path.basename(path)
        types = []
        for row in data:
            ctype = row[5][:3]
            cscore = float(row[1])
            types.append((ctype, cscore))

        # get the total and maximum per type
        totaltype = {}
        maxtype = {}
        for tpl in types:
            if tpl[0] not in totaltype.keys():
                totaltype[tpl[0]] = 0.0
            totaltype[tpl[0]] += tpl[1]

            if tpl[0] not in maxtype.keys():
                maxtype[tpl[0]] = 0.0
            if tpl[1] > maxtype[tpl[0]]:
                maxtype[tpl[0]] = tpl[1]
        total = sum(tpl[1] for tpl in types)

        # write the header for the first file
        if pidx == 0:
            fields = [
                "file name",
                "type",
                "fraction of total",
                "fraction of type",
                "fraction of maximum of type"]
            fields.extend(table.header)
            outstream.write("{0}\n".format("\t".join(fields)))

        # write the content
        for idx, (ctype, score) in enumerate(types):
            line = "{file}\t{type}\t{ftotal}\t{ftype}\t{fmax}\t{row}\n".format(
                file=fname,
                type=ctype,
                ftotal=score/total,
                ftype=score/totaltype[ctype],
                fmax=score/maxtype[ctype],
                row="\t".join(data[idx]))
            outstream.write(line)

    # close the output file
    if outstream is not sys.stdout:
        outstream.close()