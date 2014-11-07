# Written by Kent Leyde
"""
FeatureExplorer.py(): This script runs candidate features on selected ictal
and interictal files and plots results in histograms.

The process begins by selecting a subject directory.

Once a subject directory has been selected, the ictal and interictal training files 
are processed. The results are collected in histograms.  The ictal results are divided by 
the included "latency" variable and plotted in two separate histograms.
 
Channels showing the ability to discriminate between ictal/interictal and
early ictal/late ictal may be identified by the user.  
Channel identification information is stored in a <patientID>.mat file. 
"""

import os
import re

import tkinter as tk
from tkinter import *
from tkinter.ttk import *
from tkinter.filedialog import askdirectory

import numpy as np
import scipy.io as spio
import matplotlib.pyplot as plt
 
    
#####################################################################################
# Feature Explorer UI Class
#####################################################################################
class FExplorer(tk.Tk):
    
    #################################################################################
    # Class constructor
    #################################################################################
    def __init__(self,parent=None):
        tk.Tk.__init__(self)
        self.parent = parent
        self.InitUI()
       
    #################################################################################
    # InitUI() function, called by class constructor
    #################################################################################
    def InitUI(self):
        # Initialize some shared variables
        self.DirPath = ''                               #Contains path to the folder that stores all the input files
        
        self.SelectedFeature = tk.StringVar()           #Contains name of selected feature

        self.EarlyIctalFeatures=[]                      #List containing feature outputs from early ictal files. Rows correspond to input files, columns to channels
        self.LateIctalFeatures=[]                       #List containing feature outputs from late ictal files. Rows correspond to input files, columns to channels
        self.InterictalFeatures=[]                      #List containing feature outputs from interictal files. Rows correspond to input files, columns to channels  
        
        # Configure the main window and frame
        self.title('Feature Explorer')
        self.mainframe = tk.ttk.Frame(self, padding='20 20 30 30')
        self.mainframe.grid(column=0, row=0,sticky=(N,W,E,S))
        self.mainframe.columnconfigure(0, weight=1)
        self.mainframe.rowconfigure(0, weight=1)    

        # Add objects to main frame
        self.SFButton = tk.ttk.Button(self.mainframe, text="Select Folder...", command=self.SelectFolder)
        self.SFButton.grid(row=0, column=0, sticky=W) 
        self.SFLabel = tk.ttk.Label(self.mainframe, text='Folder: None')
        self.SFLabel.grid(row=0, column=1, sticky=W)

        self.FSCombo = tk.ttk.Combobox(self.mainframe, textvariable=self.SelectedFeature)
        self.FSCombo['values'] = ('Peak Detect', '10-20Hz BPF', '10-20Hz Upslope', '10-20Hz Downslope', '10-30Hz Line Length', '20-30Hz Line Length', 'Difference Peak', 'Difference 10-20Hz Line Length', 'Channel Peak Deviation', 'Difference Channel Peak Deviation')
        self.FSCombo.current(0)
        self.FSCombo.grid(row=1, column=0, sticky=W)
               
        self.CFButton = tk.ttk.Button(self.mainframe, text="Calc Features...", command=self.CalcFeatures)
        self.CFButton.grid(row=2, column=0, sticky=W)
          
        self.PRButton = tk.ttk.Button(self.mainframe, text="Plot Results...", command=self.PlotResults)
        self.PRButton.grid(row=3, column=0, sticky=W)  
 
        #################################################################################
        # Shared Variables
        #################################################################################
                  
   


    #################################################################################
    # Event Handlers
    #################################################################################
    
    #
    # SelectFolder()
    # Select the folder containing the input files.  Input files are one-second clip of data as well as metadata
    #
    def SelectFolder(self):
            print('Entering SelectFolder()')
            self.DirPath=askdirectory()
            if self.DirPath == '':
                print('Folder: None')
                exit()
            # Display the folder selection
            self.SFLabel['text']='Folder: ', self.DirPath
     

            # Open the first ictal file then retreive some basic info about the files
            reIctal=re.compile('_ictal_segment_1.mat+')
            for FileName in os.listdir(self.DirPath):
                if reIctal.search(FileName):
                    FullPath = os.path.join(self.DirPath, FileName)
                    
                    TempClipData = spio.loadmat(FullPath)     
                    TempDataArray = TempClipData['data']
                    TempDataArray = TempDataArray.transpose()
                    self.LastChan = int(TempDataArray.shape[1])     #Last channel number
                    self.Channels = np.arange(0, self.LastChan,1)   #List of channels                 
    #
    # CalcFeatures(): Calculate features for all files in selected folder. 
    # Process the early ictal, late ictal, and interictal files separately so that the results can be grouped for histogram plotting
    #
    def CalcFeatures(self):
            print('Entering CalcFeatures()')

            # Compile search expressions for finding files
            reIctal=re.compile('_ictal+')
            reInterIctal=re.compile('_interictal+')

            # Initialize lists used to hold histogram data. Columns correspond to channels, rows correspond to input data files
            self.EarlyIctalFeatures=[]
            self.LateIctalFeatures=[]
            self.InterictalFeatures=[]

            # Iterate through interictal files
            for FileName in os.listdir(self.DirPath):
                if reInterIctal.search(FileName):
                    FullPath = os.path.join(self.DirPath, FileName)
                    #print('Processing interictal file: ', FileName)
                    print('I', end="", flush=True)
                    FeatureVector=ExtractFeature(self.FSCombo.get(), FullPath)
                    self.InterictalFeatures.append(FeatureVector)
            
            # Iterate through ictal files, handle the early ictal and late ictal separately
            for FileName in os.listdir(self.DirPath):
                if reIctal.search(FileName):
                    FullPath = os.path.join(self.DirPath, FileName)
                    TempClipData = spio.loadmat(FullPath)
                    Latency = float(TempClipData['latency'])    #Latency of ictal segment (time from sz start)
                    #print('Processing ictal file: ', FileName, 'Latency is: ', Latency)
                    if Latency<=16.0:
                        #print('Found an early ictal file...')
                        print('E', end="", flush=True)
                        FeatureVector=ExtractFeature(self.FSCombo.get(), FullPath)
                        self.EarlyIctalFeatures.append(FeatureVector)
                    else:
                        #print('Processing a later ictal file...')
                        print('L', end="", flush=True)
                        FeatureVector=ExtractFeature(self.FSCombo.get(), FullPath)
                        self.LateIctalFeatures.append(FeatureVector)

            print(' ')
            print('Feature extraction complete')



    #    
    # PlotResults(): Plot histograms of the feature outputs
    #
    def PlotResults(self):
            print('Entering PlotResults()')
            # Convert the feature lists to ndarrays
            EIFeatures = np.array(self.EarlyIctalFeatures)
            LIFeatures = np.array(self.LateIctalFeatures)
            IIFeatures = np.array(self.InterictalFeatures)
            
            plt.close('all')

            fig, axarr = plt.subplots(self.LastChan,1,sharex='col')  #Create an axis object with LastChan+1 rows, 1 column; select plot #1
            
            for i in self.Channels:
                axarr[i].hist(IIFeatures[:,i], 50, normed=1, histtype='stepfilled', alpha=0.5, label='II')
                axarr[i].hist(EIFeatures[:,i], 50, normed=1, histtype='stepfilled', alpha=0.5, label='EI')
                axarr[i].hist(LIFeatures[:,i], 50, normed=1, histtype='stepfilled', alpha=0.5, label='LI')
            
            plt.legend(loc='upper right')
            fig.suptitle(('Directory: '+self.DirPath+'  Feature: '+self.FSCombo.get()))
           
            plt.show()


#####################################################################################
# Feature Extractors
# These functions are passed a string containing the path to an input clip file.
# The function will then calculate feature values for each channel.  The values
# are returned as a list variable.
#####################################################################################

#
# ExtractFeature()
# Call the correct feature extractor and return its results
def ExtractFeature(FEName, FullPath):
    if FEName == 'Peak Detect':
        return(PeakDetect(FullPath))
    elif FEName == '10-20Hz BPF':
        return(TenTwentyBPF(FullPath))
    elif FEName == '10-20Hz Upslope':
        return(TenTwentyUpslopeBPF(FullPath))
    elif FEName == '10-20Hz Downslope':
        return(TenTwentyDownslopeBPF(FullPath))
    elif FEName == '10-30Hz Line Length':
        return(TenThirtyBPFLL(FullPath))
    elif FEName == '20-30Hz Line Length':
        return(TwentyThirtyBPFLL(FullPath))
    elif FEName == 'Difference Peak':
        return(difPeakDetect(FullPath))
    elif FEName == 'Difference 10-20Hz Line Length':
        return(difTenTwentyBPFLL(FullPath))
    elif FEName == 'Channel Peak Deviation':
        return(ChannelPeakDeviation(FullPath))
    elif FEName == 'Difference Channel Peak Deviation':
        return(difChannelPeakDeviation(FullPath))
    else:
        print('No valid feature selected!')


#
# bender()
# Quick and dirty limiting function modeled after sigmoid function
def bender(x,mean,span):
    out = 1.0/(1.0+np.exp(-3.3*(x-mean)/span))
    return(out)


#
# PeakDetect()
# This feature detector does a peak detect
def PeakDetect(FullPath):
    #print('Entering PeakDetect()')
    TempClipData = spio.loadmat(FullPath)
    TempDataArray = TempClipData['data']
    TempDataArray = TempDataArray.transpose()

    Fsample = float(TempClipData['freq'])       #Sampling frequency
    dt = 1.0/Fsample                            #Time between samples
    TimeValues = np.arange(0.0, 1.0, dt)        #Construct ndarray of time values
    LastChan = int(TempDataArray.shape[1])      #Last channel number
    Channels = np.arange(0, LastChan,1)         #List of channel numbers
    
    FeatureOutput = np.zeros(LastChan)          #Initialize the output

    # Calculate the feature values for each channel       
    for i in Channels:
        #FeatureOutput[i]=TempDataArray[:,i].max()
        FeatureOutput[i]=np.log10(TempDataArray[:,i].max()*TempDataArray[:,i].max())
        FeatureOutput[i] = bender(FeatureOutput[i], 4.8, 3.0)               #Limit to range of 0 to 1.  Second arg is mean, third is span 
        
    FeatureList = FeatureOutput.tolist()        #Convert ndarray to list.  The returned value will be appended other values; this would be very inefficent with ndarray

    early = 0
    if 'latency' in TempClipData.keys():
        if TempClipData['latency'] < 16:
            early = 1
    
    #Return feature vector in form of a list
    return(FeatureList, early)


#
# TenTwentyBPF()
# This feature detects energy in the 10-20Hz band
def TenTwentyBPF(FullPath):
    #print('Entering TenTwentyBPF()')
    TempClipData = spio.loadmat(FullPath)
    TempDataArray = TempClipData['data']
    TempDataArray = TempDataArray.transpose()

    Fsample = float(TempClipData['freq'])       #Sampling frequency
    dt = 1.0/Fsample                            #Time between samples
    TimeValues = np.arange(0.0, 1.0, dt)        #Construct ndarray of time values
    LastChan = int(TempDataArray.shape[1])      #Last channel number
    Channels = np.arange(0, LastChan,1)         #List of channel numbers
    
    FeatureOutput = np.zeros(LastChan)          #Initialize the output 

    # Read in the digital filter coeficients and place in ndarrays
    FilterInfo=spio.loadmat('FilterSetTenTwentyBPF.mat')

    FilterCoefI = FilterInfo['FilterCoefI'].flatten()
    FilterCoefQ = FilterInfo['FilterCoefQ'].flatten()

    # Calculate the feature values for each channel       
    for i in Channels:
        Iproduct = FilterCoefI*TempDataArray[:,i]
        Isum=np.sum(Iproduct[i])
        
        Qproduct = FilterCoefQ*TempDataArray[:,i]
        Qsum=np.sum(Qproduct)
        
        FeatureOutput[i] = np.log( np.sqrt(Isum*Isum + Qsum*Qsum) )
        FeatureOutput[i] = bender(FeatureOutput[i], 3.0, 8.0)               #Limit to range of 0 to 1.  Second arg is mean, third is span      

    FeatureList = FeatureOutput.tolist()        #Convert ndarray to list.  The returned value will be appended other values; this would be very inefficent with ndarray

    #Return feature vector in form of a list
    return(FeatureList)


#
# TenTwentyUpslopeBPF()
# This feature detects energy in the 10-20Hz band, filter slopes-up with frequency
def TenTwentyUpslopeBPF(FullPath):
    TempClipData = spio.loadmat(FullPath)
    TempDataArray = TempClipData['data']
    TempDataArray = TempDataArray.transpose()

    Fsample = float(TempClipData['freq'])       #Sampling frequency
    dt = 1.0/Fsample                            #Time between samples
    TimeValues = np.arange(0.0, 1.0, dt)        #Construct ndarray of time values
    LastChan = int(TempDataArray.shape[1])      #Last channel number
    Channels = np.arange(0, LastChan,1)         #List of channel numbers
    
    FeatureOutput = np.zeros(LastChan)          #Initialize the output 

    # Read in the digital filter coeficients and place in ndarrays
    FilterInfo=spio.loadmat('FilterSetTenTwentyUpslopeBPF.mat')

    FilterCoefI = FilterInfo['FilterCoefI'].flatten()
    FilterCoefQ = FilterInfo['FilterCoefQ'].flatten()

    # Calculate the feature values for each channel       
    for i in Channels:
        Iproduct = FilterCoefI*TempDataArray[:,i]
        Isum=np.sum(Iproduct[i])
        
        Qproduct = FilterCoefQ*TempDataArray[:,i]
        Qsum=np.sum(Qproduct)
        
        FeatureOutput[i] = np.log( np.sqrt(Isum*Isum + Qsum*Qsum) )
        FeatureOutput[i] = bender(FeatureOutput[i], 3.0, 6.0)               #Limit to range of 0 to 1.  Second arg is mean, third is span      

    FeatureList = FeatureOutput.tolist()        #Convert ndarray to list.  The returned value will be appended other values; this would be very inefficent with ndarray

    #Return feature vector in form of a list
    return(FeatureList)


#
# TenTwentyDownslopeBPF()
# This feature detects energy in the 10-20Hz band, filter slopes-down with frequency
def TenTwentyDownslopeBPF(FullPath):
    TempClipData = spio.loadmat(FullPath)
    TempDataArray = TempClipData['data']
    TempDataArray = TempDataArray.transpose()

    Fsample = float(TempClipData['freq'])       #Sampling frequency
    dt = 1.0/Fsample                            #Time between samples
    TimeValues = np.arange(0.0, 1.0, dt)        #Construct ndarray of time values
    LastChan = int(TempDataArray.shape[1])      #Last channel number
    Channels = np.arange(0, LastChan,1)         #List of channel numbers
    
    FeatureOutput = np.zeros(LastChan)          #Initialize the output 

    # Read in the digital filter coeficients and place in ndarrays
    FilterInfo=spio.loadmat('FilterSetTenTwentyDownslopeBPF.mat')

    FilterCoefI = FilterInfo['FilterCoefI'].flatten()
    FilterCoefQ = FilterInfo['FilterCoefQ'].flatten()

    # Calculate the feature values for each channel       
    for i in Channels:
        Iproduct = FilterCoefI*TempDataArray[:,i]
        Isum=np.sum(Iproduct[i])
        
        Qproduct = FilterCoefQ*TempDataArray[:,i]
        Qsum=np.sum(Qproduct)
        
        FeatureOutput[i] = np.log( np.sqrt(Isum*Isum + Qsum*Qsum) )
        FeatureOutput[i] = bender(FeatureOutput[i], 4.0, 4.0)               #Limit to range of 0 to 1.  Second arg is mean, third is span      

    FeatureList = FeatureOutput.tolist()        #Convert ndarray to list.  The returned value will be appended other values; this would be very inefficent with ndarray

    #Return feature vector in form of a list
    return(FeatureList)


#
# TenThirtyBPFLL()
# This feature filters in the 10-30Hz band then computes line length. Filter is 100 pts long.
def TenThirtyBPFLL(FullPath):
    TempClipData = spio.loadmat(FullPath)
    TempDataArray = TempClipData['data']
    TempDataArray = TempDataArray.transpose()

    Fsample = float(TempClipData['freq'])       #Sampling frequency
    dt = 1.0/Fsample                            #Time between samples
    TimeValues = np.arange(0.0, 1.0, dt)        #Construct ndarray of time values
    LastChan = int(TempDataArray.shape[1])      #Last channel number
    Channels = np.arange(0, LastChan,1)         #List of channel numbers
    
    FeatureOutput = np.zeros(LastChan)          #Initialize the output 

    # Read in the digital filter coeficients and place in ndarrays
    FilterInfo=spio.loadmat('FilterSetTenThirtyBPF.mat')

    FilterCoefI = FilterInfo['FilterCoefI'].flatten()
    FilterCoefQ = FilterInfo['FilterCoefQ'].flatten()
    
    ILineLength=0.0
    QLineLength=0.0

    # Calculate the feature values for each channel       
    for i in Channels:
        Ifilt = np.convolve(FilterCoefI, TempDataArray[:,i])     
        Qfilt = np.convolve(FilterCoefQ, TempDataArray[:,i])
        
        
        for j in range (1, Ifilt.size):
            ILineLength = np.abs(Ifilt[j]-Ifilt[j-1])
            QLineLength = np.abs(Qfilt[j]-Qfilt[j-1])
        
        FeatureOutput[i] = np.log10(ILineLength+QLineLength)
        FeatureOutput[i] = bender(FeatureOutput[i], -3.5, 3.0)               #Limit to range of 0 to 1.  Second arg is mean, third is span      

    FeatureList = FeatureOutput.tolist()        #Convert ndarray to list.  The returned value will be appended other values; this would be very inefficent with ndarray

    #Return feature vector in form of a list
    return(FeatureList)


#
# TwentyThirtyBPFLL()
# This feature filters in the 20-30Hz band then computes line length. Filter is 100 pts long.
def TwentyThirtyBPFLL(FullPath):
    TempClipData = spio.loadmat(FullPath)
    TempDataArray = TempClipData['data']
    TempDataArray = TempDataArray.transpose()

    Fsample = float(TempClipData['freq'])       #Sampling frequency
    dt = 1.0/Fsample                            #Time between samples
    TimeValues = np.arange(0.0, 1.0, dt)        #Construct ndarray of time values
    LastChan = int(TempDataArray.shape[1])      #Last channel number
    Channels = np.arange(0, LastChan,1)         #List of channel numbers
    
    FeatureOutput = np.zeros(LastChan)          #Initialize the output 

    # Read in the digital filter coeficients and place in ndarrays
    FilterInfo=spio.loadmat('FilterSetTwentyThirtyBPF.mat')

    FilterCoefI = FilterInfo['FilterCoefI'].flatten()
    FilterCoefQ = FilterInfo['FilterCoefQ'].flatten()
    
    ILineLength=0.0
    QLineLength=0.0

    # Calculate the feature values for each channel       
    for i in Channels:
        Ifilt = np.convolve(FilterCoefI, TempDataArray[:,i])     
        Qfilt = np.convolve(FilterCoefQ, TempDataArray[:,i])
        
        
        for j in range (1, Ifilt.size):
            ILineLength = np.abs(Ifilt[j]-Ifilt[j-1])
            QLineLength = np.abs(Qfilt[j]-Qfilt[j-1])
        
        FeatureOutput[i] = np.log10(ILineLength+QLineLength)
        FeatureOutput[i] = bender(FeatureOutput[i], -2.7, 3.0)               #Limit to range of 0 to 1.  Second arg is mean, third is span      

    FeatureList = FeatureOutput.tolist()        #Convert ndarray to list.  The returned value will be appended other values; this would be very inefficent with ndarray

    #Return feature vector in form of a list
    return(FeatureList)

def difPeakDetect(FullPath):
    #print('Entering 1difPeakDetect()')
    TempClipData = spio.loadmat(FullPath)
    TempDataArray = TempClipData['data']
    TempDataArray = TempDataArray.transpose()

    Fsample = float(TempClipData['freq'])
    dt = 1.0/Fsample
    TimeValues = np.arange(0.0, 1.0, dt)
    LastChan = int(TempDataArray.shape[1])
    Channels = np.arange(0, LastChan, 1)

    FeatureOutput = np.zeros(LastChan)
    DifferenceArray = np.zeros((TempDataArray.shape[0] - 1, TempDataArray.shape[1]))

    for i in Channels:
        DifferenceArray[:,i] = np.diff(TempDataArray[:,i])

    # Read in the digital filter coeficients
    FilterInfo=spio.loadmat('FilterSet.mat')

    FilterCoefI = FilterInfo['FilterCoefI'].flatten()
    FilterCoefQ = FilterInfo['FilterCoefQ'].flatten()

    # Calculate the feature values for each channel       
    for i in Channels:
        #FeatureOutput[i]=TempDataArray[:,i].max()
        FeatureOutput[i]=np.log10(DifferenceArray[:,i].max()*DifferenceArray[:,i].max())
        FeatureOutput[i] = bender(FeatureOutput[i], 4, 4.5)
        '''
        Iproduct = FilterCoefI*TempDataArray[:,i]
        Isum=np.sum(Iproduct[i])
        
        Qproduct = FilterCoefQ*TempDataArray[:,i]
        Qsum=np.sum(Qproduct)
        
        FeatureOutput[i] = np.log10( np.sqrt(Isum*Isum + Qsum*Qsum) )
        '''

    FeatureList = FeatureOutput.tolist()        #Convert ndarray to list.  The returned value will be appended other values; this would be very inefficent with ndarray

    #Return feature vector in form of a list
    return(FeatureList)

def difTenTwentyBPFLL(FullPath):
    #print('Entering 1difPeakDetect()')
    TempClipData = spio.loadmat(FullPath)
    TempDataArray = TempClipData['data']
    TempDataArray = TempDataArray.transpose()

    Fsample = float(TempClipData['freq'])
    dt = 1.0/Fsample
    TimeValues = np.arange(0.0, 1.0, dt)
    LastChan = int(TempDataArray.shape[1])
    Channels = np.arange(0, LastChan, 1)

    FeatureOutput = np.zeros(LastChan)
    DifferenceArray = np.zeros((TempDataArray.shape[0] - 1, TempDataArray.shape[1]))

    for i in Channels:
        DifferenceArray[:,i] = np.diff(TempDataArray[:,i])

    # Read in the digital filter coeficients and place in ndarrays
    FilterInfo=spio.loadmat('FilterSetTenTwentyBPF.mat')

    FilterCoefI = FilterInfo['FilterCoefI'].flatten()
    FilterCoefQ = FilterInfo['FilterCoefQ'].flatten()

    ILineLength=0.0
    QLineLength=0.0

    # Calculate the feature values for each channel       
    for i in Channels:
        Ifilt = np.convolve(FilterCoefI, DifferenceArray[:,i])     
        Qfilt = np.convolve(FilterCoefQ, DifferenceArray[:,i])
        
        
        for j in range (1, Ifilt.size):
            ILineLength = np.abs(Ifilt[j]-Ifilt[j-1])
            QLineLength = np.abs(Qfilt[j]-Qfilt[j-1])
        
        FeatureOutput[i] = np.log10(ILineLength+QLineLength)
        FeatureOutput[i] = bender(FeatureOutput[i], -2.7, 3.0)               #Limit to range of 0 to 1.  Second arg is mean, third is span      

    FeatureList = FeatureOutput.tolist()        #Convert ndarray to list.  The returned value will be appended other values; this would be very inefficent with ndarray

    #Return feature vector in form of a list
    return(FeatureList)

def ChannelPeakDeviation(FullPath):
    #print('Entering ChannelPeakDeviation()')
    TempClipData = spio.loadmat(FullPath)
    TempDataArray = TempClipData['data']
    TempDataArray = TempDataArray.transpose()

    Fsample = float(TempClipData['freq'])       #Sampling frequency
    dt = 1.0/Fsample                            #Time between samples
    TimeValues = np.arange(0.0, 1.0, dt)        #Construct ndarray of time values
    LastChan = int(TempDataArray.shape[1])      #Last channel number
    Channels = np.arange(0, LastChan,1)         #List of channel numbers
    
    FeatureOutput = np.zeros(LastChan)          #Initialize the output

    # Calculate the feature values for each channel       
    for i in Channels:
        #FeatureOutput[i]=TempDataArray[:,i].max()
        FeatureOutput[i]=np.log10(TempDataArray[:,i].max()*TempDataArray[:,i].max())
        FeatureOutput[i] = bender(FeatureOutput[i], 4.8, 3.0)               #Limit to range of 0 to 1.  Second arg is mean, third is span 
        
    FeatureList = FeatureOutput.tolist()        #Convert ndarray to list.  The returned value will be appended other values; this would be very inefficent with ndarray

    stdev = np.std(FeatureList)
    for i in range(0, len(FeatureList)):
        FeatureList[i] = stdev
    #Return feature vector in form of a list
    return(FeatureList)

def difChannelPeakDeviation(FullPath):
    #print('Entering difChannelPeakDeviation()')
    TempClipData = spio.loadmat(FullPath)
    TempDataArray = TempClipData['data']
    TempDataArray = TempDataArray.transpose()

    Fsample = float(TempClipData['freq'])       #Sampling frequency
    dt = 1.0/Fsample                            #Time between samples
    TimeValues = np.arange(0.0, 1.0, dt)        #Construct ndarray of time values
    LastChan = int(TempDataArray.shape[1])      #Last channel number
    Channels = np.arange(0, LastChan,1)         #List of channel numbers
    
    FeatureOutput = np.zeros(LastChan)          #Initialize the output
    DifferenceArray = np.zeros((TempDataArray.shape[0] - 1, TempDataArray.shape[1]))

    for i in Channels:
        DifferenceArray[:,i] = np.diff(TempDataArray[:,i])

    # Calculate the feature values for each channel       
    for i in Channels:
        #FeatureOutput[i]=TempDataArray[:,i].max()
        FeatureOutput[i]=np.log10(DifferenceArray[:,i].max()*DifferenceArray[:,i].max())
        FeatureOutput[i] = bender(FeatureOutput[i], 4.8, 3)               #Limit to range of 0 to 1.  Second arg is mean, third is span 
        
    FeatureList = FeatureOutput.tolist()        #Convert ndarray to list.  The returned value will be appended other values; this would be very inefficent with ndarray

    stdev = np.std(FeatureList)
    for i in range(0, len(FeatureList)):
        FeatureList[i] = stdev
        FeatureList[i] = bender(FeatureList[i], .055, .1)
    
    #Return feature vector in form of a list
    return(FeatureList)
    
    

###############################################################################
# Main Loop
###############################################################################
def main():
    print('Entering main loop')
    app = FExplorer(None)
    app.mainloop()


# Call Main Loop
if __name__ == '__main__':
    main()
    
   
