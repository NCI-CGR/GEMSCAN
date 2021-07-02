## Miscellaneous

### bcftools plugin exchangeGT
We have written a bcftools plugin exchangeGT for the users to swap one of the GT fields, such as DV_GT, HC_GT and strelka2_GT, dv_priority_GT or concensus_GT as the main GT, it can be find in the bcftools_plugin directory in this repository. 

To use it, please checkout the bcftools GitHub repository, copy exchangeGT.c to its plugins directory and follow its installation directions [here](https://samtools.github.io/bcftools/howtos/install.html) to install it. 

You can get a list of options by:
```
bcftools +exchangeGT 
```

      
