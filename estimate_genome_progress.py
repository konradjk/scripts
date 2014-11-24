#!/usr/bin/env python
"""
Takes chromosome:position or "chromosome position" and approximates how far into the genome the position is.
Useful for monitoring progress of files being generated in chromosomal order.

Konrad J. Karczewski
"""

import sys

chroms = [  # GRCh37/hg19
    ["chr1", 249250621],
    ["chr2", 243199373],
    ["chr3", 198022430],
    ["chr4", 191154276],
    ["chr5", 180915260],
    ["chr6", 171115067],
    ["chr7", 159138663],
    ["chr8", 146364022],
    ["chr9", 141213431],
    ["chr10", 135534747],
    ["chr11", 135006516],
    ["chr12", 133851895],
    ["chr13", 115169878],
    ["chr14", 107349540],
    ["chr15", 102531392],
    ["chr16", 90354753],
    ["chr17", 81195210],
    ["chr18", 78077248],
    ["chr19", 59128983],
    ["chr20", 63025520],
    ["chr21", 48129895],
    ["chr22", 51304566],
    ["chrX", 155270560],
    ["chrY", 59373566],
    ["chrM", 16571]
]


def main(args):
    try:
        if len(args) > 2:
            chrom = args[1]
            pos = int(args[2])
        else:
            chrom, pos = args[1].split(':')
            chrom = 'chr%s' % chrom.replace('chr', '').replace('T', '')
            pos = int(pos)
        if chrom not in [x[0] for x in chroms]:
            print 'Chrom not found: %s' % chrom
            sys.exit(1)
        running_total = 0
        for chrom_pos in chroms:
            if chrom == chrom_pos[0]:
                final_position = running_total + pos
            running_total += chrom_pos[1]
        print '%s:%s is %.2f%% through the genome' % (chrom, pos, final_position*100/float(running_total))
    except Exception, e:
        print >> sys.stderr, e
        print >> sys.stderr, 'Must be in format chrom:pos'
        sys.exit(1)

if __name__ == '__main__':
    main(sys.argv)