#!/bin/bash

module load singularity

python print_version.py

snakemake --profile profiles/biowulf --jobs 500 --unlock

snakemake  --profile profiles/biowulf -rp --use-singularity --singularity-args "--bind /DCEG" --jobs 2000 --latency-wait 360 --rerun-incomplete
