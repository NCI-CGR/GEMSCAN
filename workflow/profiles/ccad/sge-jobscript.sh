#!/bin/bash

# properties = {properties}
#$ -terse
#$ -S /bin/bash
#$ -cwd
#$ -j yes

# properties = {properties}


set -euo pipefail


{exec_job}

echo $?
