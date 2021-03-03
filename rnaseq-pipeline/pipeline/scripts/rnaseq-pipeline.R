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
suppressPackageStartupMessages(require(ggplot2))
suppressPackageStartupMessages(require(ggrepel))
suppressPackageStartupMessages(require(glue))
suppressPackageStartupMessages(require(VennDiagram))

#############################################
########## Step 1. Read gene counts
#############################################

load_gene_counts <- function(infile, outfile) {

    # Read counts
    count_matrix <- fread(infile) %>% column_to_rownames('gene_id') %>% as.matrix

    # Get sample info
    metadata_dataframe <- data.frame(sample_name=colnames(count_matrix)) %>% mutate(treatment=gsub('(.*)_.*', '\\1', sample_name)) %>% column_to_rownames('sample_name')

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
    deseq_dataframe <- results(dds, contrast=c('treatment', groups[2], groups[1]), alpha=0.05) %>% as.data.frame %>% rownames_to_column('gene_id')

    # Get gene symbols
    id_dataframe <- select(org.Hs.eg.db, unique(deseq_dataframe$gene_id), "SYMBOL", "ENSEMBL") %>% rename('gene_id'='ENSEMBL', 'gene_symbol'='SYMBOL')

    # Merge
    result_dataframe <- id_dataframe %>% merge(deseq_dataframe, by='gene_id') %>% drop_na %>% mutate(significant=padj < 0.05 & abs(log2FoldChange) > 1, direction=ifelse(significant, ifelse(log2FoldChange > 0, 'up', 'down'), 'ns'))

    # Write
    fwrite(result_dataframe, file=outfile, sep='\t')

}

##########################################################
########## Step 3. Volcano plot
##########################################################

volcano_plot <- function(infile, outfile) {

    # Read results
    deseq_dataframe <- fread(infile)

    # Get genes
    gene_dataframe <- deseq_dataframe %>% filter(significant==TRUE) %>% group_by(direction) %>% slice_min(padj, n=10)

    # Groups
    groups <- strsplit(gsub('.*/(.*)-.*', '\\1', infile), '_vs_')[[1]]

    # Plot
    gp <- ggplot(deseq_dataframe, aes(x=log2FoldChange, y=-log10(padj), color=direction)) + 
        geom_point() +
        scale_color_manual(values=c('navyblue', 'black', 'red3')) +
        geom_label_repel(data=gene_dataframe, aes(label=gene_symbol)) +
        guides(color=FALSE) +
        theme_classic() +
        labs(title=glue('Volcano plot - {groups[1]} vs {groups[2]}')) +
        theme(plot.title = element_text(hjust = 0.5))

    # Save
    ggsave(file=outfile, height=7, width=7)

}

##########################################################
########## Step 4. Plot Venn diagram
##########################################################

plot_venn_diagram <- function(infiles, outfile) {

    # Read data
    deseq_dataframe <- lapply(infiles, function(x) { fread(x) %>% mutate(comparison=gsub('.*/(.*)-.*', '\\1', x)) }) %>% bind_rows

    # Get differential genes
    differential_genes <- deseq_dataframe %>% filter(significant == TRUE) %>% group_by(comparison) %>% summarize(genelist=list(gene_id))
    genelist <- setNames(differential_genes$genelist, differential_genes$comparison)

    # Plot
    venn.diagram(
        x = genelist,
        filename = outfile,
        output = FALSE ,
        imagetype="png" ,
        height = 480 , 
        width = 480 , 
        resolution = 300,
        compression = "lzw",
        lwd = 1,
        col=c('#e41a1c','#377eb8','#4daf4a'),
        fill = c(alpha("#e41a1c",0.3), alpha('#377eb8',0.3), alpha('#4daf4a',0.3)),
        cex = 0.5,
        fontfamily = "sans",
        cat.cex = 0.3,
        cat.default.pos = "outer",
        cat.pos = c(-27, 27, 135),
        cat.dist = c(0.055, 0.055, 0.085),
        cat.fontfamily = "sans",
        cat.col = c('#e41a1c','#377eb8','#4daf4a'),
        rotation = 1
    )

    # Remove log file
    system(glue('rm {outfile}*.log'))

}