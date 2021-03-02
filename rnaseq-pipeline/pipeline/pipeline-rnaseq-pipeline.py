#################################################################
#################################################################
############### Demo RNA-Seq Pipeline ###########################
#################################################################
#################################################################
##### Author: Denis Torre
##### Icahn School of Medicine at Mount Sinai

#############################################
########## 1. Pipeline setup
#############################################
### 1. Python
from ruffus import *
import ruffus.cmdline as cmdline
import sys, os
import pandas as pd
import numpy as np

### 2. Custom
sys.path.append('pipeline/scripts')
import job_manager

### 3. Function to run R jobs
# Minerva queue to use
# NOTE: insert your lab's queue to run jobs yourself!
P = 'acc_GuccioneLab'

# R
def run_r_job(func_name, func_input, outfile, W = '00:30', GB = 5, n = 1, q = 'express', **kwargs):
	job_manager.run_r_job(func_name, func_input, outfile, r_source='pipeline/scripts/rnaseq-pipeline.R', P=P, W = W, GB = GB, n = n, q = q, mkdir=True, **kwargs)

#######################################################
#######################################################
########## Pipeline steps
#######################################################
#######################################################

#############################################
########## Step 1. Read gene counts
#############################################
# Input: gene expression file in TSV format
# Output: SummarizedExperiment file in .rda file
# Type of operation: 1-to-1
# Ruffus decorator used: transform

# Input file path
counts_file = 'data/test.tsv'

@transform(counts_file,
		   suffix('.tsv'),
		   '.rda')

def readGeneCounts(infile, outfile):

	# Run
	run_r_job('read_gene_counts', infile, outfile, run_locally=True)

##################################################
##################################################
########## Run pipeline
##################################################
##################################################
# Get options specified from commandline
options = cmdline.get_argparse().parse_args()

# Run indicated steps
if __name__ == '__main__':
	cmdline.run(options)
print('Done!')