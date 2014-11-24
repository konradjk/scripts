#!/usr/bin/env python

import sys
import csv
import argparse
import gzip
csv.field_size_limit(sys.maxsize)


def main(args):
    table_name = args.input if args.table is None else args.table

    info = dict()
    my_open = gzip.open if args.input.endswith('.gz') else open
    delim = ',' if args.input.rstrip('.gz').endswith('.csv') else '\t'

    reader = csv.reader(my_open(args.input), delimiter=delim)
    header = reader.next()

    for column in header:
        info[column] = {
            "type": 'INT',
            "maxlength": 0,
            "values": set()
        }

    for row in reader:
        for i, value in enumerate(row):
            # Check if field is larger than max length
            if len(value) > info[header[i]]['maxlength']:
                info[header[i]]['maxlength'] = len(value)

            # If only a few values, consider an enum
            if 'values' in info[header[i]]:
                info[header[i]]['values'].add(value)
                if len(info[header[i]]['values']) > 4:
                    del info[header[i]]['values']

            try:
                # Default is integer
                a = int(float(value))
                # Make sure it's not a float
                if a != float(value):
                    info[header[i]]['type'] = 'FLOAT'
            except ValueError:
                # Otherwise, a varchar
                if info[header[i]]['type'] != 'TEXT':
                    info[header[i]]['type'] = 'VARCHAR'

                # If too long, make text
                if len(value) > 255:
                    info[header[i]]['type'] = 'TEXT'

    field_names = []
    colnames = []
    for i, column in enumerate(header):
        col_type = info[column]['type']
        col_meta = '(%s)' % info[column]['maxlength'] if col_type != 'FLOAT' else ''
        if args.enum and 'values' in info[header[i]]:
            col_type = 'ENUM'
            col_meta = "('%s')" % "', '".join(info[header[i]]['values'])
            if info[header[i]]['values'] - set(['TRUE', 'FALSE']):
                col_type = 'BOOLEAN'
                col_meta = ''

        colname = column[:64].lower().replace(' ', '_').replace('(', '').replace(')', '').replace('/', '_').replace('-', '_').replace('>', 'gt').replace('<', 'lt').replace('#', 'no').replace('%', 'perc')
        if colname == '':
            colname = 'none'
        if colname in colnames:
            # If column already exists, need new one
            version = 1
            while '%s_%s' % (colname, version) not in colnames:
                version += 1
            colname = '%s_%s' % (colname, version)
        colnames.append(colname)
        field_names.append("`%s` %s%s DEFAULT NULL" % (colname, col_type, col_meta))

    print "CREATE TABLE `%s` (\n %s\n) ENGINE=MyISAM DEFAULT CHARSET=latin1;" % (table_name, ",\n ".join(field_names))

if __name__ == '__main__':
    INFO = """Generates MySQL create statement from file (tsv or csv) using header as column names. Inspired by Nick Tatonetti's tableize"""
    parser = argparse.ArgumentParser(description=INFO)

    parser.add_argument('input', help='Input file; may be gzipped')
    parser.add_argument('--table', '-t', help='Table name (default: <input>)')
    parser.add_argument('--enum', help='Use enums where possible', action='store_true')
    args = parser.parse_args()
    main(args)