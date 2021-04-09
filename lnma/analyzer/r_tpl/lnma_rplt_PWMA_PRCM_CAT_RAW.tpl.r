## PWMA: Primary Meta-Analysis of raw data categorical (binary: events/total)
# this script won't generate plots
# Load meta package.
library (meta)

# Load jsonlite package.
# This package is used to convert the analysis results in JSON format,
# which is used in the Python backend and visualization
library(jsonlite)

# For fixing the empty Rplot.pdf
pdf(NULL)

# Load data through read.csv
PRI_CAT_RAWDATA <- read.csv("{{ fn_csvfile }}")


# running the primary meta-analysis
resultsraw <- metabin(Et, 
                      Nt, 
                      Ec, 
                      Nc, 
                      data = PRI_CAT_RAWDATA, 
                      studlab = study, 
                      comb.random = TRUE, 
                      comb.fixed = FALSE,
                      sm = "{{ measure_of_effect }}",
                      method = "MH", 
                      method.tau = "DL", 
                      hakn = {{ is_hakn }})

# CUMULATIVE META-ANALYSIS
# running cumulative meta-analysis
# we will use the function metacum
# sortvar can be indicated by an object of class meta or by an object of original data set
resultsraw2 <- metabin(Et, 
                       Nt, 
                       Ec, 
                       Nc, 
                       data = PRI_CAT_RAWDATA, 
                       studlab = study, 
                       comb.random = TRUE, 
                       comb.fixed = FALSE,
                       sm = "{{ measure_of_effect }}",
                       method = "MH", 
                       method.tau = "DL")
results.cum <- metacum(resultsraw2, sortvar = PRI_CAT_RAWDATA$year)

# Merge all the results
# The primary_ma contains all the data to produce the primary meta-analysis plot
# The cumulative_ma contains all the data to produce the cumu plot
all_ret <- list(
    primma = resultsraw,
    cumuma = results.cum,
    version = list(
        jsonlite = packageVersion('jsonlite'),
        meta = packageVersion('meta')
    )
)

# Save results as JSON file!
jsonstr <- toJSON(all_ret, pretty=TRUE, force=TRUE)
cat(jsonstr, file = (con <- file("{{ fn_jsonret }}", "w", encoding = "UTF-8")))
close(con)
