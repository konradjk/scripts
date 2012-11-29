#!/usr/bin/env python

## LiftOver from hg18 (or b36) to hg19
## Konrad J. Karczewski

from collections import defaultdict
import commands
import os
import gzip
import urllib2
from StringIO import StringIO

def parse_command_line_args():
  try:
    import argparse
    parser = argparse.ArgumentParser(description='Liftover VCF file from b36 or hg18 to hg19', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-i', '--input_vcf', help='Input VCF (can be gzipped)', required=True)
    parser.add_argument('-l', '--liftover_binary', help='LiftOver binary')
    parser.add_argument('-c', '--chain_file', help='LiftOver chain file')
    parser.add_argument('-o', '--output_vcf', help='Output VCF file (can be gzipped)')
    
    args = parser.parse_args()
  except ImportError:
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option('-i', '--input_vcf', help='Input VCF (can be gzipped)')
    parser.add_option('-l', '--liftover_binary', help='LiftOver binary')
    parser.add_option('-c', '--chain_file', help='LiftOver chain file')
    parser.add_option('-o', '--output_vcf', help='Output VCF file (can be gzipped)')
    
    (args, options) = parser.parse_args()
  
  if args.liftover_binary is None:
    args.liftover_binary = "./liftOver"
    file = "http://hgdownload.cse.ucsc.edu/admin/exe/linux.x86_64/liftOver" if ''.join(os.uname()).find('Linux') > -1 else "http://hgdownload.cse.ucsc.edu/admin/exe/macOSX.i386/liftOver"
    f = urllib2.urlopen(file)
    g = open(args.liftover_binary, 'w')
    g.write(f.read())
    g.close()
    os.chmod(args.liftover_binary, 755)
  
  if args.chain_file is None:
    args.chain_file = 'hg18_to_hg19.chain'
    f = urllib2.urlopen("http://hgdownload.cse.ucsc.edu/goldenPath/hg18/liftOver/hg18ToHg19.over.chain.gz")
    b = StringIO(f.read())
    g = open(args.chain_file, 'w')
    g.write(gzip.GzipFile(fileobj=b).read())
    g.close()
    
  if args.output_vcf is None:
    args.output_vcf = os.path.splitext(args.input_vcf)[0] + '_hg19.vcf'
  return args

def read_original_vcf():
  original_variants = defaultdict(dict)
  f = gzip.open(args.input_vcf) if args.input_vcf.endswith('.gz') else open(args.input_vcf)
  g = open('hg18.bed','w')
  header = ''
  for line in f:                            
    if line.find('#') > -1:
      header += line
    else:
      fields = line.strip().split()
      chrom = fields[0] if fields[0].startswith('chr') else 'chr' + fields[0]
      pos = int(fields[1])
      original_variants[chrom][pos] = fields
      g.write("\t".join(map(str, [chrom, pos - 1, pos, chrom, pos])) + '\n')
  f.close()
  g.close()
  return (header, original_variants)

def read_translation_table():
  f = open('hg19.bed')
  variants = defaultdict(dict)
  for line in f:
    fields = line.strip().split()
    variants[fields[0]][int(fields[2])] = fields[3] + '_' + fields[4]
  f.close()
  return variants

if __name__ == '__main__':
  args = parse_command_line_args()
  
  print "Reading original VCF..."
  header, original_variants = read_original_vcf()
  
  print "Lifting over..."
  commands.getstatusoutput("%s hg18.bed %s hg19.bed unmapped" % (args.liftover_binary, args.chain_file))
  
  print "Reading translation table..."
  variants = read_translation_table()
  
  chroms = ['chr%s' % x for x in range(1,23)]
  chroms.extend(['chrX', 'chrY', 'chrM'])
  
  print "Writing final VCF..."
  g = gzip.open(args.output_vcf, 'w') if args.output_vcf.endswith('.gz') else open(args.output_vcf, 'w')
  g.write(header)
  for chrom in chroms:
    order = sorted(variants[chrom].keys())
    for pos in order:
      orig_chrom, orig_pos = variants[chrom][pos].split('_')
      fields = original_variants[orig_chrom][int(orig_pos)]
      fields[:2] = (chrom, str(pos))
      g.write('\t'.join(fields) + '\n')
  g.close()
  
  print "Cleaning up..."
  os.remove('hg18.bed')
  os.remove('hg19.bed')
  os.remove('unmapped')
  print "Done!"
