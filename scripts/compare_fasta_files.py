#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 29 12:38:33 2020

@author: usingh

This script takes n fasta files as input and check whether all sequences are same in all files
This script is quick and not memory efficient; written to test small fasta files.
Example:
python compare_fasta_files.py file1.fa file2.fa file3.fa
"""
import sys
import pyfastx
import collections


infiles=[]
inseqs=[]
i=0
failed=False
for f in sys.argv[1:]:
    inseqs.append([])
    seqs=pyfastx.Fastx(f)
    for name, seq, *rest in seqs:
        inseqs[i].append(seq)
    i+=1

#compare length
length0 = len(inseqs[0])
print('Total seqs:',length0)
if any(len(seqs) != length0 for seqs in inseqs):
    failed=True
    print('Lens failed')
    sys.exit(1)
    
#check sequences
#for seqs in inseqs:
seq0=collections.Counter(inseqs[0])
if all(collections.Counter(seqs) == seq0 for seqs in inseqs):
    print('Passed. Seqs are same...')
    sys.exit(0)
else:
    print('Failed. Seqs are different')
    sys.exit(2)
