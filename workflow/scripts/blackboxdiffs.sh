#!/bin/bash

stamp=$1
obsBasePath="/DCEG/CGF/Bioinformatics/Production/Bari/Germline_pipeline_v4_dev/germlineCallingV4/tests/out_${stamp}"
expPath="/DCEG/CGF/Bioinformatics/Production/Bari/Germline_pipeline_v4_dev/germlineCallingV4/tests/expected_outputs/"

# skip headers for now.  complicated due to command line provenance (bcftools, gatk, genotype_union - paths, dates change)

MODES=("DV_HC_Har" "DV_HC" "DV" "HC" "DV_by_chrom")

for i in "${MODES[@]}"
do
    obsPath="${obsBasePath}_${i}"


    if [ "$i" != "HC" ]; then
        if diff -q <(grep -v "^##" ${obsPath}/deepVariant/called/gvcfs/NA12878_chr3_100000_1000000_all_chroms.g.vcf) <(grep -v "^##" ${expPath}/deepVariant/called/gvcfs/NA12878_chr3_100000_1000000_all_chroms.g.vcf); then
            echo "PASS: Rule DV_concat_gvcfs (output: ${obsPath}/deepVariant/called/gvcfs/NA12878_chr3_100000_1000000_all_chroms.g.vcf) matches expected output." | tee "${obsPath}/diff_tests.txt"
        else
            echo "ERROR: Rule DV_concat_gvcfs (output: ${obsPath}/deepVariant/called/gvcfs/NA12878_chr3_100000_1000000_all_chroms.g.vcf) does not match expected output.  Check upstream outputs to identify inconsistency." | tee "${obsPath}/diff_tests.txt"
        fi
        if diff -q <(zgrep -v "^##"  ${obsPath}/deepVariant/called/vcfs/NA12878_chr3_100000_1000000_all_chroms.vcf.gz) <(grep -v "^##"  ${expPath}/deepVariant/called/vcfs/NA12878_chr3_100000_1000000_all_chroms.vcf); then
            echo "PASS: Rule DV_concat_vcfs (output: ${obsPath}/deepVariant/called/vcfs/NA12878_chr3_100000_1000000_all_chroms.vcf.gz) matches expected output." | tee -a "${obsPath}/diff_tests.txt"
        else
            echo "ERROR: Rule DV_concat_vcfs (output: ${obsPath}/deepVariant/called/vcfs/NA12878_chr3_100000_1000000_all_chroms.vcf.gz) does not match expected output.  Check upstream outputs to identify inconsistency." | tee -a "${obsPath}/diff_tests.txt"
        fi
        if diff -q <(zgrep -v "^##" ${obsPath}/deepVariant/genotyped/DV_variants.vcf.gz) <(grep -v "^##" ${expPath}/deepVariant/genotyped/DV_variants.vcf); then
            echo "PASS: Rule DV_compress_merged_vcfs (output: ${obsPath}/deepVariant/genotyped/DV_variants.vcf.gz) matches expected output." | tee -a "${obsPath}/diff_tests.txt"
        else
            echo "ERROR: Rule DV_compress_merged_vcfs (output: ${obsPath}/deepVariant/genotyped/DV_variants.vcf.gz) does not match expected output.  Check upstream outputs to identify inconsistency." | tee -a "${obsPath}/diff_tests.txt"
        fi
    fi

    if [[ "$i" != "DV" && "$i" != "DV_by_chrom" ]]; then
        if diff -q <(zgrep -v "^##" ${obsPath}/HaplotypeCaller/called/NA12878_chr3_100000_1000000_all_chroms.g.vcf.gz) <(grep -v "^##" ${expPath}/HaplotypeCaller/called/NA12878_chr3_100000_1000000_all_chroms.g.vcf); then
            echo "PASS: Rule HC_concat_gvcfs (output: ${obsPath}/HaplotypeCaller/called/NA12878_chr3_100000_1000000_all_chroms.g.vcf.gz) matches expected output." | tee -a "${obsPath}/diff_tests.txt"
        else
            echo "ERROR: Rule HC_concat_gvcfs (output: ${obsPath}/HaplotypeCaller/called/NA12878_chr3_100000_1000000_all_chroms.g.vcf.gz) does not match expected output.  Check upstream outputs to identify inconsistency." | tee -a "${obsPath}/diff_tests.txt"
        fi

        if diff -q <(zgrep -v "^##"  ${obsPath}/HaplotypeCaller/genotyped/combined/HC_variants.vcf.gz) <(grep -v "^##" ${expPath}/HaplotypeCaller/genotyped/combined/HC_variants.vcf); then
            echo "PASS: Rule HC_concat_vcfs_bcftools (output: ${obsPath}/HaplotypeCaller/genotyped/combined/HC_variants.vcf.gz) matches expected output." | tee -a "${obsPath}/diff_tests.txt"
        else
            echo "ERROR: Rule HC_concat_vcfs_bcftools (output: ${obsPath}/HaplotypeCaller/genotyped/combined/HC_variants.vcf.gz) does not match expected output.  Check upstream outputs to identify inconsistency." | tee -a "${obsPath}/diff_tests.txt"
        fi
    fi

    if [ "$i" == "DV_HC_Har" ]; then
        if diff -q <(zgrep -v "^##"  ${obsPath}/ensemble/all_callers_merged_genotypes.vcf.gz) <(grep -v "^##" ${expPath}/ensemble/all_callers_merged_genotypes.vcf); then
            echo "PASS: Rule merge_by_sample (output: ${obsPath}/ensemble/all_callers_merged_genotypes.vcf.gz) matches expected output." | tee -a "${obsPath}/diff_tests.txt"
        else
            echo "ERROR: Rule merge_by_sample (output: ${obsPath}/ensemble/all_callers_merged_genotypes.vcf.gz) does not match expected output.  Check upstream outputs to identify inconsistency." | tee -a "${obsPath}/diff_tests.txt"
        fi
    fi

done

# if diff -q ${obsPath}/ ${expPath}/; then
#     echo "Rule  (output: ) matches expected output."
# else
#     echo "ERROR: Rule  (output: ) does not match expected output.  Check upstream outputs to identify inconsistency."
# fi

# if diff -q ${obsPath}/ ${expPath}/; then
#     echo "Rule  (output: ) matches expected output."
# else
#     echo "ERROR: Rule  (output: ) does not match expected output.  Check upstream outputs to identify inconsistency."
# fi

# if diff -q ${obsPath}/ ${expPath}/; then
#     echo "Rule  (output: ) matches expected output."
# else
#     echo "ERROR: Rule  (output: ) does not match expected output.  Check upstream outputs to identify inconsistency."
# fi

# if diff -q ${obsPath}/ ${expPath}/; then
#     echo "Rule  (output: ) matches expected output."
# else
#     echo "ERROR: Rule  (output: ) does not match expected output.  Check upstream outputs to identify inconsistency."
# fi



# tree in "expected_outputs":
# .
# ├── deepVariant
# │   ├── called
# │   │   ├── gvcfs
# │   │   │   └── NA12878_chr3_100000_1000000_all_chroms.g.vcf
# │   │   └── vcfs
# │   │       └── NA12878_chr3_100000_1000000_all_chroms.vcf
# │   └── genotyped
# │       └── DV_variants.vcf
# ├── ensemble
# │   ├── all_callers_merged_genotypes.vcf
# │   ├── all_callers.vcf
# │   ├── DV_header.vcf
# │   ├── DV_labeled.vcf
# │   ├── DV_normalized.vcf
# │   ├── DV_vars.vcf
# │   ├── HC_header.vcf
# │   ├── HC_labeled.vcf
# │   ├── HC_normalized.vcf
# │   ├── HC_vars.vcf
# │   ├── prepended.DV_header.vcf
# │   ├── prepended.DV_vars.vcf
# │   ├── prepended.HC_header.vcf
# │   └── prepended.HC_vars.vcf
# └── HaplotypeCaller
#     ├── called
#     │   └── NA12878_chr3_100000_1000000_all_chroms.g.vcf
#     └── genotyped
#         └── combined
#             └── HC_variants.vcf
