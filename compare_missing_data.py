import csv



def allZero(v):
    for x in v:
        if(x!=0):
            return False
    return True




k_vals = [1,2,3,4,5,6,7,8,9,10,15,20,25,30,35,40,45,50]
k_vals = [1,2,3,4,5,6,7,8,9,10,15,20,25]





with open('results/regions_missing_data.csv', 'w') as f1:
    w = csv.writer(f1)
    w.writerow(['num_regions', 'dimension', 'dimension_frac', 'perc_missing'])
    for k in k_vals:
        filename = "features_imb20_k%d/pace_features.csv" % k
        print("reading %s" % filename)
        with open(filename, 'r') as f2:
            r = csv.reader(f2)
            _=r.next()
            del(_)
            
            data_counts = None
            total_rows = 0
            for line in r:
                features = map(float, line[3:])
                
                if(not allZero(features)):
                    if(data_counts==None):
                        data_counts = [0 for v in features]
                    
                    for i in xrange(len(features)):
                        if(features[i]!=0):
                            data_counts[i] += 1
                    
                    total_rows += 1
            
        perc_missing = [1 - float(count)/total_rows for count in data_counts]
        perc_missing.sort()
        
        for i in xrange(len(perc_missing)):
            line= [k,i, float(i)/len(perc_missing), perc_missing[i]]
            w.writerow(line)
    