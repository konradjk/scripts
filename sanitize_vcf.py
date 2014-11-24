#!/usr/bin/env python
"""
Sanitize a VCF file (remove lines where number of fields is not equal to number of fields in header line).

Konrad J. Karczewski
"""

import os
import sys
import gzip


def parse_command_line_args():
    try:
        import argparse
        parser = argparse.ArgumentParser(description='Sanitize a VCF File', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        parser.add_argument('-i', '--input_vcf', help='Input VCF (can be gzipped)', required=True)
        parser.add_argument('-o', '--output_vcf', help='Output VCF file (can be gzipped)')

        args = parser.parse_args()
    except ImportError:
        from optparse import OptionParser
        parser = OptionParser()
        parser.add_option('-i', '--input_vcf', help='Input VCF (can be gzipped)')
        parser.add_option('-o', '--output_vcf', help='Output VCF file (can be gzipped)')

        (args, options) = parser.parse_args()

        if args.input_vcf is None:
            print >> sys.stderr, "Error: Did not supply input file"
            sys.exit(1)

    if args.output_vcf is None:
        args.output_vcf = os.path.splitext(args.input_vcf)[0] + '_clean.vcf'
    return args

if __name__ == '__main__':
    args = parse_command_line_args()

    f = gzip.open(args.input_vcf) if args.input_vcf.endswith('.gz') else open(args.input_vcf)
    g = gzip.open(args.output_vcf, 'w') if args.output_vcf.endswith('.gz') else open(args.output_vcf, 'w')
    bad_lines = 0
    good_lines = 0
    for line in f:
        if line.find('##') > -1:
            g.write(line)
        elif line.find('#') > -1:
            header_length = len(line.strip().split())
            print >> sys.stderr, 'Header is %s entries' % header_length
            g.write(line)
        else:
            fields = line.strip().split()
            if len(fields) == header_length: #and sum([x for x in fields[9:] if x.find(':') > -1]) + 9 == header_length:
                g.write(line)
                good_lines += 1
            else:
                bad_lines += 1
    f.close()
    g.close()

    print >> sys.stderr, 'Kept %s records (removed %s bad records)' % (good_lines, bad_lines)

