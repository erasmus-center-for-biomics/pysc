import pyngs.fastq as fq
from itertools import groupby
from operator import itemgetter


class PEDemultiplexer:

    def __init__(self):
        """Initialize a new demultiplexer."""
        self.wbc_read = 2
        self.wbc_start = 0
        self.wbc_end = 12
        self.data_start = 0
        self.batchsize = 1000000

        # the default readname
        self.reada_fname = "{sample}_{wbc}_{row}_{column}_R1.fastq"
        self.readb_fname = "{sample}_{wbc}_{row}_{column}_R2.fastq"

        #
        self.expected = {}
        self.unexpected = {
            "sample": "undetermined",
            "row": "NA",
            "column": "NA"
        }

    def option_report(self):
        return """PEDemultiplexer
well-barcode-read: {wbc_read}
well-barcode-start: {wbc_start}
well-barcode-end: {wbc_end}
data-start: {data_start}

batchsize: {batchsize}

output-read-a: {reada_fname}
output-read-b: {readb_fname}

expected {n} barcodes
        """.format(
            wbc_read=self.wbc_read,
            wbc_start=self.wbc_start,
            wbc_end=self.wbc_end,
            data_start=self.data_start,
            batchsize=self.batchsize,
            reada_fname=self.reada_fname,
            readb_fname=self.readb_fname,
            n=len(self.expected))

    def well_barcode(self, sequence, quality):
        """Get the well barcode and sequence from a read."""
        wbc = sequence[self.wbc_start:self.wbc_end]
        seq = sequence[self.data_start:]
        qual = quality[self.data_start:]
        return wbc, seq, qual

    def process(self, streama, streamb):
        """Demultiplex the data read."""
        # prepare the generators
        fastqa = fq.fastq(streama)
        fastqb = fq.fastq(streamb)
        rbuffer = []

        # traverse the reads
        for ida, seqa, quala in fastqa:
            idb, seqb, qualb = next(fastqb)

            # get the well barcode
            if self.wbc_read == 2:
                wbc, seqb, qualb = self.well_barcode(seqb, qualb)
            else:
                wbc, seqa, quala = self.well_barcode(seqa, quala)

            # add the well barcode to the readnames
            ida = fq.clean_readname(ida)
            idb = fq.clean_readname(idb)
            ida = fq.encode_in_readname(ida, ["wbc={wbc}".format(wbc=wbc)])
            idb = fq.encode_in_readname(idb, ["wbc={wbc}".format(wbc=wbc)])

            # add data to the buffer
            rbuffer.append((
                wbc,
                (ida, seqa, quala),
                (idb, seqb, qualb)))

            if len(rbuffer) >= self.batchsize:
                self.write_batch(rbuffer)
                rbuffer.clear()

    def write_batch(self, batch):
        """Write a batch of reads."""
        batch.sort(key=itemgetter(0))

        # group items by well barcode
        for wbc, group in groupby(batch, key=itemgetter(0)):
            sample = self.unexpected
            if wbc in self.expected.keys():
                sample = self.expected[wbc]

            fnamea = self.reada_fname.format(wbc=wbc, **sample)
            stra = open(fnamea, "at")

            fnameb = self.readb_fname.format(wbc=wbc, **sample)
            strb = open(fnameb, "at")

            # write the reads in the group to the output file
            for item in group:
                assert len(item[1][1]) == len(item[1][2])
                assert len(item[2][1]) == len(item[2][2])

                stra.write(fq.format(item[1][0], item[1][1], item[1][2]))
                strb.write(fq.format(item[2][0], item[2][1], item[2][2]))

            stra.close()
            strb.close()
