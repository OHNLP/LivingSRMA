# Load gemtc package.
# The Markov Chain Monte Carlo simulation procedures, such as the Gibbs sampling
# are implemented in this package, which is used to build the bayesian network 
# meta-analysis model 
library(gemtc)

# Load meta package
# This package provides the functions to convert HR/Lower/Upper to TE/seTE
# Details are here: https://rdrr.io/cran/meta/src/R/TE.seTE.ci.R
library(meta)

# Load netmeta package.
# The details of installation of netmeta are described in the official document: 
# https://bookdown.org/MathiasHarrer/Doing_Meta_Analysis_in_R/frequentist.html
library(netmeta)

# Load the dmetar package.
# dmetar package provide additional functionality for the meta package, so of 
# which are used in this frequentist analysis.
# The detail of this package can be found in: https://dmetar.protectlab.org/
# And the installation is as follows:
# https://bookdown.org/MathiasHarrer/Doing_Meta_Analysis_in_R/dmetar.html
library(dmetar)

# Load jsonlite package.
# This package is used to convert the analysis results in JSON format,
# which is used in the Python backend and visualization
library(jsonlite)

# Load dataset csv file.
# the `fn_csvfile` variable will be replaced with actual file name
# in the Python script.
mydata_netmeta <- read.csv("{{ fn_csvfile_netmeta }}")

# Get TE and seTE.
# In our case, the TE is HR, and the seTE is calculated by lowerci and upperci.
# Details are here: https://rdrr.io/cran/meta/src/R/TE.seTE.ci.R
TEseTE <- metagen(lower = mydata_netmeta$lowerci, upper = mydata_netmeta$upperci)

# Prepare data for netmeta package.
# The netmeta package requires a specific data format with some attributes.
# Such as `TE`, `seTE`, which can be calculated before running this script.
# Since current version only supports Hazard Ratio analysis, the `sm`
# attribute is set to 'HR' as default.
# It seems that the treatment1 (t1) is the comparator.
nma <- netmeta(TE = mydata_netmeta$TE,
    seTE = mydata_netmeta$seTE,
    treat1 = mydata_netmeta$t1,
    treat2 = mydata_netmeta$t2,
    studlab = paste(mydata_netmeta$study),
    data = mydata_netmeta,
    sm = "{{ measure_of_effect }}",
    comb.fixed = {{ is_fixed }},
    comb.random = {{ is_random }},
    reference.group = "{{ reference_treatment }}"
)

# Generate network plot.
mynetplt <- netgraph(nma)

# Generate league table.
myleaguetb <- netleague(nma, bracket="(", digits=2)

# Generate forest plot.
myforest <- forest(nma)

# Generate ranks
# the default output on the screen looks like the following
##               P-score
## Rosiglitazone  0.9789
## Metformin      0.8513
## Pioglitazone   0.7686
## Miglitol       0.6200
## Benfluorex     0.5727
## Acarbose       0.4792
## Vildagliptin   0.3512
## Sitagliptin    0.2386
## Sulfonylurea   0.1395
## Placebo        0.0000
# But the format of output variable is different.
# The format will be parsed with help of `nma$trts` variable
myrank = netrank(nma, small.values="{{ small_values_are }}")

# Load dataset csv file.
# the `fn_csvfile` variable will be replaced with actual file name
# in the Python script.
mydata <- read.csv("{{ fn_csvfile }}")

# Construct network.
# To conduct the bayesian network analysis, a network data structure must
# be built for the next steps, which follows:
# https://bookdown.org/MathiasHarrer/Doing_Meta_Analysis_in_R/bayesnma.html
network <- mtc.network(data.re = mydata)

# Build model.
# First, specify the network object we created.
# Second, specify whether use random or fixed model.
# Lastly, specify the number of Markov chains.
# According to the tutorial, a value between 3 and 4 is sensible.
model <- mtc.model(network, 
                   linearModel = "{{ fixed_or_random }}",
                   n.chain = {{ mtc_model_n_chain }})

# Run the simulation.
# We defined the number of iteration to 10000 to achieve accurate estimates.
mcmc2 <- mtc.run(model, n.adapt = 500, n.iter = 10000, thin = 10)

# Calculate the probability for each treatment to be the best, second best,
# third best, and so forth, option.
rank.probs <- rank.probability(mcmc2)

# Get the rownames
rank.probsmat = as.matrix(rank.probs)
rank.rownames = rownames(rank.probsmat)

# Calcuate the SUCRA
# The `sucra_lower_is_better` is defined by user 
rank.sucra <- sucra(rank.probs, lower.is.better = {{ sucra_lower_is_better }})

# Merge all the results.
# The network characteristic table shows the data in `nma`.
# The network plot shows the data in `mynetplt`.
# The league table shows the data in `myleaguetb`.
# The forest plot also shows the data in `myforest`.
# The version information is used for identify the data format
# The SUCRA rank table shows the data in `sucrarank`
# The SUCRA figure shows the data in `sucraplot`
all_ret <- list(
    nma = nma,
    mynetplt = mynetplt,
    myleaguetb = myleaguetb,
    myforest = myforest,
    myrank = list(
        trts = nma$trts,
        fixed = myrank$Pscore.fixed,
        random = myrank$Pscore.random
    ),
    sucraplot = list(
        probs = rank.probs,
        rows = rank.rownames
    ),
    sucrarank = rank.sucra,
    version = list(
        jsonlite = packageVersion('jsonlite'),
        dmetar = packageVersion('dmetar'),
        gemtc = packageVersion('gemtc'),
        netmeta = packageVersion('netmeta')
    )
)

# Save results as json file!
jsonstr <- toJSON(all_ret, pretty=TRUE, force=TRUE)
cat(jsonstr, file = (con <- file("{{ fn_jsonret }}", "w", encoding = "UTF-8")))
close(con)