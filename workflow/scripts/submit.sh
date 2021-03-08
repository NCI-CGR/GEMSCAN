#!/bin/bash
#$ -S /bin/sh
#$ -j y

set -euo pipefail

die() {
    echo "ERROR: $* (status $?)" 1>&2
    exit 1
}

configFile=""
if [ $# -eq 0 ]; then
    echo "Please specify config file with full path."
    exit 1
else
    configFile=$1
fi

if [ ! -f "$configFile" ]; then
    echo "Config file not found."
    exit 1
fi

# note that this will only work for simple, single-level yaml
# this also requires a whitespace between the key and value pair in the config (except for the cluster command, which requires single or double quotes)
snakeDir=$(awk '($0~/^snakePath/){print $2}' $configFile | sed "s/['\"]//g")
#logDir=$(awk '($0~/^logDir/){print $2}' $configFile | sed "s/['\"]//g")
outDir=$(awk '($0~/^outputDir/){print $2}' $configFile | sed "s/['\"]//g")
logDir="${outDir}logs/"
maxJobs=$(awk '($0~/^maxJobs/){print $2}' $configFile | sed "s/['\"]//g")
threads=$(awk '($0~/^threads/){print $2}' $configFile | sed "s/['\"]//g")
clusterLine=$(awk '($0~/^clusterMode/){print $0}' $configFile | sed "s/\"/'/g")  # allows single or double quoting of the qsub command in the config file
clusterMode=''$(echo $clusterLine | awk -F\' '($0~/^clusterMode/){print $2}')''

if [[ "$clusterMode" =~ ^qsub ]]; then
    clusterMode="\"$clusterMode -pe by_node ${threads} -o ${logDir} \""
elif  [[ "$clusterMode" =~ ^local ]]; then
    clusterMode="\"$clusterMode\""
elif  [[ "$clusterMode" =~ ^gcp ]]; then
    clusterMode="gcp"
fi


if [ ! -d "$logDir" ]; then
    mkdir -p "$logDir" || die "mkdir ${logDir} failed"
fi

if [ ! -d "$outDir" ]; then
    mkdir -p "$outDir" || die "mkdir ${outDir} failed"
fi

DATE=$(date +"%Y%m%d%H%M%S")
cd $outDir  # snakemake passes $PWD to singularity and binds it as the home directory, and then works relative to that path.
sing_arg='"'$(echo "-B /DCEG:/DCEG")'"'


cmd=""
if [ "$clusterMode" == '"'"local"'"' ]; then
    cmd="conf=$configFile snakemake -p -s ${snakeDir}/Snakefile_germline_snv_calling --use-singularity --singularity-args ${sing_arg} --cores ${threads} --config dt=${DATE} --rerun-incomplete &> ${logDir}/log_${DATE}.out"
elif [ "$clusterMode" = '"'"unlock"'"' ]; then  # put in a convenience unlock
    cmd="conf=$configFile snakemake -p -s ${snakeDir}/Snakefile_germline_snv_calling --unlock"
elif [ "$clusterMode" = '"'"gcp"'"' ]; then  # google genomics pipeline
    cmd="conf=$configFile snakemake --google-lifesciences --default-remote-prefix ${outputDir} -s ${snakeDir}/Snakefile_germline_snv_calling --use-singularity --config dt=${DATE} --google-lifesciences-region us-east-1"
else
    cmd="conf=$configFile snakemake -s ${snakeDir}/Snakefile_germline_snv_calling --use-singularity --singularity-args ${sing_arg} --jobscript ${snakeDir}/jobscript.sh --config dt=${DATE} --rerun-incomplete --cluster ${clusterMode}  --jobs $maxJobs --latency-wait 300 &> ${logDir}/log_${DATE}.out"
    # --nt - keep temp files
fi

source /etc/profile.d/modules.sh;
module load singularity;
echo "Command run: $cmd"
eval $cmd
