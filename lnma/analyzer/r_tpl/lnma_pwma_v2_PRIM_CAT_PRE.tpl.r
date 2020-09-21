## PWMA: Primary Meta-Analysis of precalculated (computed) risk ratios and risk difference! Yes! That's great!
# Load meta package.
library (meta)

# Load jsonlite package.
# This package is used to convert the analysis results in JSON format,
# which is used in the Python backend and visualization
library(jsonlite)

# For fixing the empty Rplot.pdf
pdf(NULL)

# Load data through readxl
# library(readxl)
# PRI_CAT_PREDATA <- read_excel("PRI_CAT_PREDATA.xlsx")

PRI_CAT_PREDATA <- read.csv("{{ fn_csvfile }}")

# the meta package requires a specific data format with some attributes.
# we need to calculate the SE
# for which we need to log transform the TE, lower and upper ci
# TE can be HR, OR, RR, RD, here we are using HR based data.
PRI_CAT_PREDATA$TE<-log(PRI_CAT_PREDATA$TE)
PRI_CAT_PREDATA$lowerci<-log(PRI_CAT_PREDATA$lowerci)
PRI_CAT_PREDATA$upperci<-log(PRI_CAT_PREDATA$upperci)
PRI_CAT_PREDATA$SE<-(PRI_CAT_PREDATA$upperci-PRI_CAT_PREDATA$lowerci)/3.92

# We will use the function metagen to run the analysis
# some arguments (parameters) need to be set first
# sm can be "HR", "OR", "RR", "RD"
# HR = Hazard Ratio
# OR = Odds Ratio
# RR = Relative Risk
# RD = Risk Difference

# model can be random-effects or fixed-effect (indicated with a logical)

# method.tau can be "REML", "ML", "EB", "DL", "SJ", "HE", "HS", "PM"
# REML = Restricted Maximum-likelihood
#	ML = Maximum Likelihood
#	EB = Empirical Bayes
#	DL = DerSimonian-Laird
#	SJ = Sidik-Jonkman
#	HE = Hedges
#	HS = Hunter-Schmidt
#	PM = Paul-Mendel

# hakn can be indicated with a logical only if random-effects is selected
# hakn = Hartung-Knapp adjustment

# running the analysis
results <- metagen(TE, 
                   SE, 
                   data = PRI_CAT_PREDATA, 
                   studlab = study, 
                   sm = "{{ measure_of_effect }}", 
                   comb.fixed = {{ is_fixed }}, 
                   comb.random = {{ is_random }}, 
                   method.tau = "DL", 
                   hakn = {{ is_hakn }})

# Merge all the results.
all_ret <- list(
    primma = results,
    version = list(
        jsonlite = packageVersion('jsonlite'),
        meta = packageVersion('meta')
    )
)

# Save results as json file!
jsonstr <- toJSON(all_ret, pretty=TRUE, force=TRUE)
cat(jsonstr, file = (con <- file("{{ fn_jsonret }}", "w", encoding = "UTF-8")))
close(con)