# -*- coding: utf-8 -*-
"""
Created on Wed Mar 18 16:54:50 2015

@author: brian
"""
import csv

def parseTable(filename):
    with open(filename, 'r') as f:
        w = csv.reader(f)
        w.next()
        s = """\\begin{table}
\\centering
\\def\\arraystretch{2.5}
\\begin{tabular}{ccccc}
\\toprule
Event           & Start Time          & \\shortstack{Duration \\\\ (hours)} & \shortstack{Hours \\\\ Above \\\\ Thresh}    & \\shortstack{Max \\\\ (min/mi)}   \\\\
"""

        
        for [event,start_date,end_date,max_mahal,mahal_quant,duration,hours_above_thresh,max_pace_dev, min_pace_dev,worst_trip] in w:
            [d1,d2] = start_date.split(" ")            
            s += "%s & \\shortstack{%s \\\\ %s} & %s & %s & %s \\\\ \n" % (event, d1, d2, duration, hours_above_thresh, max_pace_dev)
        
        s += """\\bottomrule
\\end{tabular}
\\caption{blahblahblahcaption}
\\label{table:events}
\\end{table}
        """        
        
        print s
            

if(__name__=="__main__"):
    parseTable("results/events_labeled.csv")
    print
    print
    print"%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"
    print"%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"
    print"%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"
    print
    print
    parseTable("results/link_20_normalize_events_labeled.csv")
    