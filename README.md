Taxi GPS Data as Pervasive City-Scale Resilience Sensors
=============

#1)Overview

The code in this repository can be used to reproduce the results of paper "Using coarse GPS data to quantify city-scale transportation system resilience to extreme events" by Brian Donovan and Dan Work.  The purpose of this analysis is to extract meaningful information from large-scale taxi data, which can be downloaded [here](https://uofi.box.com/s/zmggziub40wx1bq2h9bq).


#2)License


This software is licensed under the *University of Illinois/NCSA Open Source License*:

**Copyright (c) 2013 The Board of Trustees of the University of Illinois. All rights reserved**

**Developed by: Department of Civil and Environmental Engineering University of Illinois at Urbana-Champaign**

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal with the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions: Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimers. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimers in the documentation and/or other materials provided with the distribution. Neither the names of the Department of Civil and Environmental Engineering, the University of Illinois at Urbana-Champaign, nor the names of its contributors may be used to endorse or promote products derived from this Software without specific prior written permission.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE CONTRIBUTORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS WITH THE SOFTWARE.


#3)How to Run the Code

**Step 1 - Download the data**
The dataset used in our analysis is made publicly available [here](https://uofi.box.com/s/zmggziub40wx1bq2h9bq).  This dataset contains record of almost 700 million taxi trips in New York City between 2010 and 2013 (inclusive).  Included information:
- GPS coordinates for pickup and dropoff
- Date and time for pickup and dropoff
- Metered Distance
- Driver and car ID

All of this data should be downloaded and placed in a folder called "new_chron".  This folder is placed NEXT TO the gpsresilience folder, not inside it.  So, at this point the directory tree should look something like:
.
├── gpsresilience
│   ├── eventDetection.py
│   ├── extractGridFeaturesParallel.py
│   ├── featureHistograms.py
│   ├── likelihood_test_parallel.py
│   ├── ...
│   ├── results
│   │   └── ...
└── new_chron
    ├── fix2011.py
    ├── FOIL2010
    │   ├── trip_fare_1.csv
    │   ├── ...
    ├── FOIL2011
    │   ├── trip_fare_1.csv
    │   ├── ...
    ├── FOIL2012
    │   ├── trip_fare_1.csv
    │   ├── ...
    └── FOIL2013
        ├── trip_fare_1.csv
        └── ...


