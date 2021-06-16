## Pipeline inputs and outputs

#### Input

In the config folder, please edit the samples.txt to list the aligned BAM files, one on each line. 
We also assume that the BAM file index are in the same directory and are with the name ``<bam_filename>.bai``

#### samples.txt

In the config folder, please create the tab delimited samples.txt to list the sample names, aligned BAM files, and their index, one on each line. Please make sure that you include the header  'sampleID	bam	index' as well. 
For example:
```
sampleID	bam	index
sample1 bam1.bam  bam1.bam.bai
sample2 bam2.bam  bam2.bam.bai
```

The pipeline *does* support CRAM file input, please list your CRAM files under the bam column and CRAM indexes under the index column in the samples.txt file.

Note that if the input files are on google storage please also use ``gs://`` as the prefix. The pipeline uses the prefix to determine whether they are remote files.
Also note that while on-prem/local runs can take advantage of remote files, currently it may cause unexpected errors when multiple tasks try to download the same file into the same location. This will be solved in the next release.

### bed file
Currently, the pipeline requires a bed file and a gzipped bed file for both exome, tagetted and WGS. The bedfile needed to be sorted propoerly.
We have included a simple check as the first task when running the pipeline
```
bedops --ec --everything {input.bed} >/dev/null
```
It is better to use the above command to see if you get any error message before running the pipeline.

If you see ```Error executing rule validate_bed_file on cluster``` in your snakemake log file, chances are your bed file did not pass the *bedops* validation. Please check ```logs/validate_bed_file/bedops.log``` to see the error message from *bedops* validation.

#### Config file

Please create the config.yaml file from the config_template.yaml and edit accordingly, please note that you need to:
- provide full path to strelka2_glnexus.yml for glnexus_strelka2_config if strelka2 is used
- outputDir is default to './' if clusterMode is set to 'cluster'. If you are running on GCP, please set to a gs storage bucket accordingly


#### Expected Outputs

Depends on run mode selected in the config, but can include:
Multi-sample VCF called with DeepVariant
Multi-sample VCF called with HaplotypeCaller
##### Multi-sample VCF called with Strelka2
Strelka2 output includes filtered calls (with FILTER IndelConflict, SiteConflict, LowGQX, HighDPFRatio, HighSNVSB, HighDepth, LowDepth). 

##### ensenbled variants
If runMode is set to TURE for streka2, haplotypeCaller, deepVariant and harmonize, you should find a multi-sample VCF file containing the union of the DeepVariant, HaplotypeCaller and Strelka2 calls: all_callers_merged_genotypes.vcf.gz(.tbi). Please note that the FILTER field in this VCF file is set to be one of the following: oneCaller, twoCallers, and threeCallers. Many of the variant evaluation and analysis tools would filter any variant without PASS or . in the FILTER field by default. Please be extra careful with this. 

We also generated the several ensemble genotypes (GT) fields with various degree of confidence to fit different purposes:
- ensembled GT in the final output (GT):
  If all 3 callers have calls: 
     any of the two callers are concordant:  GT is set to that concordant GT; 
none are concordant: GT is set to ./.
If only 2 callers have calls:
they are concordant: GT is set to that concordant GT;
they are not concordant: GT is set to ./.
If only one caller has call, it's set to that GT
- Majority concensus voting (concensus_GT):
If only one caller has call, it's set to ./.
- DV priority voting (dv_priority_GT):
If there is DV call, set to that GT
If there's no DV call:
HC and strelka2 calls the same genotype, GT is set to that genotype
Otherwise GT is set to ./.
