#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan  7 12:11:55 2020

@author: hao
"""

from dataDecode import dataDecode
import requests
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from scipy import signal
import math
from numpy.fft import fft, fftshift

urlstart="http://xds.ym.edu.tw:81/00230052/191220.023"
    #前面都是做例外處理，確認設備是否在線上或者，這裡是正式下載資料
r = requests.get(urlstart)
rawtxt=r.content #content:二進制
Data,sampling_rate=dataDecode.rawdataDecode(rawtxt)
#CH1 = Data[0]
#CH2 = Data[1]
#CH3 = Data[2]
CH4 = Data[3]
CH5 = Data[4]
data_sam = sampling_rate/2
duration=int(len(CH5)/(data_sam))
Data_len=int(data_sam)*duration
Data_from=len(CH5)-Data_len

vector=CH5[Data_from:Data_from+Data_len]#-medfilt(np.array(Data[0][Data_from:Data_from+Data_len]),125)
plt.plot(vector)
#   plt.plot(medfilt(np.array(Data[0][Data_from:Data_from+Data_len]),125))
col = {"HR" : vector}
data = pd.DataFrame(col)


    
#xs = [i for i in range(Data_len)]
#x1 = np.linspace(0, duration, len(xs))  #x軸，將point轉換成time
#x_time = []     #存入x_time這個list
#for x in x1:
#    x_time.append(x)

plt.plot(data)