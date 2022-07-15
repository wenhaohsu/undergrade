#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 10 16:34:28 2020

@author: hao
"""

from dataDecode import dataDecode
import matplotlib.pyplot as plt
import numpy as np
def resample(signal,input_fs,output_fs):
    scale = output_fs / input_fs
    n = round(len(signal) * scale)
    resampled_signal = np.interp(
        np.linspace(0.0, 1.0, n, endpoint=False),  # where to interpret
        np.linspace(0.0, 1.0, len(signal), endpoint=False),  # known positions
        signal,  # known data points
    )
    return resampled_signal
#%%
fname='/Users/hao/Desktop/陳威儒OK/200212威儒1.RAW'
Raw_Data = open(fname, "rb").read()
Data,sampling_rate,time=dataDecode.rawdataDecode(Raw_Data)
data_sam = sampling_rate[0]/4
duration=int(len(Data[0])/(sampling_rate[0]))
Data_len=int(sampling_rate[0])*duration
Data_from=len(Data[0])-Data_len
vector=[Data[i][Data_from:Data_from+Data_len] for i in range(len(Data))]
#%%
#resample_data=[resample(Data[i][Data_from:Data_from+Data_len],sampling_rate[0],data_sam) for i in range(len(Data))]
#fig1=plt.figure(figsize=(20,20))
#fig1.add_subplot(2,1,1)
#plt.plot(vector[3])
#fig1.add_subplot(2,1,2)
#plt.plot(resample_data[3])