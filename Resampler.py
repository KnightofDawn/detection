# Resampler (version 2)

import os
import scipy.io
import scipy.signal
import numpy as np
from tkinter.filedialog import askdirectory

import time

dirpath = askdirectory()
if dirpath == '':
    print('Folder: None')
    exit()

newdir = askdirectory()

outfreq = 400

start = time.clock()

for dn in os.listdir(dirpath):
    dirstart = time.clock()
    fullpath = os.path.join(dirpath, dn)
    newpath = os.path.join(newdir, dn)
    if not os.path.isdir(newpath):
        os.mkdir(newpath)
    if "Store" not in dn:
        for fn in os.listdir(fullpath):
            fullname = os.path.join(fullpath, fn)
            newname = os.path.join(newpath, fn)
            f = scipy.io.loadmat(fullname)
            data = f['data']
            infreq = f['freq']
            
            newdata = np.ndarray((data.shape[0], outfreq))
            for i in range(0, len(data)):
                newdata[i] = scipy.signal.resample(data[i], outfreq)

            f['data'] = newdata
            f['freq'] = outfreq

            scipy.io.savemat(newname, f)
    print("Processed", dn, "in", time.clock() - dirstart, "seconds")

print("Processed all directories in", time.clock() - start, "seconds")
