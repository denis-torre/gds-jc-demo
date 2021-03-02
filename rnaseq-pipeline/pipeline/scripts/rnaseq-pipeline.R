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

    # save
    save(dds, file=outfile)

}