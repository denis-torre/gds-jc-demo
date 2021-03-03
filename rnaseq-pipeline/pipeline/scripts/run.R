# Initialize parser
library(optparse)
parser <- OptionParser()
parser <- add_option(parser, c("-f", "--func_name"), help="Function name")
parser <- add_option(parser, c("-s", "--r_source"), help="Source of R function to run")
parser <- add_option(parser, c("-i", "--func_input"), help="Path of input file or list of paths")
parser <- add_option(parser, c("-o", "--outfile"), help="Path of output file for function")
parser <- add_option(parser, c("-a", "--additional_params"), default=NULL, help="Additional parameters to be passed to function")

# Parse arguments
args <- parse_args(parser)

# Split
for (param in c('func_input', 'additional_params')) {
    if ((!is.null(args[[param]])) && (grepl(',', args[[param]]))) {
        args[[param]] <- strsplit(args[[param]], ',')[[1]]
    }
}

# Load library
source(args$r_source)

# Get params
params <- list(args$func_input, args$outfile)
if (!is.null(args$additional_params)) {
    params[[length(params)+1]] <- args$additional_params
}

# Call function
do.call(args$func_name, params)