#!/bin/bash

# Usage: ./prepend_INFO_labels.sh <vcf_without_headers> <vcf_header_file> <caller_label>
#
# Takes a VCF, uncompressed and split into vars and header files,
# and returns, uncompressed:
#   1. a variant file where all input fields (;-delimited)
#   and format fields (:-delimited) are prepended with the caller
#   label (e.g. AF=123; becomes HC_AF=123;), and
#   2. a header file where the info and format fields are
#   updated to match, with prepended caller labels (e.g.
#   INFO=<ID=HC_AF>).
# Note that the GT field is duplicated.  The first entry is left
# as "GT"; the second is prepended with the caller label ("HC_GT").
# This allows bcftools merge to function as intended.


set -euo pipefail

inFile=$1
caller=$2
chrom=$3
threads=$4
mergedOutFileVCF=$5


inFileName="${inFile##*/}"

# header
bcftools view --threads ${threads} -I -h ${inFile} -Ov | sed "s/##INFO=<ID=/##INFO=<ID=${caller}_/" | sed "s/##FORMAT=<ID=/##FORMAT=<ID=${caller}_/" | sed "/##FORMAT=<ID=${caller}_GT/ i\##FORMAT=<ID=GT,Number=1,Type=String,Description=\"Concordant Genotype\">\n##INFO=<ID=${caller}_QUAL,Number=1,Type=String,Description=\"Record of original QUAL value\">" > header.vcf

#info field
bcftools view --threads ${threads} -I -H ${inFile} -r ${chrom} -Ov | cut -f8 | awk -v var="${caller}" 'BEGIN{FS=OFS=";"} {for(i=1;i<=NF;i++) $i=var"_"$i; print $0}' > "info.${inFileName}.temp"

#format field
bcftools view --threads ${threads} -I -H ${inFile} -r ${chrom} -Ov | cut -f9  | awk -v var="${caller}" 'BEGIN{FS=OFS=":"} {for(i=1;i<=NF;i++) $i=var"_"$i; print "GT:"$0}' > "format.${inFileName}.temp"

#left of the info and format fields
bcftools view --threads ${threads} -I -H ${inFile} -r ${chrom} -Ov | cut -f1-7  > "left.${inFileName}.temp"

#right of the info and format fields
bcftools view --threads ${threads} -I -H ${inFile} -r ${chrom} -Ov | cut -f10- | awk 'BEGIN{FS=OFS="\t"} {for(i=1;i<=NF;i++) {split($i,a,":"); $i=a[1]":"$i} print $0}' > "right.${inFileName}.temp"

# need to duplicate GT and preserve one as plain "GT" to allow bcftools merge to work as expected
# combine back to a chromosome vcf
# stream the data as much as possible to avoid having to write to disk
cat <(cat header.vcf) <(paste "left.${inFileName}.temp" "info.${inFileName}.temp" "format.${inFileName}.temp" "right.${inFileName}.temp" | awk -v var="${caller}" 'BEGIN{FS=OFS="\t"} {$8 = $8";"var"_QUAL="$6; print $0}') | bgzip -c >${mergedOutFileVCF}

tabix -p vcf ${mergedOutFileVCF}


rm "left.${inFileName}.temp" "info.${inFileName}.temp" "format.${inFileName}.temp" "right.${inFileName}.temp"



# test : add copying qual into INFO field as caller_qual=

# streaming 2 commands to one file
# cat <(command1) <(command2) > outputfile
