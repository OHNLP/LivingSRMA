# Load netmeta package.
# The details of installation of netmeta are described in the official document: 
# https://bookdown.org/MathiasHarrer/Doing_Meta_Analysis_in_R/frequentist.html
library(netmeta)

# Load jsonlite package.
# This package is used to convert the analysis results in JSON format,
# which is used in the Python backend and visualization
library(jsonlite)

# Load dataset csv file.
# the `fn_csvfile` variable will be replaced with actual file name
# in the Python script.
mydata_netmeta <- read.csv("{{ fn_csvfile }}")


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
    sm = "HR",
    comb.fixed = {{ is_fixed }},
    comb.random = {{ is_random }},
    reference.group = "{{ reference_treatment }}"
)

# Generate network plot.
mynetplt <- netgraph(nma)

# Generate league table.
myleaguetb <- netleague(nma, bracket="(", digits=2)

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
myrank = netrank(nma)

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
    myrank = list(
        trts = nma$trts,
        fixed = myrank$Pscore.fixed,
        random = myrank$Pscore.random
    ),
    version = list(
        jsonlite = packageVersion('jsonlite'),
        netmeta = packageVersion('netmeta')
    )
)

# Save results as json file!
jsonstr <- toJSON(all_ret, pretty=TRUE, force=TRUE)
cat(jsonstr, file = (con <- file("{{ fn_jsonret }}", "w", encoding = "UTF-8")))
close(con)