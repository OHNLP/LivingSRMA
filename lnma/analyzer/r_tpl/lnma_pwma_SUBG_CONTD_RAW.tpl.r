## Subgroup Analysis of raw data (continuous: mean/sd/N)
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
# SUBGROUP_CONTD_RAWDATA <- read_excel("C:/Users/sarsa/Desktop/Vitals/Research Stuff/MA/Studies/Living System/Code data_script/Data/SUBGROUP_CONTD_RAWDATA.xlsx")
SUBGROUP_CONTD_RAWDATA <- read.csv("{{ fn_csvfile }}") 

# the meta package requires a specific data format with some attributes.


# We will use the function metacont to run the analysis
# some arguments (parameters) need to be set first
# model can be random-effects or fixed-effect (indicated with a logical)

# sm can be "MD", "SMD"
# MD = Mean Difference
# SMD = Standardized Mean Difference
# if "SMD" we will need to specify method for estimation of SMD (method.smd)
# method.smd can be "Hedges", "Cohen", "Glass"

# method can only be "Inverse"


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
subgroupresults <- metacont(Nt, 
                       Mt, 
                       SDt, 
                       Nc, 
                       Mc, 
                       SDc, 
                       data = SUBGROUP_CONTD_RAWDATA, 
                       studlab = study, 
                       comb.fixed = {{ is_fixed }}, 
                       comb.random = {{ is_random }}, 
                       sm = "{{ measure_of_effect }}", 
                       method.tau = "{{ tau_estimation_method }}", 
                       hakn = {{ is_hakn }}, 
                       byvar = subgroup, 
                       method.smd = "{{ smd_estimation_method }}")

fig_width <- 10
fig_height <- fig_width * (0.25 + subgroupresults$k * 0.06)
png(filename="{{ fn_outplt1 }}", width=fig_width, height=fig_height, units='in', res=200)
par(mar=c(1, 0, 1, 0))

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
            plotwidth = "9cm", 
            lwd = 1.8, 
            spacing = 1.3, 
            label.right = "Favours {{ control }}", 
            label.left = "Favours {{ treatment }}", 
            # colgap.forest.left = "1cm", 
            # colgap.forest.right = "0.1cm", 
            colgap.left = "0.5cm", 
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