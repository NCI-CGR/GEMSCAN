# GEMSCAN - GErMline Snp Small Indel CAller PipeliNe 

Joint variant calling with GATK4 HaplotypeCaller, Google DeepVariant 1.0.0 and Strelka2, coordinated via Snakemake.

## Authors

* Shalabh Suman, Bari Ballew and Wendy Wong 
* Technical Lead: Bin Zhu

## Usage

If you use this workflow in a paper, don't forget to give credits to the authors by citing the URL of this (original) repository and, if available, its DOI (see above). The documentation of this pipeline is at nci-cgr.github.io/gemscan/

## Contribute back

In case you have also changed or added steps, please consider contributing them back to the original repository:

1. [Fork](https://help.github.com/en/articles/fork-a-repo) the original repo to a personal or lab account.
2. [Clone](https://help.github.com/en/articles/cloning-a-repository) the fork to your local system, to a different place than where you ran your analysis.
3. Copy the modified files from your analysis to the clone of your fork, e.g., `cp -r workflow path/to/fork`. Make sure to **not** accidentally copy config file contents or sample sheets. Instead, manually update the example config files if necessary.
4. Commit and push your changes to your fork.
5. Create a [pull request](https://help.github.com/en/articles/creating-a-pull-request) against the original repository.
