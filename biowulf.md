### Running on the Biowulf cluster (Slurm)

#### Prepare the pipeline

- clone the repository. 

```git clone https://github.com/NCI-CGR/GEMSCAN.git```

  This would clone the GEMSCAN github repository under your current folder, i.e. <your current dir>/GEMSCAN
  Alternatively, You could create a project folder say _my_variantCalling_project_ by
  ```mkdir my_variantCalling_project```
  and then clone the GEMSCAN repo to it:
  ```git clone https://github.com/NCI-CGR/GEMSCAN.git ./my_variantCalling_project```

- create config/samples.txt and config/config.yaml as described in the [Inputs and outputs](inputs_and_outputs.md) section.

- go to workflow directory

	```cd <cloned repo dir>/workflow```

- You might want to create a submission script that looks like this

	```
	#!/bin/bash
	#SBATCH --time=2-00:00:00
	#SBATCH -o <cloned repo dir>/workflow/snakemake.out
	#SBATCH -e <cloned repo dir>/workflow/snakemake.err
	
	module load singularity
	
	export SINGULARITY_CACHEDIR=/data/<yourusername>/
	
	eval "$(conda shell.bash hook)"
        conda activate snakemake
	
	snakemake  --profile profiles/biowulf --use-singularity --singularity-args "--bind /data/$USER,/fdb,/lscratch" --jobs 100
  ```

- If you have lots of samples, you may want to keep your main Snakemake workflow manager running until all the tasks finishes and it may exceed the maximum wall time of the norm partition on Biowulf. In that case you may want to use the unlimited partition, i.e.
	
	```
	#!/bin/bash
	#SBATCH --partition=unlimited	
	#SBATCH -o <cloned repo dir>/workflow/snakemake.out
	#SBATCH -e <cloned repo dir>/workflow/snakemake.err
	
	module load singularity
	
	export SINGULARITY_CACHEDIR=/data/<yourusername>/
	
	eval "$(conda shell.bash hook)"
        conda activate snakemake
	
	snakemake  --profile profiles/biowulf --use-singularity --singularity-args "--bind /data/$USER,/fdb,/lscratch" --jobs 100
  ```
	
	One thing to pay attention to is that if any data you use is not on the list of directories listed in the example script above, you will have to add them to --singularity-args after --bind, so that singularity will bind those folders as well.  

- Make sure you have a relatively updated Snakemake in your conda environment (>=5.26.1).  Then activate the snakemake conda environment created in the installation step 

	```conda activate snakemake```

- submit the script 

	```sbatch --time=48:00:00 <script>```

- monitor the jobs

	```squeue -u <your_username>```

- The log files are in ```<cloned repo dir>/workflow/logs/```, it is also useful to look at ```<cloned repo dir>/workflow/snakemake.err``` to see the snakemake running progress and potential errors
