t = read.csv("4year_features/pace_features.csv")

x_vals = 1:1000



day_subset = t[t$Weekday=="Wednesday" & t$Hour==12,]$M.M
day_subset = day_subset[day_subset > 0]
day_mean = mean(day_subset)
day_sd = sd(day_subset)

night_subset = t[t$Weekday=="Wednesday" & t$Hour==0,]$M.M
night_subset = night_subset[night_subset > 0]
night_mean = mean(night_subset)
night_sd = sd(night_subset)

svg("results/relative_prob_explanation.svg", 10, 6)

par(mfrow=c(2,1), mar=c(2,4,2,1))

plot(x_vals, dnorm(x_vals, mean=night_mean, sd=night_sd), col="blue", type="l", lwd=3,
  main="Probability Density of Pace (Midtown to Midtown)", xlab="Pace (sec/mi)", ylab="Probability Density")
lines(x_vals, dnorm(x_vals, mean=day_mean, sd=day_sd), col="red", lwd=3)
legend("topright", legend=c("12pm", "12am"), col=c("red", "blue"), lwd=3, cex=2)



max_day = dnorm(day_mean, mean=day_mean, sd=day_sd)
max_night = dnorm(night_mean, mean=night_mean, sd=night_sd)

plot(x_vals, dnorm(x_vals, mean=night_mean, sd=night_sd)/max_night, col="blue", type="l", lwd=3,
  main="Relative Probability Density of Pace (Midtown to Midtown)", xlab="Pace (sec/mi)", ylab="Relative Probability Density")
lines(x_vals, dnorm(x_vals, mean=day_mean, sd=day_sd)/max_day, col="red", lwd=3)
legend("topright", legend=c("12pm", "12am"), col=c("red", "blue"), lwd=3, cex=2)





dev.off()