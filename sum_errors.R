#Brian Donovan (briandonovan100@gmail.com)
#Sums all of the various types of errors over time and reports a summary

#Read the global features file
t = read.csv("../4year_features/global_features.csv")

#Data that is not necessarily an error, but is still not useful to the analysis
bad_data = sum(t$BAD_GPS) + sum(t$BAD_LO_STRAIGHTLINE) + sum(t$BAD_HI_STRAIGHTLINE) + sum(t$BAD_LO_DIST) +
	    sum(t$BAD_HI_DIST) + sum(t$BAD_LO_WIND) + sum(t$BAD_HI_WIND) + sum(t$BAD_LO_TIME) +
	    sum(t$BAD_HI_TIME) + sum(t$BAD_LO_PACE) + sum(t$BAD_HI_PACE)

#Data that is clearly an error
err_data = sum(t$ERR_GPS) + sum(t$ERR_LO_STRAIGHTLINE) + sum(t$ERR_HI_STRAIGHTLINE) + sum(t$ERR_LO_DIST) +
	    sum(t$ERR_HI_DIST) + sum(t$ERR_LO_WIND) + sum(t$ERR_HI_WIND) + sum(t$ERR_LO_TIME) +
	    sum(t$ERR_HI_TIME) + sum(t$ERR_LO_PACE) + sum(t$ERR_HI_PACE) + sum(t$ERR_OTHER)

#Bad months that need to be thrown away
err_date_data = sum(t$ERR_GPS)

#The good data
good_data = sum(t$VALID)

#Total number of trips
total = bad_data + err_data + err_date_data + good_data


#Print total trips and percent of various types of errors
print(paste("total", total))
print(paste("good data", good_data/total))
print(paste("bad data", bad_data/total))
print(paste("err data", err_data/total))
print(paste("err date data", err_date_data/total))
