## Subgroup Analysis of precalculated (computed) risk ratios
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
# SUBGROUP_CAT_PREDATA <- read_excel("C:/Users/sarsa/Desktop/Vitals/Research Stuff/MA/Studies/Living System/Code data_script/Data/SUBGROUP_CAT_PREDATA.xlsx")
SUBGROUP_CAT_PREDATA <- read.csv("{{ fn_csvfile }}")

# the meta package requires a specific data format with some attributes.
# we need to calculate the SE
# for which we need to log transform the TE, lower and upper ci
# TE can be HR, OR, RR, RD, here we are using HR based data.
SUBGROUP_CAT_PREDATA$TE<-log(SUBGROUP_CAT_PREDATA$TE)
SUBGROUP_CAT_PREDATA$lowerci<-log(SUBGROUP_CAT_PREDATA$lowerci)
SUBGROUP_CAT_PREDATA$upperci<-log(SUBGROUP_CAT_PREDATA$upperci)
SUBGROUP_CAT_PREDATA$SE<-(SUBGROUP_CAT_PREDATA$upperci-SUBGROUP_CAT_PREDATA$lowerci)/3.92

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
subgroupresults <- metagen(TE, 
                   SE, 
                   data = SUBGROUP_CAT_PREDATA, 
                   studlab = study, 
                   sm = "{{ measure_of_effect }}", 
                   comb.fixed = {{ is_fixed }}, 
                   comb.random = {{ is_random }}, 
                   method.tau = "{{ tau_estimation_method }}", 
                   hakn = {{ is_hakn }}, 
                   byvar = subgroup)

fig_width <- 9
fig_height <- fig_width * (0.25 + subgroupresults$k * 0.06)
png(filename="{{ fn_outplt1 }}", width=fig_width, height=fig_height, units='in', res=200)
par(mar=c(1.5, 1, 1, 1))

# generating the forest plot
forest.meta(subgroupresults, 
            col.square = "black", 
            col.diamond = "red", 
            col.diamond.lines.{{ fixed_or_random }} = "black", 
            fontsize = 10, 
            squaresize = 0.5, 
            print.pval = TRUE, 
            smlab = "{{ smlab_text }} (95% CI)", 
            weight.study = "same", 
            lwd = 1.8, 
            spacing = 1.3, 
            label.right = "Favours {{ control }}", 
            label.left = "Favours {{ treatment }}", 
            plotwidth = "10cm", 
            # colgap.forest.left = "1cm", 
            # colgap.forest.right = "0.1cm", 
            # colgap.left = "0.5cm", 
            leftcols = c("studlab", "effect", "ci"), 
            rightcols = c("w.{{ fixed_or_random }}"), 
            rightlabs = c("Relative weight"), 
            col.study = "black", 
            test.subgroup.{{ fixed_or_random }} = TRUE, 
            col.by = "black")

dev.off()

# Merge all the results.
all_ret <- list(
    results = subgroupresults,
    version = list(
        jsonlite = packageVersion('jsonlite'),
        meta = packageVersion('meta')
    )
)

# Save results as json file!
jsonstr <- toJSON(all_ret, pretty=TRUE, force=TRUE)
cat(jsonstr, file = (con <- file("{{ fn_jsonret }}", "w", encoding = "UTF-8")))
close(con)