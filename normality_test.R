library(psych)
t = read.csv("4year_features/pace_features.csv")


pdf("log_normality_test.pdf", 10, 10)
for(weekday in c('Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday')){
  for(hour in 0:23){
    par(mfrow=c(2,2))
    print(paste(weekday, hour))
    s = t[t$Weekday==weekday & t$Hour==hour,]
    good_data = s[apply(s[,4:19] > 0, 1, sum) ==16,4:19]
    good_data = log(good_data)


    mu = colMeans(good_data)
    sigma = cov(good_data)

    d2 = mahalanobis(good_data, center=mu, cov=sigma)

    plot(density(d2, bw=1), main=paste("KDE of Squared Mahal", weekday, hour))
    rug(d2)
    chipoints = qchisq(ppoints(length(d2)), df=16)
    qqplot(chipoints, d2, main=paste("Chi^2-ness of Squared Mahal", weekday, hour))
    abline(0,1, lwd=2, col="blue")
    
    
    trimmed_data = good_data[d2 < quantile(d2, probs=.9),]
    mu = colMeans(trimmed_data)
    sigma = cov(trimmed_data)

    d2 = mahalanobis(trimmed_data, center=mu, cov=sigma)
    
    plot(density(d2, bw=1), main=paste("Trimmed KDE of Squared Mahal", weekday, hour))
    rug(d2)
    chipoints = qchisq(ppoints(length(d2)), df=16)
    qqplot(chipoints, d2, main=paste("Trimmed Chi^2-ness of Squared Mahal", weekday, hour))
    abline(0,1, lwd=2, col="blue")
    

    

  }
}
dev.off()

