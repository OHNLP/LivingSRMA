## PWMA: Primary Meta-Analysis of raw data categorical (binary: events/total)
# Load meta package.
library (meta)

# For fixing the empty Rplot.pdf
pdf(NULL)

# Load data through read.csv
PRI_CAT_RAWDATA <- read.csv("{{ fn_csvfile }}")


# running the analysis
resultsraw <- metabin(Et, 
                      Nt, 
                      Ec, 
                      Nc, 
                      data = PRI_CAT_RAWDATA, 
                      studlab = study, 
                      comb.random = TRUE, 
                      comb.fixed = FALSE,
                      sm = "{{ measure_of_effect }}",
                      method = "MH", 
                      method.tau = "DL", 
                      hakn = {{ is_hakn }})


# generating the forest plot
# prediction interval can be used (indicated with a logical)
fig_width <- 10
fig_height <- fig_width * (0.25 + resultsraw$k * 0.03)
png(filename="{{ fn_outplt1 }}", width=fig_width, height=fig_height, units='in', res=150)
# png(filename="{{ fn_outplt1 }}")
par(mar=c(2, 2, 2, 2))

forest.meta(resultsraw, 
            col.square = "black", 
            col.diamond = "red", 
            col.diamond.lines.random = "black", 
            fontsize = 10, 
            squaresize = 0.7, 
            print.pval = TRUE, 
            lab.e = "Treatment", 
            lab.c = "Control", 
            pooled.totals = TRUE, 
            pooled.events = TRUE, 
            smlab = "{{ smlab_text }} (95% CI)",
            weight.study = "random", 
            label.left = "Favours Treatment", 
            label.right = "Favours Control",  
            leftcols = c("studlab", "event.e", "n.e", "event.c", "n.c", "effect", "ci"), 
            leftlabs = c("Events", "Total", "Events", "Total"), 
            rightcols = c("w.random"), 
            rightlabs = c("Relative weight"))

dev.off()


#CUMULATIVE META-ANALYSIS
#running cumulative meta-analysis
# we will use the function metacum
# sortvar can be indicated by an object of class meta or by an object of original data set
resultsraw2 <- metabin(Et, 
                       Nt, 
                       Ec, 
                       Nc, 
                       data = PRI_CAT_RAWDATA, 
                       studlab = study, 
                       comb.random = TRUE, 
                       comb.fixed = FALSE,
                       sm = "{{ measure_of_effect }}",
                       method = "MH", 
                       method.tau = "DL")
results.cum <- metacum(resultsraw2, sortvar = PRI_CAT_RAWDATA$year)

fig_width <- 10
fig_height <- fig_width * (0.25 + resultsraw$k * 0.04)
png(filename="{{ fn_cumuplt }}", width=fig_width, height=fig_height, units='in', res=150)
# png(filename="{{ fn_cumuplt }}")
par(mar=c(2, 2, 2, 2))

#generating the forest plot for cumulative meta-analysis
forest.meta(results.cum, 
            col.square = "black", 
            col.diamond = "red", 
            col.diamond.lines.random = "black", 
            fontsize = 10, 
            squaresize = 0.5, 
            weight.study = "random", 
            lwd = 1.8, lty.random = 2,  
            spacing = 1.3, 
            colgap.left = "0.5cm",
            smlab = "{{ smlab_text }} (95% CI)")

dev.off()