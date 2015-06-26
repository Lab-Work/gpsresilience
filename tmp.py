from datetime import datetime, timedelta
from db_functions import db_main, db_trip

db_main.connect('db_functions/database.conf')


dates = [datetime(2012,4,18,h) for h in range(24)]
s = ""
for d in dates:
    end = d + timedelta(hours=1)
    trips = db_trip.find_pickup_dt(d,end)
    total_dur = sum([trip.time for trip in trips])
    avg_dur = float(total_dur) / len(trips)
    print(avg_dur)
    s = s + "%f,"%avg_dur


print(s)
