"""The Trainer.py script performs feature detection on a set of training data
 by iteratint through a folder of .mat files containing EEG data and extracting
 the following features:

- peak voltage
- standard deviation of peak channel voltages following a first difference
    NOTE: replace std dev w/ IQR
- signal energy following a bandpass between 10 and 20 Hz

An output file is created for each segment containing a value for each feature
and the segment's class.  These files are used for classification of new
segments by Classifier.py."""

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

# location of .mat files
dirpath = "E:/DATA/"

# destination for output files
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
                
                # full path and filename of input file
                fullname = os.path.join(fullpath, fn)
                
                # full path and filename of output file
                newname = os.path.join(newpath, str.replace(fn, 'segment', 'point'))
                
                # detect feature for each channel
                PD, early = PeakDetect(fullname)
                dCPD = difChannelPeakDeviation(fullname)[0]
                BPF = TenTwentyBPF(fullname)
                
                # take mean of channel values (dCPD is already std dev of channel
                # values, so only contains one value)
                #   NOTE: use median instead of mean
                f1 = np.mean(PD)
                f2 = dCPD
                f3 = np.mean(BPF)
                
                data = [f1, f2, f3]
                
                # get segment class                
                if "interictal" in fn:
                    typ = "i"
                else:
                    if early:
                        typ = 'e'
                    else:
                        typ = 'l'
                        
                # create dict for output file
                point = {'data':data, 'type':typ}
                
                # save dict as a .mat file
                sio.savemat(newname, point)
                
    print("Processed", dn, "in", time.clock() - dirstart, "seconds.")

print("Processed all directories in", time.clock() - start, "seconds")
