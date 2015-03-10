# [1] "Date"                "Hour"                "Weekday"            
# [4] "Count"               "Pace"                "Miles"              
# [7] "Drivers"             "AvgWind"             "SdWind"             
#[10] "VALID"               "BAD_GPS"             "ERR_GPS"            
#[13] "BAD_LO_STRAIGHTLINE" "BAD_HI_STRAIGHTLINE" "ERR_LO_STRAIGHTLINE"
#[16] "ERR_HI_STRAIGHTLINE" "BAD_LO_DIST"         "BAD_HI_DIST"        
#[19] "ERR_LO_DIST"         "ERR_HI_DIST"         "BAD_LO_WIND"        
#[22] "BAD_HI_WIND"         "ERR_LO_WIND"         "ERR_HI_WIND"        
#[25] "BAD_LO_TIME"         "BAD_HI_TIME"         "ERR_LO_TIME"        
#[28] "ERR_HI_TIME"         "BAD_LO_PACE"         "BAD_HI_PACE"        
#[31] "ERR_LO_PACE"         "ERR_HI_PACE"         "ERR_DATE"           
#[34] "ERR_OTHER"  

t = read.csv("../4year_features/global_features.csv")

bad_data = sum(t$BAD_GPS) + sum(t$BAD_LO_STRAIGHTLINE) + sum(t$BAD_HI_STRAIGHTLINE) + sum(t$BAD_LO_DIST) +
	    sum(t$BAD_HI_DIST) + sum(t$BAD_LO_WIND) + sum(t$BAD_HI_WIND) + sum(t$BAD_LO_TIME) +
	    sum(t$BAD_HI_TIME) + sum(t$BAD_LO_PACE) + sum(t$BAD_HI_PACE)


err_data = sum(t$ERR_GPS) + sum(t$ERR_LO_STRAIGHTLINE) + sum(t$ERR_HI_STRAIGHTLINE) + sum(t$ERR_LO_DIST) +
	    sum(t$ERR_HI_DIST) + sum(t$ERR_LO_WIND) + sum(t$ERR_HI_WIND) + sum(t$ERR_LO_TIME) +
	    sum(t$ERR_HI_TIME) + sum(t$ERR_LO_PACE) + sum(t$ERR_HI_PACE) + sum(t$ERR_OTHER)

err_date_data = sum(t$ERR_GPS)

good_data = sum(t$VALID)


total = bad_data + err_data + err_date_data + good_data
print(paste("total", total))
print(paste("good data", good_data/total))
print(paste("bad data", bad_data/total))
print(paste("err data", err_data/total))
print(paste("err date data", err_date_data/total))
