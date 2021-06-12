## PWMA: Primary Meta-Analysis of raw data categorical (binary: events/total)
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
# PRI_CAT_RAWDATA <- read_excel("PRI_CAT_RAWDATA.xlsx")
PRI_CAT_RAWDATA <- read.csv("{{ fn_csvfile }}")

# the meta package requires a specific data format with some attributes.


# We will use the function metabin to run the analysis
# some arguments (parameters) need to be set first
# model can be random-effects or fixed-effect (indicated with a logical)

# sm can be "OR", "RR", "RD"
# OR = Odds Ratio
# RR = Relative Risk
# RD = Risk Difference

# method can be "Inverse", "Peto", "MH"
# MH = Mantel-Haenszel
# Peto can only be indicated if model is fixed-effect and sm is OR

# method.tau can be "REML", "ML", "EB", "DL", "SJ", "HE", "HS", "PM"
# REML = Restricted Maximum-likelihood
#	ML = Maximum Likelihood
#	EB = Empirical Bayes
#	DL = DerSimonian-Laird
#	SJ = Sidik-Jonkman
#	HE = Hedges
#	HS = Hunter-Schmidt
#	PM = Paul-Mendel

# hakn can be used only if the model is random-effects (indicated with a logical)
# hakn = Hartung-Knapp adjustment

# running the analysis
resultsraw <- metabin(Et, 
                      Nt, 
                      Ec, 
                      Nc, 
                      data = PRI_CAT_RAWDATA, 
                      studlab = study, 
                      comb.fixed = {{ is_fixed }}, 
                      comb.random = {{ is_random }}, 
                      sm = "{{ measure_of_effect }}", 
                      method = "{{ pooling_method }}", 
                      method.tau = "{{ tau_estimation_method }}", 
                      hakn = {{ is_hakn }})

# generating the forest plot
# prediction interval can be used (indicated with a logical)
fig_width <- 10
fig_height <- fig_width * (0.25 + resultsraw$k * 0.03)
png(filename="{{ fn_outplt1 }}", width=fig_width, height=fig_height, units='in', res=200)
par(mar=c(1.5, 1, 1, 1))

forest.meta(resultsraw, 
            col.square = "black", 
            col.diamond = "red", 
            col.diamond.lines.{{ fixed_or_random }} = "black", 
            fontsize = 10, 
            squaresize = 0.5, 
            print.pval = TRUE, 
            lab.e = "{{ treatment }}", 
            lab.c = "{{ control }}", 
            pooled.totals = TRUE, 
            pooled.events = TRUE, 
            smlab = "{{ smlab_text }} (95% CI)", 
            weight.study = "{{ fixed_or_random }}", 
            # lwd = 1.8, 
            # plotwidth = "08cm", 
            # spacing = 1.3, 
            label.left = "Favours {{ treatment }}", 
            label.right = "Favours {{ control }}", 
            # colgap.forest.left = "1cm", 
            # colgap.forest.right = "0.1cm", 
            # colgap.left = "0.5cm", 
            leftcols = c("studlab", "event.e", "n.e", "event.c", "n.c", "effect", "ci"), 
            leftlabs = c("Events", "Total", "Events", "Total"), 
            rightcols = c("w.{{ fixed_or_random }}"), 
            rightlabs = c("Relative weight"), 
            prediction = {{ is_prediction }}, 
            col.predict = "blue")

dev.off()


#generating the funnel plot (This is only for primary analysis- not for sensitivity and cumulative analysis)
fig_width <- 8
fig_height <- fig_width * 0.6
png(filename="{{ fn_fnnlplt }}", width=fig_width, height=fig_height, units='in', res=200)
par(mar=c(2, 2, 1, 1))

funnel.meta(resultsraw)

dev.off()


{% if sensitivity_analysis == 'yes' %}
#Sensitivity analysis by exclusion (multiple options to exclude more than one study)
results.sensitivity<- update.meta(resultsraw, subset = study != c({{ sensitivity_analysis_exsubset }}))

fig_width <- 10
fig_height <- fig_width * (0.25 + (resultsraw$k - {{ sensitivity_analysis_excluded_study_list|length }}) * 0.03)
png(filename="{{ fn_sensplt }}", width=fig_width, height=fig_height, units='in', res=200)
par(mar=c(1.5, 1, 1, 1))

#generating  the forest plot for sensitivity analysis
forest.meta(results.sensitivity, 
            col.square = "black", 
            col.diamond = "red", 
            col.diamond.lines.{{ fixed_or_random }} = "black", 
            fontsize = 10, 
            squaresize = 0.5, 
            print.pval = TRUE, 
            lab.e = "{{ treatment }}", 
            lab.c = "{{ control }}", 
            pooled.totals = TRUE, 
            pooled.events = TRUE, 
            smlab = "{{ smlab_text }} (95% CI)", 
            weight.study = "{{ fixed_or_random }}", 
            lwd = 1.8, 
            # plotwidth = "08cm", 
            spacing = 1.3, 
            label.left = "Favours {{ treatment }}", 
            label.right = "Favours {{ control }}", 
            # colgap.forest.left = "1cm", 
            # colgap.forest.right = "0.1cm", 
            # colgap.left = "0.5cm", 
            leftcols = c("studlab", "event.e", "n.e", "event.c", "n.c", "effect", "ci"), 
            leftlabs = c("Events", "Total", "Events", "Total"), 
            rightcols = c("w.{{ fixed_or_random }}"), 
            rightlabs = c("Relative weight"), 
            prediction = {{ is_prediction }}, 
            col.predict = "blue")

dev.off()
{% endif %}


{% if cumulative_meta_analysis == 'yes' %}
#running cumulative meta-analysis
# we will use the function metacum
# x will be an object of class meta
# sortvar can be indicated by an object of class meta or by an object of original data set
results.cum <- metacum(
    resultsraw, 
    sortvar = PRI_CAT_RAWDATA${{ cumulative_meta_analysis_sortby }}
)

fig_width <- 10
fig_height <- fig_width * (0.25 + resultsraw$k * 0.04)
png(filename="{{ fn_cumuplt }}", width=fig_width, height=fig_height, units='in', res=200)
par(mar=c(2, 2, 2, 2))

#generating the forest plot for cumulative meta-analysis
forest.meta(results.cum, 
            col.square = "black", 
            col.diamond = "red", 
            col.diamond.lines.{{ fixed_or_random }} = "black", 
            fontsize = 10, 
            squaresize = 0.5, 
            weight.study = "{{ fixed_or_random }}", 
            lwd = 1.8, lty.{{ fixed_or_random }} = 2, 
            # plotwidth = "08cm", 
            spacing = 1.3, 
            # colgap.forest.left = "1cm", 
            # colgap.forest.right = "0.1cm", 
            colgap.left = "0.5cm",
            smlab = "{{ smlab_text }} (95% CI)")

dev.off()

# Merge all the results.
all_ret <- list(
    results = resultsraw,
    primma = resultsraw,
    cumuma = results.cum,
    version = list(
        jsonlite = packageVersion('jsonlite'),
        meta = packageVersion('meta')
    )
)

{% else %}

# Merge all the results.
all_ret <- list(
    results = resultsraw,
    primma = resultsraw,
    version = list(
        jsonlite = packageVersion('jsonlite'),
        meta = packageVersion('meta')
    )
)

{% endif %}



# Save results as json file!
jsonstr <- toJSON(all_ret, pretty=TRUE, force=TRUE)
cat(jsonstr, file = (con <- file("{{ fn_jsonret }}", "w", encoding = "UTF-8")))
close(con)