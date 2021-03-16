#!/bin/bash
# properties = {properties}
set -euo pipefail

#export TMPDIR=/lscratch/$SLURM_JOB_ID

{exec_job}
