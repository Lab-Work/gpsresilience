t = read.csv("4year_features/pace_features.csv")

x_vals = 1:600



day_subset = t[t$Weekday=="Wednesday" & t$Hour==9,]$M.M
day_subset = day_subset[day_subset > 0]
day_mean = mean(day_subset)
day_sd = sd(day_subset)

night_subset = t[t$Weekday=="Wednesday" & t$Hour==0,]$M.M
night_subset = night_subset[night_subset > 0]
night_mean = mean(night_subset)
night_sd = sd(night_subset)

svg("results/relative_prob_explanation.svg", 10, 6)

plot(x_vals, d_norm(x_vals, mean=day_subset, sd=day_sd), col="red", type="l", lwd=3
  main="Probability Density of Pace", xlab="Pace (sec/mi)")
lines(x_vals, d_norm(x_vals, mean=night_subset, sd=night_sd), col="blue", lwd=3)




dev.off()