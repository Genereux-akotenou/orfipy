#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: genereux
"""
import orfipy_core as oc

"""
seq:       ATGTTTATGAAATAGAACTAAATGCCCATG
frame1:    ATG TTT ATG AAA TAG AAC TAA ATG CCC ATG
frame2: x  TGT TTA TGA AAT AGA ACT AAA TGC CCA TG
frame2: xx GTT TAT GAA ATA GAA CTA AAT GCC CAT G

rev_seq:   CATGGGCATTTAGTTCTATTTCATAAACAT
frame1:    CAT GGG CAT TTA GTT CTA TTT CAT AAA CAT
frame2: x  ATG GGC ATT TAG TTC TAT TTC ATA AAC AT
frame2: xx TGG GCA TTT AGT TCT ATT TCA TAA ACA T
"""

seq='ATGTTTATGAAATAGAACTAAATGCCCATGTAG'
seq_rc='CTACATGGGCATTTAGTTCTATTTCATAAACAT'
def test_orf_search():
    result=oc.start_search(seq, #seq
                    seq_rc,     #seq_rc
                    'test',     #seqname
                    0,          #minlen
                    100000,     #maxlen
                    'b',        #strand
                    ['ATG'],    #starts
                    ['TAG'],    #stops
                    '1',        #table
                    True,       #include_stop
                    False,      #partial3
                    False,      #partial5
                    False,      #between_stops
                    True,       #nested
                    [False,False,False,False,False]  #out_opts     
    )
    
    print(result)
    print(result[0])
    print(len(result[0].split('\n')))
    assert len(result[0].split('\n'))==5
    
test_orf_search()