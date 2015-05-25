# -*- coding: utf-8 -*-
"""
Created on Thu Apr  9 10:21:13 2015

@author: Brian Donovan (briandonovan100@gmail.com)
"""
import csv

LOG_FN = "out_measure_outliers.txt"
OUT_FN = 'eigen_counts.csv'

with open(LOG_FN, 'r') as f:
    with open(OUT_FN, 'w') as of:
        w = csv.writer(of)
        w.writerow(['gamma', 'num_eigen'])
        current_gamma = 0
        for line in f:
            if('gamma' in line):
                current_gamma = float(line.split('gamma=')[1].split(',')[0])
                
            if('Nonzero' in line):
                ev = int(line.split(': ')[1])
                w.writerow([current_gamma, ev])
        