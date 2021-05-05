## PWMA: Primary Meta-Analysis of single arm proportions (binary: events/total)
# The input data should contains the following columns:
#
# study,  year, E, N, treat
# Zimmer, 2021, 3, 20, Cabo
# Author, 2020, 5, 90, Cabo
# 
# Load meta package.
library (meta)

# Load jsonlite package.
# This package is used to convert the analysis results in JSON format,
# which is used in the Python backend and visualization
library(jsonlite)

# For fixing the empty Rplot.pdf
pdf(NULL)

# Load data in the CSV file
PRI_SINARM_PROP <- read.csv("{{ fn_csvfile }}")

# We will use the function metaprop to run the analysis
# some arguments (parameters) need to be set first
# model can be random-effects or fixed-effect (indicated with a logical)

# sm indicates transformations of proportions to calculate an overall population
# sm can be "PLOGIT", "PAS", "PFT", "PLN", "PRAW"
# - PLOGIT: Logit transformation (default)
# - PAS: Arcsine transformation 
# - PFT: Freeman-Tukey Double arcsine transformation
# - PLN: Log transformation
# - PRAW: Raw (untransformed, proportions)
#
# method can be "Inverse", "GLMM", "MH"
# - Inverse: Inverse Variance (default)
# - GLMM:  Generalised linear mixed model
# - GLMM only indicated when sm is PLOGIT and method.tau is ML. 
#
# method.tau can be "REML", "ML", "EB", "DL", "SJ", "HE", "HS", "PM"
# - REML: Restricted Maximum-likelihood
# - ML: Maximum Likelihood
# - EB: Empirical Bayes
# - DL: DerSimonian-Laird
# - SJ: Sidik-Jonkman
# - HE: Hedges
# - HS: Hunter-Schmidt
# - PM: Paul-Mendel
#
# hakn: Hartung-Knapp adjustment, whichcan be used only 
# if the model is random-effects (indicated with a logical)
# the value could be:
# - TRUE
# - FALSE
#
# adhoc.hakn: Adhoc correction to Hartung-Knapp adjustment
# it is used only if the model is random-effects and hakn is applied
# adhoc.hakn can be "se", "ci"
# - se
# - ci

results_raw <- metaprop(E, 
                       N,  
                       data = PRI_SINARM_PROP, 
                       studlab = study, 
                       comb.fixed = {{ is_fixed }}, 
                       comb.random = {{ is_random }}, 
                       sm = "{{ measure_of_effect }}", 
                       method = "{{ pooling_method }}", 
                       method.tau = "{{ tau_estimation_method }}", 
                       hakn = {{ hakn_adjustment }},
                       adhoc.hakn = "{{ adhoc_hakn }}")

{% if is_create_figure == 'yes' %}

# output the primary ma result in forest plot
fig_width <- 10
fig_height <- fig_width * (0.25 + results_raw$k * 0.03)
png(filename="{{ fn_outplt1 }}", 
    width=fig_width, height=fig_height, 
    units='in', res=150)
par(mar=c(1.5, 1, 1, 1))

forest.meta(results_raw, 
            col.square = "black", 
            col.diamond = "red", 
            col.diamond.lines.random = "black", 
            fontsize = 10, 
            squaresize = 0.5, 
            print.pval = TRUE, 
            pooled.events = TRUE, 
            pooled.totals = TRUE, 
            smlab = "PLOGIT (95% CI)", 
            weight.study = "random", 
            plotwidth = "08cm",  
            leftcols = c("studlab", "event", "n", "effect", "ci"), 
            leftlabs = c("Events", "Total"), 
            rightcols = c("w.random"), 
            rightlabs = c("Relative weight"), 
            prediction = FALSE, 
            col.predict = "blue",
            pscale = 100
            )

dev.off()

{% endif %}

# Run cumulative meta-analysis
# we will use the function metacum
# x will be an object of class meta
# sortvar can be indicated by an object of class meta or by an object of original data set
results_cum <- metacum(results_raw, 
                       sortvar = PRI_SINARM_PROP${{ cumulative_meta_analysis_sortby }})

{% if is_create_figure == 'yes' %}

# output the cumulative ma result in forest plot
fig_width <- 10
fig_height <- fig_width * (0.25 + results_raw$k * 0.04)
png(filename="{{ fn_cumuplt }}", 
    width=fig_width, height=fig_height, 
    units='in', res=150)
par(mar=c(2, 2, 2, 2))

#generating the forest plot for cumulative meta-analysis
forest.meta(results_cum, 
            col.square = "black", 
            col.diamond = "red", 
            col.diamond.lines.random = "black", 
            fontsize = 10, 
            squaresize = 0.5, 
            weight.study = "random", 
            lwd = 1.8, lty.random = 2, 
            plotwidth = "08cm", 
            spacing = 1.3, 
            # colgap.forest.left = "1cm", 
            # colgap.forest.right = "0.1cm", 
            colgap.left = "0.5cm",
            smlab = "PLOGIT (95% CI)",
            pscale = 100
            )

{% endif %}


# Merge all the results
# The primary_ma contains all the data to produce the primary meta-analysis plot
# The cumulative_ma contains all the data to produce the cumu plot
all_ret <- list(
    incdma = results_raw,
    cumuma = results_cum,
    version = list(
        jsonlite = packageVersion('jsonlite'),
        meta = packageVersion('meta')
    )
)

# Save results as JSON file!
jsonstr <- toJSON(all_ret, pretty=TRUE, force=TRUE)
cat(jsonstr, file = (con <- file("{{ fn_jsonret }}", "w", encoding = "UTF-8")))
close(con)
