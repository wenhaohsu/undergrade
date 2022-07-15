#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 24 10:36:29 2019

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

urlstart="http://xds.ym.edu.tw/01530055/191224b.153"
    #前面都是做例外處理，確認設備是否在線上或者，這裡是正式下載資料
r = requests.get(urlstart)
rawtxt=r.content #content:二進制

Data,sampling_rate=dataDecode.rawdataDecode(rawtxt)
data_sam = sampling_rate/2
duration=int(len(Data[0])/(data_sam))
Data_len=int(data_sam)*duration
Data_from=len(Data[0])-Data_len

vector=Data[0][Data_from:Data_from+Data_len]#-medfilt(np.array(Data[0][Data_from:Data_from+Data_len]),125)
#plt.plot(vector)
fc = 45
w = fc/(sampling_rate/4)
b, a = signal.butter(2, w)
vector_filt = signal.filtfilt(b, a, vector)
#plt.plot(medfilt(np.array(Data[0][Data_from:Data_from+Data_len]),125))
col = {"HR" : vector_filt}
#col2 = {"HR" : vector}
data = pd.DataFrame(col)
#plt.plot(vector_filt)
#data2 = pd.DataFrame(col2)
xs = [i for i in range(Data_len)]
x1 = np.linspace(0, duration, len(xs))  #x軸，將point轉換成time
x_time = []     #存入x_time這個list
for x in x1:
    x_time.append(x)

hrw = 0.3 #One-sided window size, as proportion of the sampling frequency
fs = sampling_rate/2 #The example dataset was recorded at 100Hz
#fs = sampling_rate/2
mov_avg = data['HR'].rolling(int(hrw*fs)).mean() 
#Calculate moving average
#Impute where moving average function returns NaN, which is the beginning of the signal where x hrw
avg_hr = (np.mean(data.HR))
mov_avg = [avg_hr if math.isnan(x) else x for x in mov_avg]
mov_avg = [x*1.13 for x in mov_avg] 
#For now we raise the average by 4% to prevent the secondary heart contraction from interfering, in part 2 we will do this dynamically
data['HR_rollingmean'] = mov_avg 

#Append the moving average to the dataframe    
window = []
peaklist = []
listpos = 0 #We use a counter to move over the different data columns
for datapoint in data.HR:
    rollingmean = data.HR_rollingmean[listpos] #Get local mean
    if (datapoint < rollingmean) and (len(window) < 1): #If no detectable R-complex activity -> do nothing
        listpos += 1
    elif (datapoint > rollingmean): #If signal comes above local mean, mark ROI
        window.append(datapoint)
        listpos += 1
    else: #If signal drops below local mean -> determine highest point
        #maximum = max(window)
        beatposition = listpos - len(window) + (window.index(max(window))) #Notate the position of the point on the X-axis
        peaklist.append(beatposition) #Add detected peak to list
        window = [] #Clear marked ROI
        listpos += 1
ybeat = [data.HR[x] for x in peaklist] #Get the y-value of all peaks for plotting purposes
peaklist_time = [x_time[j] for j in peaklist]

px = []
py = []
qx = []
qy = []
sx = []
sy = []
tx = []
ty = []

prx = []
qrsx = []
qtx = []

thershold = [30, 80, 120]

for index3 in peaklist:
    
    ##------peak------##
    # P-wave
    if index3 < thershold[1]:
        p_list = vector[0:(index3 - thershold[0])]
        p_x = max(p_list)
        p_index = p_list.index(max(p_list))
        p_y = 0 + p_index
    
    else:
        p_list = vector[(index3 - thershold[1]):(index3 - thershold[0])]
        p_y = max(p_list)
        p_index = p_list.index(max(p_list))
        p_x = index3 - thershold[1] + p_index
    px.append(p_x)  
    py.append(p_y)
       
    # Q-wave
    q_list = vector[(index3 - thershold[0]):index3]
    q_y = min(q_list)
    q_index = q_list.index(min(q_list))
    q_x = index3 - thershold[0] + q_index
    qx.append(q_x)          
    qy.append(q_y)
    
    # S-wavw
    s_list = vector[index3:(index3 + thershold[0])]
    s_y = min(s_list)
    s_index = s_list.index(min(s_list))
    s_x = index3 + s_index
    sx.append(s_x)          
    sy.append(s_y)
    
    # T-wave
    t_list = vector[(index3 + thershold[0]):(index3 + thershold[2])]
    t_y = max(t_list)
    t_index = t_list.index(max(t_list))
    t_x = index3 + t_index + thershold[0]
    tx.append(t_x)          
    ty.append(t_y)
#    
#    ##------interval------##
#    # P-R interval
#    pr_time = ((q_x - p_x)/sampling_rate)*1000
#    prx.append(pr_time)
#    
#    # QRS complex
#    qrs_time = ((s_x - q_x)/sampling_rate)*1000
#    qrsx.append(qrs_time)
#    
#    # Q-T interval
#    qt_time = ((t_x - q_x)/sampling_rate)*1000
#    qtx.append(qt_time)
#    
#
#
px_time = [x_time[a] for a in px]            
qx_time = [x_time[b] for b in qx] 
sx_time = [x_time[c] for c in sx]
tx_time = [x_time[d] for d in tx]

ticks_size = 14
label_size = 18

plt.figure(1)
plt.title("Detected peaks in signal", fontsize = 20)
plt.xticks(fontsize = ticks_size)
plt.yticks(fontsize = ticks_size)
plt.xlabel('Time (s)', fontsize = label_size)
plt.ylabel('Amplitude (mV)', fontsize = label_size)
#plt.plot(x_time, data2.HR)
plt.plot(x_time, data.HR) #Plot semi-transparent HR
plt.scatter(peaklist_time, ybeat, c='red') #Plot detected peaks
#plt.scatter(px_time, py, c='blue')
#plt.scatter(qx_time, qy, c='red')
#plt.scatter(sx_time, sy, c='red')
#plt.scatter(tx_time, ty, c='y')
plt.show()
#%%
'''----------------
Interval extraction
-------------------'''

#P-R interval

p0 = []

#for index4 in px:
#    pr_list = vector[(index4 - 40):index4]
#    p_0 = (statistics.median(pr_list))
#    for index5 in (pr_list):
#        if (index5 - p_0) <= 0:
#            p0.append(pr_list.index(index5))
#    prxx = p0[-1]; pryy = (vector[prx])


'''--------------
Cut each cycle
-----------------'''

#------------cut R peak------------#
plt.figure(2)   
sub = 1
sub2 = 0
epoch = 150

for index in peaklist:
       
    #add subplot
    column = math.ceil(len(peaklist)/6) 
    plt.subplot(6, column, sub + sub2)  #set row & column
    
    #cut R peak，計算切割區間(以R peak為中心的300ms)
    cut1 = (x_time[index] - (epoch/1000))*sampling_rate     
    cut2 = (x_time[index] + (epoch/1000))*sampling_rate
    y = []
    for k in range(len(vector[int(cut1):int(cut2)])):
        k = (k/sampling_rate)
        y.append(k)
    
    plt.plot(y, vector[int(cut1):int(cut2)])
#    plt.xticks([])
#    plt.yticks([])
               
    sub2 = sub2 + 1     #畫完一張圖，新增一個subplot
#%%
#plt.xlabel('Time (ms)', fontsize = label_size)
#plt.ylabel('Amplitude (mV)', fontsize = label_size)
 
##-------------filter------------##
#fc = 40
#w = fc/(samplingrate/2)
#b, a = signal.butter(5, w)
#y = signal.filtfilt(b, a, vector)
#
#vector2 = [a for a in vector_filt]
#plt.figure(3)
#plt.plot(x_time, vector, 'b', alpha=0.75)
#plt.plot(x_time, vector2, 'k')
#plt.legend(('noisy signal','filtfilt'), loc='best')
##plt.grid(True)
#plt.show()

##--time domain--##

plt.figure(4)

peak_diff = [peaklist[i+1]-peaklist[i] for i in range(len(peaklist)-1)]
RR = [(i/sampling_rate)*1000 for i in peak_diff]
RR_sample = 4
time_new = np.arange(0,duration,1/RR_sample)
RR_interval = signal.resample(RR,len(time_new))
plt.plot(time_new, RR_interval,'o-',color = 'g')
Mean_RR = np.mean(RR_interval)
SD_RR = np.std(RR_interval)
RMSSD = np.sqrt(np.mean(np.array(SD_RR)**2))

plt.title("R-R interval", fontsize = 20)
plt.xticks(fontsize = ticks_size)
plt.yticks(fontsize = ticks_size)
plt.xlabel('Time (s)', fontsize = label_size)
plt.ylabel('Interval (ms)', fontsize = label_size)

##--frequency domain--##
#%%
plt.figure(5)

RR_frq = fft(RR_interval)      #快速傅立葉變換
RR_real = RR_frq.real    # 獲取實數部分
RR_conj = RR_frq.imag    # 獲取虛數部分
RR_time = len(time_new)
power_RR = abs(np.multiply(RR_frq,RR_conj/RR_time))
fsb = RR_sample/RR_time
f = fsb*time_new[0:round(RR_time/2)]
#%%
def band(low,high,x):
    output1 = []
    for i in range(len(x)):
        if x[i] <= high and low <= x[i]:
            output1.append(i)
    return output1
vl = band(0,0.04,f)
lf = band(0.04,0.15,f)
hf = band(0.15,0.4,f)
LF = sum(power_RR[lf])*fsb
HF = sum(power_RR[hf])*fsb
VLF = sum(power_RR[vl])*fsb
TP = LF+HF+VLF 
LHratio=LF/HF

#plt.plot(f[findex],power_RR[findex])
plt.plot(f[hf],power_RR[hf],label='HF')
plt.plot(f[lf],power_RR[lf],label="LF")
plt.legend()
plt.title('Power spectral density')
plt.xlabel('Frequency (Hz)')   
#    testData=pd.DataFrame(vector_filt[int(cut1):int(cut2)]) 
    
