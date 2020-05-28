# Load BUGSnet package.
# The details of installation process of BUGSnet are described in the official
# document: https://bugsnetsoftware.github.io/instructions.html
library(BUGSnet)

# Load jsonlite package.
# This package is used to convert the analysis results in JSON format,
# which is used in the Python backend and visualization
library(jsonlite)

# Load dataset csv file.
# the `fn_csvfile` variable will be replaced with actual file name
# in the Python script.
mydata <- read.csv("{{ fn_csvfile }}")

# Prepare data for BUGSnet package.
# The BUGSnet package requires a specific data format with some attributes.
# With `data.prep` function, the user input data will be transformed to the
# format needed.
dich.slr <- data.prep(arm.data = mydata,
                     varname.t = "treat",
                     varname.s = "study")

# Statistics on the network characteristics.
# The BUGSnet package provide this function to help understand the basic
# characteristics of this treatment network, including:
# 
# - Number of Interventions
# - Number of Studies
# - Total Number of Patients in Network
# - Total Possible Pairwise Comparisons
# - Total Number of Pairwise Comparisons With Direct Data
# - Is the network connected
# - Number of Two-arm Studies
# - Number of Multi-Arms Studies
# - Total Number of Events in Network
# - Number of Studies With No Zero Events
# - Number of Studies With At Least One Zero Event
# - Number of Studies with All Zero Events
#
# These results will be displayed in the frontend.
network.char <- net.tab(data = dich.slr,
                        outcome = "event",
                        N = "total", 
                        type.outcome = "binomial",
                        time = NULL)

# Build a fixed or random effect model.
# The `nma.model` function could build a effect model based on our input data
# and the parameters given, e.g., reference treatment, fixed or random effect.
# The `model_param_time_column` parameter is defined by measure (HR, RR, etc)
# If `HR` is specified in the parameters, `model_param_time_column` is `time`.
# The detail of this function can be found in:
# https://bugsnetsoftware.github.io/vignettes
# And:
# http://dx.doi.org/10.1186/s12874-019-0829-2
fr_effects_model <- nma.model(data=dich.slr,
                     outcome = "event",
                     N = "total",
                     reference = "{{ reference_treatment }}",
                     family = "binomial",
                     link = "{{ measure_of_effect_to_link }}",
                     {{ model_param_time_column }}
                     effects = "{{ fixed_or_random }}")

# Set the random seed and run this model.
# The number of iteration and other numbers are default for the Just Another 
# Gibbs Sampler (JAGS) package, BUGSnet calls JAGS in the background.
set.seed(20190829)
fr_effects_results <- nma.run(fr_effects_model,
                           n.iter = 10000,
                           n.adapt = 1000,
                           n.burnin = 1000)

# Calculate the Surface Under the Cumulative RAnking (SUCRA) score.
# The `sucra_largerbetter` variable is defined by user input parameter.
sucra.out <- nma.rank(fr_effects_results, 
                      largerbetter = {{ sucra_largerbetter }}, 
                      sucra.palette = "Set1")

# Generate league table.
# The columns are sorted by the SUCRA value
league.out <- nma.league(fr_effects_results,
                         central.tdcy="median",
                         order = sucra.out$order,
                         log.scale = FALSE,
                         low.colour = "springgreen4",
                         mid.colour = "white",
                         high.colour = "red",
                         digits = 2)

# Merge all the results.
# The network characteristic table shows the data in `network_char`.
# The network plot also shows the data in `network_char`.
# The league table shows the data in `league`.
# The forest plot also shows the data in `league`.
# The version information is used for identify the data format
# The SUCRA rank table shows the data in `sucraplot`
# The SUCRA figure shows the data in `sucraplot`
all_ret <- list(
    network_char = network.char,
    sucraplot = sucra.out$sucratable,
    league = league.out$longtable,
    version = list(
        jsonlite = packageVersion('jsonlite'),
        BUGSnet = packageVersion('BUGSnet'),
        netmeta = packageVersion('netmeta')
    )
)

# Save results as JSON file!
jsonstr <- toJSON(all_ret, pretty=TRUE, force=TRUE)
cat(jsonstr, file = (con <- file("{{ fn_jsonret }}", "w", encoding = "UTF-8")))
close(con)