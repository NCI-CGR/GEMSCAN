## Welcome to the GEMSCAN pipeline page

GEMSCAN is a Joint variant calling with GATK4 HaplotypeCaller, Google DeepVariant 1.0.0 and Strelka2, coordinated via Snakemake.

### Documentation

- [Installation](Installation.md)
- [Inputs and outputs](inputs_and_outputs.md)
- [Running_on_DCEG_CCAD](ccad.md)
- [Running_on_NIH_Biowulf](biowulf.md)
- [Running_on_GCP](gcp.md)
- [Running_on_other_compute environments](other_compute_environments.md)
- [Miscellaneous](miscellaneous.md)

### Support or Contact

Having trouble with GEMSCAN? Please check the FAQ below for commonly encountered issues. If you can't find a solution there please create an issue on the [GEMSCAN repository](https://github.com/NCI-CGR/GEMSCAN) we would try to help you out. And if you have any suggestions we would love to hear from you as well!

### Common issues
- Failed to pull singularity image due to disk quota exceeded
   - The default directory location for the image cache is **$HOME/.singularity/cache**. You may want to change the default cache location by setting the **SINGULARITY_CACHEDIR** environmental variable to another location if you have a small quota for your home directory.  
- Job killed when pulling singularity images
   - From what I have seen singularity pull may require up to 2GB memory so to be safe please request at least 4GB for the Snakemake main job 
- specifying runtime in resources under the rules
   - Sometimes you may want to modify the time limit of a certain rule. Currently, the user would have to modify these in the Snakefile. Please note that GEMSCAN expects the runtime to be expressed in minutes, i.e. if you want to put a limit of 1 hour, please put runtime=60 
- We have not tested the pipeline with huge number of samples and some of the rules may require much longer running time than the default settings. If your job is killed due to time limits please try to add time to resources in the rules or edit profiles/biowulf/cluster_config.yaml to increase the default time limit, if you are on biowulf.  
