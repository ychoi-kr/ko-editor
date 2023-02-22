#!/usr/bin/python3

import csv
import shutil
import os
import sys
from pathlib import Path

TSV = sys.argv[1] if (len(sys.argv) == 2 and Path(sys.argv[1]).suffix == '.tsv') else 'rename.tsv'

with open(TSV, 'r') as f:
    for line in csv.reader(f, delimiter='\t'):
        if len(line) != 2:
            continue
        old, new = line[0], line[1]
        print('old:', old, ', new:', new)
        for ext in ['png', 'jpg', 'jpeg']:
            filea = f'{old}.{ext}'
            fileb = f'{new}.{ext}'
            if os.path.isfile(filea):
                shutil.move(filea, fileb)
                break
        else:
            if os.path.exists(old):
                shutil.move(old, new)


