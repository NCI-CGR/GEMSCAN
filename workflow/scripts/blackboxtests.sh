#!/bin/bash

# script a run of the snakemake workflow here, then do some diffs to compare output at various steps to "accepted" output

DATE=$(date +"%Y%m%d%H%M")
myExecPath="/DCEG/Projects/CoherentLogic/germline/germlineCallingV4_test/germlineCallingV4"
# myInPath="/DCEG/CGF/Bioinformatics/Production/Bari/germlineCallingV4/tests/data/"
myOutPath="${myExecPath}/tests/out_${DATE}"
myTempPath="/scratch/bballew/${DATE}"

MODES=("DV_HC_Har" "DV_HC" "DV" "HC" "DV_by_chrom")

# create config and directories for five different run modes
for i in "${MODES[@]}"
do

    outPath="${myOutPath}_${i}/"
    tempPath="${myTempPath}_${i}"

    if [ ! -d "$outPath" ]; then
        mkdir -p "$outPath" || die "mkdir ${outPath} failed"
    else
        echo "${outPath} already exists!"
    fi

    # generate a test config:
    echo "maxJobs: 100" > ${outPath}/TESTconfig.yaml
    echo "inputDir: '${myExecPath}/tests/data/'" >> ${outPath}/TESTconfig.yaml
    echo "outputDir: '${outPath}'" >> ${outPath}/TESTconfig.yaml
    echo "logDir: '${outPath}/logs/'" >> ${outPath}/TESTconfig.yaml
    echo "tempDir: '${tempPath}'" >> ${outPath}/TESTconfig.yaml
    echo "bedFile: '${myExecPath}/tests/regions/seqcap_EZ_Exome_v3_v3utr_intersect_correct_NOchr4.bed'" >> ${outPath}/TESTconfig.yaml
    echo "clusterMode: 'qsub -q long.q -V -j y -o ${outPath}/logs/'" >> ${outPath}/TESTconfig.yaml
    echo "snakePath: '${myExecPath}/scripts/'" >> ${outPath}/TESTconfig.yaml
    echo "gatkPath: '/DCEG/Projects/Exome/SequencingData/GATK_binaries/gatk-4.0.11.0/'" >> ${outPath}/TESTconfig.yaml
    echo "refGenome: '/DCEG/CGF/Bioinformatics/Production/Bari/refGenomes/hg19_canonical_correct_chr_order.fa'" >> ${outPath}/TESTconfig.yaml
    echo "numShards: 4" >> ${outPath}/TESTconfig.yaml
    echo "modelPath: '/opt/wes/model.ckpt' # either /opt/wgs/model.ckpt or /opt/wes/model.ckpt for WGS or WES, respectively" >> ${outPath}/TESTconfig.yaml
    echo "runMode: " >> ${outPath}/TESTconfig.yaml

done

# DV, HC, and harmonization modules
echo "  haplotypeCaller: TRUE"  >> ${myOutPath}_DV_HC_Har/TESTconfig.yaml
echo "  deepVariant: TRUE"  >> ${myOutPath}_DV_HC_Har/TESTconfig.yaml
echo "  harmonize: TRUE"  >> ${myOutPath}_DV_HC_Har/TESTconfig.yaml
echo "useShards: TRUE" >> ${myOutPath}_DV_HC_Har/TESTconfig.yaml

# DV and HC, no harmonization
echo "  haplotypeCaller: TRUE"  >> ${myOutPath}_DV_HC/TESTconfig.yaml
echo "  deepVariant: TRUE"  >> ${myOutPath}_DV_HC/TESTconfig.yaml
echo "  harmonize: FALSE"  >> ${myOutPath}_DV_HC/TESTconfig.yaml
echo "useShards: TRUE" >> ${myOutPath}_DV_HC/TESTconfig.yaml

# DV only
echo "  haplotypeCaller: FALSE"  >> ${myOutPath}_DV/TESTconfig.yaml
echo "  deepVariant: TRUE"  >> ${myOutPath}_DV/TESTconfig.yaml
echo "  harmonize: FALSE"  >> ${myOutPath}_DV/TESTconfig.yaml
echo "useShards: TRUE" >> ${myOutPath}_DV/TESTconfig.yaml

# HC only
echo "  haplotypeCaller: TRUE"  >> ${myOutPath}_HC/TESTconfig.yaml
echo "  deepVariant: FALSE"  >> ${myOutPath}_HC/TESTconfig.yaml
echo "  harmonize: FALSE"  >> ${myOutPath}_HC/TESTconfig.yaml
echo "useShards: TRUE" >> ${myOutPath}_HC/TESTconfig.yaml

# DV only, parallelize by chromosome (others are by shard)
echo "  haplotypeCaller: FALSE"  >> ${myOutPath}_DV_by_chrom/TESTconfig.yaml
echo "  deepVariant: TRUE"  >> ${myOutPath}_DV_by_chrom/TESTconfig.yaml
echo "  harmonize: FALSE"  >> ${myOutPath}_DV_by_chrom/TESTconfig.yaml
echo "useShards: FALSE" >> ${myOutPath}_DV_by_chrom/TESTconfig.yaml


module load python3/3.6.3 sge
unset module

for i in "${MODES[@]}"
do
    outPath="${myOutPath}_${i}/"
    cmd="qsub -q long.q -V -j y -S /bin/sh -o ${outPath} ${myExecPath}/scripts/submit.sh ${outPath}/TESTconfig.yaml"
    echo "Command run: $cmd"
    eval $cmd
done
