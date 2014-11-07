# Written by Alex McMaster
"""The FeatureVisualizer.py script accepts a directory containing output files
from Trainer.py and plots each file as a point in 3D Cartesian space.  Features
are represented on the 3 axes, while segment class is represented by color as
follows:

Blue - Interictal
Yellow - Early ictal
Red - Late ictal"""

import matplotlib.pyplot as plt
import scipy.io as sio
import time
import os

# directory containing input files for all patients
dirpath = "E:/training results 5/"

# patient to plot
# can be set to "" to use all patients at once
patient = "Dog_1"

start = time.clock()

ipoints = [] # interictal points
epoints = [] # early ictal points
lpoints = [] # late ictal points

for dn in os.listdir(dirpath):
    dirstart = time.clock()
    fullpath = os.path.join(dirpath, dn)
    if patient in dn:
        for fn in os.listdir(fullpath):
            if "test" not in fn:
                
                # full path and filename of input file
                fullname = os.path.join(fullpath, fn)
                
                # create dict from input file
                point = sio.loadmat(fullname)
                
                # separate classes
                if point['type'] == 'i':
                    ipoints.append(point['data'].tolist())
                elif point['type'] == 'e':
                    epoints.append(point['data'].tolist())
                elif point['type'] == 'l':
                    lpoints.append(point['data'].tolist())
                else:
                    print("Invalid point type.")
    print("Processed", dn, "in", time.clock() - dirstart, "seconds.")

print("Processed all directories in", time.clock() - start, "seconds")

# create scatter plot and fill with data
fig = plt.figure()
axis = fig.add_subplot(111, projection='3d')
x = list(ipoints[i][0][0] for i in range(0, len(ipoints)))
y = list(ipoints[i][0][1] for i in range(0, len(ipoints)))
z = list(ipoints[i][0][2] for i in range(0, len(ipoints)))
axis.scatter(x, y, z, c='b')
x = list(epoints[i][0][0] for i in range(0, len(epoints)))
y = list(epoints[i][0][1] for i in range(0, len(epoints)))
z = list(epoints[i][0][2] for i in range(0, len(epoints)))
axis.scatter(x, y, z, c='y')
x = list(lpoints[i][0][0] for i in range(0, len(lpoints)))
y = list(lpoints[i][0][1] for i in range(0, len(lpoints)))
z = list(lpoints[i][0][2] for i in range(0, len(lpoints)))
axis.scatter(x, y, z, c='r')
xL = axis.set_xlabel('f1')
yL = axis.set_ylabel('f2')
zL = axis.set_zlabel('f3')
plt.show()
