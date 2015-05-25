Taxi GPS Data as Pervasive City-Scale Resilience Sensors
=============

##1)Overview

The code in this repository can be used to reproduce the results of paper "Using coarse GPS data to quantify city-scale transportation system resilience to extreme events" by Brian Donovan and Dan Work.  The purpose of this analysis is to extract meaningful information from large-scale taxi data, which can be downloaded [here](http://publish.illinois.edu/dbwork/open-data/).  Technically, the analysis processes the GPS data into two types of traffic estimates:
1. Origin-Destination Paces.  This represents the expected pace (minutes/mile) of vehicles between pairs of regions in the city.
2. Link-Level paces.  This represents the expected pace of vehicles driving over individual links in the road network.

Either of these traffic estimates can be used to detect outliers, using Robust PCA.  Further analysis identifies windows of time, or 'events' where there are a lot of outliers, using a hidden Markov model.

This library relies heavily on the [taxisim](https://github.com/Lab-Work/taxisim) library.  The **taxisim** library should be downloaded and placed inside the **gpsresilience** folder.  The recommended setup to instead place the **taxisim** folder next to the **gpsresilience** folder, then create a symbolic link to it inside the **gpsrresilience folder.

##2)License


This software is licensed under the *University of Illinois/NCSA Open Source License*:

**Copyright (c) 2013 The Board of Trustees of the University of Illinois. All rights reserved**

**Developed by: Department of Civil and Environmental Engineering University of Illinois at Urbana-Champaign**

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal with the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions: Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimers. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimers in the documentation and/or other materials provided with the distribution. Neither the names of the Department of Civil and Environmental Engineering, the University of Illinois at Urbana-Champaign, nor the names of its contributors may be used to endorse or promote products derived from this Software without specific prior written permission.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE CONTRIBUTORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS WITH THE SOFTWARE.








##3)How to Download the data

The dataset used in our analysis is made publicly available [here](http://publish.illinois.edu/dbwork/open-data/).  This dataset contains record of almost 700 million taxi trips in New York City between 2010 and 2013 (inclusive).  Included information:
- GPS coordinates for pickup and dropoff
- Date and time for pickup and dropoff
- Metered Distance
- Driver and car ID

All of this data should be downloaded and placed in a folder called "new_chron".  This folder is placed NEXT TO the gpsresilience folder, not inside it.  So, at this point the directory tree should look something like:
<pre>
<code>
.
|-- gpsresilience
|   |-- taxisim/
|   |-- eventDetection.py
|   |-- extractRegionFeaturesParallel.py
|   |-- ...
`-- new_chron
    |-- fix2011.py
    |-- FOIL2010
    |   |-- trip_fare_1.csv
    |   |-- trip_fare_2.csv
    |   |-- trip_fare_3.csv
    |   |-- trip_fare_4.csv
    |   |-- ...
    |-- FOIL2011
    |   |-- ...
    |-- FOIL2012
    |   |-- ...
    |-- FOIL2013
    |   |-- ...
    `-- header
</code>
</pre>
 
##4) How to run the Code
The code needs to be run in a specific order, since the results of each step depend on the results of the previous step.  This section describes the proper order.  Since two methods of analysis are possible (link-level and origin-destination), they are described separately.

###**Link-Level Method**
This method identifies travel times on each link of the road network.  Then, the periodic patterns are used to identify outliers and the events that cause them.  The code is run as follows:
1. Run **taxisim.mpi_parallel.test_traffic_estimation.run_test()**.  This produces the link-level traffic estimates and saves them into a PostgreSQL database.  This is a heavy computation if it is applied to many hours of traffic data.  On our dataset, it took roughly 1-2 hours to compute the estimates for one hour of traffic data.  Since we applied it to a 4-year dataset, supercomputing resources were required.  This is why the code is an mpi program instead of a standard program.  If you just need the traffic estimates for NYC, and you don't want to re-run this step, you can just download the data [here](www.ihaventuploadedthedatayet.com).
2. Run **measureLinkOutliers.py** .  This takes the traffic estimates from the previous section and identifies the links that consistently have trips on them (i.e. they don't have very much missing data).  The traffic estimates on these links only are placed into Numpy vectors - one vector for each hour of estimates, each dimension corresponds to a different link.  These vectors are organised into groups based on the weekly periodic pattern.  There are **24x7=168** groups.  This organised data is dumped into a large pickle file called **tmp_vectors.pickle** file so it can be re-used later without accessing the database.
3. Run **measureOutliers.py** .  Inside the main section <code>if(__name__=="__main__"):</code> , ensure that the lines labled "This performs the link-level analysis" are uncommented. This portion of the analysis examines each group independently and uses Robust PCA to identify outliers.  Each hour is assigned outlier scores, based on their similarity to other hours in the same group.  These results are saved in a file such as **link_features_imb20_k10_RPCAtune_10000000pcs_5percmiss_robust_outlier_scores.csv**.
4. Run **hmm_event_detection.py** .  This takes the outlier scores from the previous section and identifies windows of time with lots of outliers, and tags those as events.  It produces two files as output:
    i. **fine_events_scores.csv** - This is identical to **link_features_imb20_k10_RPCAtune_10000000pcs_5percmiss_robust_outlier_scores.csv** except that it contains an additional column with the binary event flags.  I.e. 1 for event, 0 for not event.
    ii. **fine_events.csv** - A list of the detected events and their dates, durations, peak behavior, etc.

###**Origin-Destination Method**



