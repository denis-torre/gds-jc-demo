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
P = 'acc_YOURQUEUE'

# R
def run_r_job(func_name, func_input, outfile, W = '00:30', GB = 5, n = 1, q = 'express', modules=['R/3.5.3', 'python/3.7.3'], **kwargs):
	job_manager.run_r_job(func_name, func_input, outfile, r_source='pipeline/scripts/rnaseq-pipeline.R', P=P, W = W, GB = GB, n = n, q = q, modules = modules, mkdir=True, **kwargs)

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
counts_file = 'data/counts.tsv'

@transform(counts_file,
		   suffix('.tsv'),
		   '.rda')

def loadGeneCounts(infile, outfile):

	# Run
	run_r_job('read_gene_counts', infile, outfile, run_locally=True)

#######################################################
########## Step 2. Get differentially expressed genes
#######################################################
# Input: output of loadGeneCounts function (SummarizedExperiment file in .rda file)
# Output: multiple TSV files with differential genes, one per comparison
# Type of operation: 1-to-many
# Ruffus decorator used: subdivide

@subdivide(loadGeneCounts,
		   regex(r'(.*).rda'),
		   r'data/*_vs_*-differential_genes.tsv',
		   r'data/{comparison[0]}_vs_{comparison[1]}-differential_genes.tsv')

def runDifferentialExpression(infile, outfiles, outfileRoot):

	# Define comparisons
	comparisons = [
		['DMSO', 'DrugA'],
		['DMSO', 'DrugB'],
		['DMSO', 'DrugC']
	]

	# Loop through comparisons
	for comparison in comparisons:

		# Get outfile name
		outfile = outfileRoot.format(**locals())

		# Run
		run_r_job('run_differential_expression', infile, outfile, run_locally=True)

##########################################################
########## Step 3. Volcano plot
##########################################################
# Input: output of runDifferentialExpression function (.tsv files)
# Output: one image per comparison
# Type of operation: 1-to-1
# Ruffus decorator used: transform

@transform(runDifferentialExpression,
		   suffix('.tsv'),
		   '.png')

def volcanoPlot(infile, outfile):

	# Run
	run_r_job('volcano_plot', infile, outfile, run_locally=True)

##########################################################
########## Step 4. Plot Venn diagram
##########################################################
# Input: output of runDifferentialExpression function (.tsv files)
# Output: a venn diagram showing overlap between DEGs
# Type of operation: many-to-1
# Ruffus decorator used: merge

@follows(volcanoPlot) # requires volcanoPlot to be run before

@merge(runDifferentialExpression,
	   'data/differential_genes-venn_diagram.png')

def plotVennDiagram(infiles, outfile):

	# Run
	run_r_job('plot_venn_diagram', infiles, outfile, run_locally=True)

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