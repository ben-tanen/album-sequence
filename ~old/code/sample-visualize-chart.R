library(data.table)
library(ggplot2)

n_obs <- 500

dt1 <- data.table(pos = 1:10, avg = c(3, 4, 7.5, 6, 5, 4, 3, 2.5, 3.2, 3.5))
dt2 <- data.table(pos = sort(rep(dt1$pos, n_obs)), pop = unlist(lapply(dt1$avg, function(x) rnorm(n_obs, mean = x, sd = 1))))
dt2$pos_rand <- dt2$pos + rnorm(nrow(dt2), mean = 0, sd = 0.05)

ggplot(dt2, aes(x = pop, y = -pos_rand)) + geom_point(aes(color = factor(pos)))
