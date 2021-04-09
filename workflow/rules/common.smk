#!/usr/bin/env python3

import os
import subprocess
import pandas as pd

if clusterMode == "gcp" or useRemoteFiles:
    from snakemake.remote.GS import RemoteProvider as GSRemoteProvider
    GS = GSRemoteProvider()

# The pipeline will terminate with an error without .bai files
# The assumption is enforced in input to DV, HC and Strelka2 calling rules
def get_samples(samplesFile):
    with open(samplesFile) as f:
        bamList = [line.rstrip() for line in f]
    return(bamList)

    
def get_sm_tag(bam): 
    if Path(bam).is_file():
        command = 'samtools view -H ' + bam + ' | grep "^@RG" | grep -Eo "SM[^[:space:]]+" | cut -d":" -f2 | uniq'
        sm = subprocess.check_output(command, shell=True).decode('ascii').rstrip()
        return sm

def get_bam(wildcards):
    bam = wildcards.sample + ".bam"
    return(bam)  

def get_bam_index(wildcards):
    bam = sample2bam[wildcards.sample]
    return(bam + '.bai')    

def path_sanitize(path):
    if path.startswith( 'gs://' ):
        gs_path = path.replace("gs://", "")
        return GS.remote(gs_path, keep_local=True)
    else:
        return path  

def get_DBImport_path1(wildcards):
    return(glob.glob('HaplotypeCaller/DBImport/' +  wildcards.chrom + '/' + wildcards.chrom + '*/genomicsdb_meta_dir/genomicsdb_meta*.json'))

def get_DBImport_path2(wildcards):
    path = ''.join(glob.glob('HaplotypeCaller/DBImport/' + wildcards.chrom + '/*/__*/'))
    myList = []
    if os.path.exists(path):
        myList = ['AD.tdb', 'AD_var.tdb', 'ALT.tdb', 'ALT_var.tdb', 'BaseQRankSum.tdb', '__book_keeping.tdb.gz', '__coords.tdb', 'DP_FORMAT.tdb', 'DP.tdb', 'DS.tdb', 'END.tdb', 'ExcessHet.tdb', 'FILTER.tdb', 'FILTER_var.tdb', 'GQ.tdb', 'GT.tdb', 'GT_var.tdb', 'ID.tdb', 'ID_var.tdb', 'InbreedingCoeff.tdb', 'MIN_DP.tdb', 'MLEAC.tdb', 'MLEAC_var.tdb', 'MLEAF.tdb', 'MLEAF_var.tdb', 'MQRankSum.tdb', 'PGT.tdb', 'PGT_var.tdb', 'PID.tdb', 'PID_var.tdb', 'PL.tdb', 'PL_var.tdb', 'QUAL.tdb', 'RAW_MQandDP.tdb', 'ReadPosRankSum.tdb', 'REF.tdb', 'REF_var.tdb', 'SB.tdb', '__tiledb_fragment.tdb']
        myList = [path + file for file in myList]
    return(myList)


# read in chromosome list from reference dict file (assumes the dict is already created)
# this circumvents the issue of whether to use hg19-style or b37-style chromosome annotation
# as it just pulls the chromosome names directly from the dict index.    
def get_chrom_names(dictionaryFile, bedFile):
    chromList = []
    with open(dictionaryFile) as f:
        next(f)
        for line in f:
            f1 = line.split("\t")[1]
            f2 = f1.split(":")[1]
            # if hc_mode and not subprocess.call(['grep', '-q', '^' + f2 + ':', intervalFile]): # exclude chroms not in the regions of interest, otherwise creates an empty interval file which GATK doesn't like
            # chromList.append(f2)
            if not subprocess.call(['grep', '-q', '^' + f2 + '\\s', bedFile]):
                chromList.append(f2)
    return(chromList)   
