#################################################################
#################################################################
############### Demo RNA-Seq Pipeline - R Support ###############
#################################################################
#################################################################
# Load libraries
suppressPackageStartupMessages(require(DESeq2))
suppressPackageStartupMessages(require(data.table))
suppressPackageStartupMessages(require(dplyr))
suppressPackageStartupMessages(require(tibble))
suppressPackageStartupMessages(require(tidyr))
suppressPackageStartupMessages(require(org.Hs.eg.db))

#############################################
########## Step 1. Read gene counts
#############################################

read_gene_counts <- function(infile, outfile) {

    # Read counts
    count_matrix <- fread(infile) %>% column_to_rownames('gene_id') %>% as.matrix

    # Get sample info
    metadata_dataframe <- data.frame(sample_name=colnames(count_matrix)) %>% mutate(treatment=gsub('(.*)_.', '\\1', sample_name)) %>% column_to_rownames('sample_name')

    # Create DDS
    dds <- DESeqDataSetFromMatrix(countData = count_matrix, colData = metadata_dataframe, design = ~treatment)

    # Run DESeq
    dds <- DESeq(dds)

    # save
    save(dds, file=outfile)

}

#######################################################
########## Step 2. Get differentially expressed genes
#######################################################

run_differential_expression <- function(infile, outfile) {

    # Load
    load(infile)

    # Get groups
    groups <- strsplit(gsub('.*/(.*)-.*', '\\1', outfile), '_vs_')[[1]]

    # Get results
    deseq_dataframe <- results(dds, contrast=c('treatment', groups[2], groups[1])) %>% as.data.frame %>% rownames_to_column('gene_id')

    # Get gene symbols
    id_dataframe <- select(org.Hs.eg.db, unique(deseq_dataframe$gene_id), "SYMBOL", "ENSEMBL") %>% rename('gene_id'='ENSEMBL', 'gene_symbol'='SYMBOL')

    # Merge
    result_dataframe <- id_dataframe %>% merge(deseq_dataframe, by='gene_id') %>% drop_na

    # Write
    fwrite(result_dataframe, file=outfile, sep='\t')

}

##########################################################
########## Step 3. Plot differential expression results
##########################################################

plot_differential_expression_results <- function(infile, outfile) {

    print(infile)
}