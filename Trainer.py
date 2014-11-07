from FeatureExplorer import PeakDetect
from FeatureExplorer import difChannelPeakDeviation
from FeatureExplorer import difPeakDetect
from FeatureExplorer import TenTwentyBPF
from FeatureExplorer import TenThirtyBPFLL

import matplotlib.pyplot as plt
import scipy.io as sio
import numpy as np
import string
import time
import os

dirpath = "E:/DATA/"
newdir = "E:/training results 5/"
if not os.path.isdir(newdir):
    os.mkdir(newdir)

start = time.clock()

for dn in os.listdir(dirpath):
    dirstart = time.clock()
    fullpath = os.path.join(dirpath, dn)
    newpath = os.path.join(newdir, dn)
    if not os.path.isdir(newpath):
        os.mkdir(newpath)
    if 'Store' not in dn:
        for fn in os.listdir(fullpath):
            if "test" not in fn:
                fullname = os.path.join(fullpath, fn)
                newname = os.path.join(newpath, str.replace(fn, 'segment', 'point'))
                PD, early = PeakDetect(fullname)
                dCPD = difChannelPeakDeviation(fullname)[0]
                #dPD = difPeakDetect(fullname)
                BPF = TenTwentyBPF(fullname)
                
                f1 = np.mean(PD)
                
                f2 = dCPD
                
                f3 = np.mean(BPF)
                
                data = [f1, f2, f3]
                if "interictal" in fn:
                    typ = "i"
                else:
                    if early:
                        typ = 'e'
                    else:
                        typ = 'l'
                point = {'data':data, 'type':typ}
                sio.savemat(newname, point)
    print("Processed", dn, "in", time.clock() - dirstart, "seconds.")

print("Processed all directories in", time.clock() - start, "seconds")
