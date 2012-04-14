library(ggplot2)

# makes a table 
sink("../../writeup/tables/test.tex")
cat(1 +1)
sink()


# makes a plot
x <- runif(1000)
g <- qplot(x)
png("../../writeup/plots/hist.png")
print(g)
dev.off() 
