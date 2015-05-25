# -*- coding: utf-8 -*-
"""
Created on Wed Mar 18 16:54:50 2015

@author: brian
"""
import csv

def parseTable(filename, max_events=10):
    with open(filename, 'r') as f:
        w = csv.reader(f)
        w.next()
        s = """\\begin{table}
\\centering
\\caption{blahblahblahcaption}
\\label{table:events}
\\begin{tabular}{ccccc}
\\hline
Event           & Start Time          & \\shortstack{Duration \\\\ (hours)}  & \\shortstack{Max \\\\ (min/mi)}   \\\\
"""

        i = 0
        for [event,start_date,end_date,duration,max_mahal,max_pace_dev,min_pace_dev] in w:
            [d1,d2] = start_date.split(" ")            
            s += "%s & \\shortstack{%s \\\\ %s} & %s & %s \\\\ \n" % (event, d1, d2, duration, max_pace_dev)
            i += 1
            if(i>= max_events):
                break
        
        s += """\\hline
\\end{tabular}
\\end{table}
        """        
        
        print s
            

if(__name__=="__main__"):
    parseTable("results/coarse_events.csv")
    print
    print
    print"%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"
    print"%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"
    print"%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"
    print
    print
    parseTable("results/fine_events.csv")
    