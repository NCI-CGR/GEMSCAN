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

#### Config file

Please create the config.yaml file from the config_template.yaml and edit accordingly, please note that you need to:
- provide full path to strelka2_glnexus.yml for glnexus_strelka2_config if strelka2 is used
- outputDir is default to './' if clusterMode is set to 'cluster'. If you are running on GCP, please set to a gs storage bucket accordingly


#### Expected Outputs

Depends on run mode selected in the config, but can include:
Multi-sample VCF called with DeepVariant
Multi-sample VCF called with HaplotypeCaller
Multi-sample VCF called with Strelka2
Multi-sample VCF containing the union of the DeepVariant, HaplotypeCaller and Strelka2 calls
