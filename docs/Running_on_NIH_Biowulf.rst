.. _`Running on the Biowulf cluster`:

Running on the Biowulf cluster (Slurm)
======================================

Prepare the pipeline
--------------------

- activate the snakemake conda environment created in the installation step 

	``conda activate snakemake``

- clone the repository

- modify config/samples.txt and config/config.yaml as described in :ref:`Input_and_Output`

- go to workflow directory

	``cd <cloned repo dir>/workflow``

- create a script that looks like this

	``#!/bin/bash
	#SBATCH -o <cloned repo dir>/workflow/snakemake.out
	#SBATCH -e <cloned repo dir>/workflow/snakemake.err
	module load singularity
	snakemake  --profile profiles/biowulf --use-singularity --singularity-args "--bind /data/$USER,/fdb,/scratch,/lscratch" --jobs 100``

- submit the script 

	``sbatch --time=48:00:00 <script>``

- monitor the jobs

	``squeue -u <your_username>``

- The log files are in ``<cloned repo dir>/workflow/logs/``, it is also useful to look at ``<cloned repo dir>/workflow/snakemake.err`` to see the snakemake running progress and potential errors