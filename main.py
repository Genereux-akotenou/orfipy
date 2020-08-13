import time
import pyximport; pyximport.install()
import orfipy_core as oc
import sys
from pyfaidx import Fasta
import multiprocessing
import math


out_bedfile=""
out_fastafile=""

def worker(seqlist,q):
    """
    start worker
    """
    #for each fasta find orf
    for k in seqlist:
        thisname=k[0]
        thisseq=k[1]
        thisseq_rc=k[2]

        #call orf function
        
        #res=oc.find_orfs(thisseq,thisseq_rc,thisname)
        res=oc.find_orfs2(thisseq,thisseq_rc,thisname,minlen=0)
        #q.put(res)



def listener(q):
    '''listens for messages on the q, writes to file. '''
    with open('sampout', 'w') as f:
        while 1:
            m = q.get()
            if m == 'kill':
                #f.write('killed')
                break
            f.write(str(m) + '\n')
            f.flush()


def list_chunks(inlist, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(inlist), n):
        yield inlist[i:i + n]

def result_to_bed(result,fastaob,minlen=30):
    bed_result=[]
    seq_result=[]
    for key, value in result.items():
        seq=fastaob[key][:].seq
        seq_rc=fastaob[key][:].reverse.complement.seq

        chrstart='0'
        chrend=str(len(seq)-1)
        totalorfs=0
        #value is a tuple with three lists
        for i in range(len(value)):
            for orf in value[i]:
                frame=str(i+1)
                if i>=3:
                    frame=str(3-(i+1)) #frames -1,-2,-3
                orfstart=orf[0]
                orfend=orf[1]
                #determine strand
                strand='+'
                #fwd strand seq
                thisseq=seq[orfstart:orfend+1]

                #if negative strand
                if orfstart >= orfend:
                    thisseq=seq_rc[(len(seq)-orfstart):(len(seq)-orfend+1)]
                    #swap start and end
                    temp=orfstart
                    orfstart=orfend
                    orfend=temp
                    strand='-'

                #filter by len
                if len(thisseq)<minlen:
                    continue

                totalorfs+=1
                id='ID='+key+'.'+str(totalorfs)+';ORF len:'+str(len(thisseq))+';ORF frame:'+frame
                score='0'

                thisorf='\t'.join([key,chrstart,chrend,id,score,strand,str(orfstart),str(orfend)])
                bed_result.append(thisorf)

                ##get seq
                thisname='>'+key+'.'+str(totalorfs)+' '+str(orfstart)+'-'+str(orfend)+'('+strand+')'+' len:'+str(len(thisseq))+' ORF frame:'+frame
                seq_result.append(str(thisname)+'\n'+str(thisseq))
                if not thisseq:
                    print ("EROOORRRRRRRRRRRRRRRRRRR")

    return ('\n'.join(bed_result),'\n'.join(seq_result))

def result_to_seq(result,fastaob,minlen=30):
    seq_result=[]
    for key, value in result.items():
        seq=fastaob[key][:]
        #value is a tuple with three lists
        for i in range(len(value)):
            for orf in value[i]:
                thisname='>'+key+str(orf[0])+'-'+str(orf[1])
                #seq_result.append(thisname)
                thisseq=seq[orf[0]:orf[1]+3]
                if len(thisseq)>=minlen:
                    seq_result.append(str(thisname)+'\n'+str(thisseq))
                if not thisseq:
                    print ("EROOORRRRRRRRRRRRRRRRRRR")

    print(seq_result)
    return '\n'.join(seq_result)

def main():
    start = time.time()
    threads=int(sys.argv[2])+2
    infasta=sys.argv[1]
    seqs = Fasta(infasta)
    duration = time.time() - start
    #print('Readting time',duration)
    totalseqs=len(seqs.keys())
    seqperthread=math.ceil((totalseqs/threads))
    splitlist= list(list_chunks(list(seqs.keys()),seqperthread))
    #print('totalseq',totalseqs,'spt',seqperthread,'lst len',len(splitlist))
    #for i in list_chunks(list(seqs.keys()),threads):
    #    splitlist.append(i)
    #print('splitt',splitlist)

    #split keys
    #jobs = []
    #for i in range(len(splitlist)):
    #    thisseqlist=[]
    #    for k in splitlist[i]:
    #        thisname=seqs[k].name
    #        thisseq=seqs[k][:].seq
    #        thisseq_rc=seqs[k][:].complement.reverse.seq
    #        thisseqlist.append((thisname,thisseq,thisseq_rc))
    #    p = multiprocessing.Process(target=worker, args=(thisseqlist,))
    #    jobs.append(p)
    #    p.start()

    #must use Manager queue here, or will not work
    manager = multiprocessing.Manager()
    q = manager.Queue()
    pool = multiprocessing.Pool(threads)

    #put listener to work first
    watcher = pool.apply_async(listener, (q,))
    #fire off workers
    jobs = []
    for i in range(len(splitlist)):
        thisseqlist=[]
        for k in splitlist[i]:
            thisname=seqs[k].name
            thisseq=seqs[k][:].seq
            thisseq_rc=seqs[k][:].complement.reverse.seq
            thisseqlist.append((thisname,thisseq,thisseq_rc))
        job = pool.apply_async(worker, (thisseqlist, q))
        jobs.append(job)

    # collect results from the workers through the pool result queue
    for job in jobs:
        job.get()

    #now we are done, kill the listener
    q.put('kill')
    pool.close()
    pool.join()

    #print('wait join')
    #for proc in jobs:
    #    proc.join()
    #print('done join')
    duration = time.time() - start
    print('d0',duration)
    #print ('result',result)
    #fres=result_to_bed(result,seqs)
    #print (fres[0])
    #print (fres[1])
    #print(result_to_seq(result,seqs))
    duration = time.time() - start
    print('d1',duration)

    #write to file
    #bedfile=infasta.split('.')[0]+'.orfs.bed'
    #orfsfile=infasta.split('.')[0]+'.orfs.fasta'
    #open(bedfile,'w').write(fres[0])
    #open(orfsfile,'w').write(fres[1])

    duration = time.time() - start
    print(duration)


if __name__ == '__main__':
    main()
