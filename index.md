## Welcome to the GEMSCAN pipeline page

GEMSCAN is a Joint variant calling with GATK4 HaplotypeCaller, Google DeepVariant 1.0.0 and Strelka2, coordinated via Snakemake.

### Documentation

The documentation of GEMSCAN is currently available on [readthedocs](https://gemscan.readthedocs.io/en/latest/)

### Support or Contact

Having trouble with GEMSCAN? Please check the FAQ below for commonly encountered issues. If you can't find a solution there please create an issue on the [GEMSCAN repository](https://github.com/NCI-CGR/GEMSCAN) we would try to help you out. And if you have any suggestions we would love to hear from you as well!

### Common issues
- Failed to pull singularity image due to disk quota exceeded
   - The default directory location for the image cache is **$HOME/.singularity/cache**. You may want to change the default cache location by setting the **SINGULARITY_CACHEDIR** environmental variable to another location if you have a small quota for your home directory.  

