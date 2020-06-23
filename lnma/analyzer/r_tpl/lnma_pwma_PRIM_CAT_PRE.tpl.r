## PWMA: Primary Meta-Analysis of precalculated (computed) risk ratios
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
                   method.tau = "{{ tau_estimation_method }}", 
                   hakn = {{ is_hakn }})

# generating the forest plot
# prediction interval can be indicated with a logical
fig_width <- 8
fig_height <- fig_width * 0.66
png(filename="{{ fn_outplt1 }}", width=fig_width, height=fig_height, units='in', res=300)
par(mar=c(2, 2, 2, 2))

forest.meta(results, 
            col.square = "black", 
            col.diamond = "red", 
            col.diamond.lines.{{ fixed_or_random }} = "black", 
            fontsize = 10, 
            squaresize = 0.5, 
            print.pval = TRUE, 
            smlab = "{{ smlab_text }} (95% CI)", 
            weight.study = "{{ fixed_or_random }}", 
            lwd = 1.8, lty.{{ fixed_or_random }} = 2, 
            plotwidth = "08cm", 
            spacing = 1.3, 
            # colgap.forest.left = "1cm", 
            # colgap.forest.right = "0.1cm", 
            # colgap.left = "0.5cm", 
            leftcols = c("studlab", "effect", "ci"), 
            rightcols = c("w.{{ fixed_or_random }}"), 
            rightlabs = c("Relative weight"), 
            prediction = {{ is_prediction }}, 
            col.predict = "blue")

dev.off()

{% if sensitivity_analysis == 'no' and cumulative_meta_analysis == 'no' %}
#generating the funnel plot (This is only for primary analysis- not for sensitivity and cumulative analysis)
fig_width <- 8
fig_height <- fig_width * 0.66
png(filename="{{ fn_fnnlplt }}", width=fig_width, height=fig_height, units='in', res=300)
par(mar=c(2, 2, 2, 2))

funnel.meta(results)

dev.off()
{% endif %}

{% if sensitivity_analysis == 'yes' %}
#Sensitivity analysis by exclusion (multiple options to exclude more than one study)
results.sensitivity<- update.meta(results, subset = study != c("Tomita Y et al"))

#generating the forest plot for sensitivity analysis
forest.meta(results.sensitivity, 
            col.square = "black", 
            col.diamond = "red", 
            col.diamond.lines.{{ fixed_or_random }} = "black", 
            fontsize = 10, 
            squaresize = 0.5, 
            print.pval = TRUE, 
            smlab = "{{ smlab }} (95% CI)", 
            weight.study = "{{ fixed_or_random }}", 
            lwd = 1.8, lty.{{ fixed_or_random }} = 2, 
            plotwidth = "08cm", 
            spacing = 1.3, 
            colgap.forest.left = "1cm", 
            colgap.forest.right = "0.1cm", 
            colgap.left = "0.5cm", 
            leftcols = c("studlab", "effect", "ci"), 
            rightcols = c("w.{{ fixed_or_random }}"), 
            rightlabs = c("Relative weight"), 
            prediction = {{ is_prediction }}, 
            col.predict = "blue")

{% endif %}

#running cumulative meta-analysis
# we will use the function metacum
# x will be an object of class meta
# sortvar can be indicated by an object of class meta or by an object of original data set
{% if cumulative_meta_analysis == 'yes' %}
results.cum <- metacum(results, sortvar = PRI_CAT_PREDATA$year)

#generating the forest plot for cumulative meta-analysis
forest.meta(results.cum, 
            col.square = "black", 
            col.diamond = "red", 
            col.diamond.lines.{{ fixed_or_random }} = "black", 
            fontsize = 10, 
            squaresize = 0.5, 
            smlab = "{{ smlab_text }} (95% CI)", 
            weight.study = "{{ fixed_or_random }}", 
            lwd = 1.8, lty.{{ fixed_or_random }} = 2, 
            plotwidth = "08cm", 
            spacing = 1.3, 
            colgap.forest.left = "1cm", 
            colgap.forest.right = "0.1cm", 
            colgap.left = "0.5cm")
{% endif %}

# Merge all the results.
all_ret <- list(
    results = results,
    version = list(
        jsonlite = packageVersion('jsonlite'),
        netmeta = packageVersion('meta')
    )
)

# Save results as json file!
jsonstr <- toJSON(all_ret, pretty=TRUE, force=TRUE)
cat(jsonstr, file = (con <- file("{{ fn_jsonret }}", "w", encoding = "UTF-8")))
close(con)