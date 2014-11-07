from FeatureExplorer import *

import matplotlib.pyplot as plt
import scipy.io as sio
import numpy as np
import string
import time
import os

trainingdir = "E:/training results 5/"
testingdir = "E:/DATA/"
outputfile = "E:/testing results/training5.txt"
f = open(outputfile, 'w')

for dn in os.listdir(trainingdir):
    
    # load classified points
    ipoints = []
    epoints = []
    lpoints = []
    trainingpath = os.path.join(trainingdir, dn)
    if "Store" not in dn:
        for fn in os.listdir(trainingpath):
            if "test" not in fn:
                trainingfile = os.path.join(trainingpath, fn)
                point = sio.loadmat(trainingfile)
                if point['type'] == 'i':
                    ipoints.append(point['data'].tolist())
                elif point['type'] == 'e':
                    epoints.append(point['data'].tolist())
                elif point['type'] == 'l':
                    lpoints.append(point['data'].tolist())
                else:
                    print("Invalid point type.")
    
    # classify new points
    testingpath = os.path.join(testingdir, dn)
    print(testingpath)
    for fn in os.listdir(testingpath):
        if "test" in fn:
            print(fn)
            testname = os.path.join(testingpath, fn)
            PD, is_early = PeakDetect(testname)
            dCPD = difChannelPeakDeviation(testname)[0]
            #dPD = difPeakDetect(testname)
            BPF = TenTwentyBPF(testname)
    
            f1 = np.mean(PD)
            f2 = dCPD
            f3 = np.mean(BPF)
    
            point = [f1, f2, f3]
    
            i_neighbors = []
            for i in ipoints:
                dist = ((f1 - i[0][0])**2 + (f2 - i[0][1])**2 + (f3 - i[0][2])**2)**0.5
                i_neighbors.append(dist)
    
            e_neighbors = []
            for i in epoints:
                dist = ((f1 - i[0][0])**2 + (f2 - i[0][1])**2 + (f3 - i[0][2])**2)**0.5
                e_neighbors.append(dist)
    
            l_neighbors = []
            for i in lpoints:
                dist = ((f1 - i[0][0])**2 + (f2 - i[0][1])**2 + (f3 - i[0][2])**2)**0.5
                l_neighbors.append(dist)
    
            ins = sorted(i_neighbors)[:]
            while len(ins) < 10:
                ins.append(100)
            ens = sorted(e_neighbors)[:]
            while len(ens) < 10:
                ens.append(100)
            lns = sorted(l_neighbors)[:]
            while len(lns) < 10:
                lns.append(100)
    
            i = 0.0
            e = 0.0
            l = 0.0
    
            for j in range(0, 10):
                if ins[0] < ens[0]:
                    if ins[0] < lns[0]:
                        i += 1.0
                        ins.pop(0)
                    else:
                        l += 1.0
                        lns.pop(0)
                else:
                    if ens[0] < lns[0]:
                        e += 1.0
                        ens.pop(0)
                    else:
                        l += 1.0
                        lns.pop(0)
            
            ictal = 1.0 - i/10.0
            early = e/10.0
            f.write(fn)
            f.write(',')
            f.write("{0:.1f}".format(ictal))
            f.write(",{0:.1f}\n".format(early))

print("\nClassification complete.")
f.close()
            
    
    