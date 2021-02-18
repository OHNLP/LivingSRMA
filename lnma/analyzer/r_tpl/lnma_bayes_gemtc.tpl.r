library(gemtc)
library(rjags)
library(dmetar)
library(jsonlite)
data<-read.csv("{{ fn_csvfile }}")

network<-mtc.network(data.re = data)
model<-mtc.model(network, link="log", likelihood="poisson", linearModel="{{ fixed_or_random }}")
mcmc1<-mtc.run(model, n.adapt = 50, n.iter = 1000, thin = 1)
mtc.run(model) -> results
summary(results)

# RANKOGRAM
rank.probability <- rank.probability(mcmc1)
rank.probsmat = as.matrix(rank.probability)
rank.rownames = rownames(rank.probsmat)
rank.sucra<-sucra(rank.probability, lower.is.better = {{ sucra_lower_is_better }})
# rank.sucra<-sucra(rank.probability)

# plot(sucra)

# FORET PLOT
myforest <- forest(relative.effect(results, t1="{{ reference_treatment }}"), digits=2)

# LEAGUE TABLE (for back transforming and exporting)
league<-relative.effect.table(results)
expleague<-data.frame(exp(league))
#write.csv(expleague, file = "name.csv")

all_ret <- list(
    model = model,
    expleague = expleague,
    sucraplot = list(
        probs = rank.probability,
        rows = rank.rownames
    ),
    sucrarank = rank.sucra,
    version = list(
        jsonlite = packageVersion('jsonlite'),
        gemtc = packageVersion('gemtc')
    )
)

jsonstr <- toJSON(all_ret, pretty=TRUE, force=TRUE)
cat(jsonstr, file = (con <- file("{{ fn_jsonret }}", "w", encoding = "UTF-8")))
close(con)