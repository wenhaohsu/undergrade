# -*- coding: utf-8 -*-
"""
Created on Thu Jul 11 15:16:08 2019

@author: kylab
"""
import matplotlib.pyplot as plt
import matplotlib.ticker as tck
import numpy as np
from scipy.signal import find_peaks
import scipy.signal as signal
import math
from revised_wo_dev import revised_wo as wo
import pandas as pd
def medfilt (x, k):
    """Apply a length-k median filter to a 1D array x.
    Boundaries are extended by repeating endpoints.
    """
    assert k % 2 == 1, "Median filter length must be odd."
    assert x.ndim == 1, "Input must be one-dimensional."
    k2 = (k - 1) // 2
    y = np.zeros ((len (x), k), dtype=x.dtype)
    y[:,k2] = x
    for i in range (k2):
        j = k2 - i
        y[j:,i] = x[:-j]
        y[:j,i] = x[0]
        y[:-j,-(i+1)] = x[j:]
        y[-j:,-(i+1)] = x[-1]
    return np.median (y, axis=1)

#duration=4
duration=10
fs=250
refs=700
signal_start=4000
signal_len=duration*fs

cali=(1/256)*1.8/800*1000#256是2的8次方，1.8伏特，1000是伏特單位換算
fname = '060402.raw'   #取raw檔路徑

#%% Open RAW file in python

# samplingrate 500Hz

Raw_Data = open(fname, "rb").read()

RAW = []
for s in Raw_Data:
    RAW.append(s)

header = RAW[0:512]             #RAW files header
RAW = RAW[512:len(RAW)]         #RAW data

caliRAW=[i * cali for i in RAW]

#np.arange(0,duration,1/resample)
xs = np.arange(0,duration,1/fs)
ys = np.arange(0,2,0.5)
ecg = caliRAW[signal_start:signal_start+signal_len]
#xnew = np.arange(0,duration,1/refs)
#ecg_new = signal.resample(ecg,len(xnew))
col = {"HR" : ecg}
data = pd.DataFrame(col)

#%% plot1
mainfontsize=14
subfontsize=12
fig1 = plt.figure(figsize=(15,10))
fig1.add_subplot(2,1,1)

plt.plot(xs,ecg,'k',linewidth=1)
plt.xlim([0,duration])
plt.ylim([0,2])
plt.xlabel('Time (s)',fontsize=mainfontsize)
plt.ylabel('Amplitude (mV)',fontsize=mainfontsize)
ax = plt.gca()
ax.xaxis.grid(True,which='both') # vertical lines
ax.yaxis.grid(True,which='both') # horizontal lines

ax.yaxis.set_ticks(np.arange(0,256*cali,0.5))
ax.xaxis.set_minor_locator(tck.AutoMinorLocator())
ax.yaxis.set_minor_locator(tck.AutoMinorLocator())
plt.grid(which='major',color='r', linestyle='-', linewidth=1.2)
plt.grid(which='minor',color='r', linestyle='-', linewidth=0.5)
#ax.tick_params(axis='x', which='minor', bottom=True)
ax.tick_params(which='minor', length=0.5, color='r',direction='in')
plt.xticks(fontsize=subfontsize)
plt.yticks(fontsize=subfontsize)
peaks, _ = find_peaks(ecg, height=np.percentile(ecg, 95)) #取第95百分位
#peaks, _ = find_peaks(ecg_new, height=np.percentile(ecg_new, 95))
ECG = np.array(ecg) #list變成可以進行運算的N維陣列
plt.plot(peaks/fs, ECG[peaks], "*") #畫記號圖
plt.show()

#%% plot2
#fig1.add_subplot(2,1,2)
#
#ysmedian = np.arange(-1,1,0.5)
#r_peaks = ecg-medfilt(np.array(ecg),75) #這裡就已經將list轉為可以進行運算的N維陣列
#plt.plot(xs,r_peaks,'k',linewidth=1)
#plt.xlim([0,duration])
#plt.ylim([-1,1])
#plt.xlabel('Time (s)',fontsize=mainfontsize)
#plt.ylabel('Amplitude (mV)',fontsize=mainfontsize)
#ax = plt.gca()
#ax.xaxis.grid(True,which='both') # vertical lines
#ax.yaxis.grid(True,which='both') # horizontal lines
#
#ax.yaxis.set_ticks(np.arange(-1,1.1,0.5))
#ax.xaxis.set_minor_locator(tck.AutoMinorLocator())
#ax.yaxis.set_minor_locator(tck.AutoMinorLocator())
#plt.grid(which='major',color='r', linestyle='-', linewidth=1.2)
#plt.grid(which='minor',color='r', linestyle='-', linewidth=0.5)
##ax.tick_params(axis='x', which='minor', bottom=True)
#ax.tick_params(which='minor', length=0.5, color='r',direction='in')
#plt.xticks(fontsize=subfontsize)
#plt.yticks(fontsize=subfontsize)
#
#peaks, _ = find_peaks(r_peaks, height=np.percentile(r_peaks, 95))
##取第95百分位，也就是按照常態分佈取第二標準差以後的結果
#plt.plot(peaks/fs, r_peaks[peaks], "*") #畫記號圖
##plt.plot(peaks/refs, r_peaks[peaks], "*")

#%% rr interval

plt.figure(2)   
sub = 1
sub2 = 0

for i in peaks:
        
    #add subplot
    column = math.ceil(len(peaks)/6) 
    plt.subplot(6, column, sub + sub2)  #set row & column
    
    #cut R peak
    cut1 = (xs[i] - (175/1000))*fs     

    cut2 = (xs[i] + (175/1000))*fs

    test = plt.plot(ecg[int(cut1):int(cut2)])

    
    sub2 = sub2 + 1     #畫完一張圖，新增一個subplot
#

##--------------CI 95%--------------#
plt.figure(3)

for i in peaks:
     
    cut1 = (xs[i] - (150/1000))*fs      
    cut2 = (xs[i] + (150/1000))*fs

    
    plt.plot(ecg[int(cut1):int(cut2)])


    
Mean_HR = np.mean(data.HR)     #average
std_HR = np.std(data.HR)    #標準差
sqrt_HR = np.sqrt(len(data))      
CI1 = Mean_HR + 1.96*std_HR/sqrt_HR
CI2 = Mean_HR - 1.96*std_HR/sqrt_HR

plt.xlim(0, 150)
plt.plot(CI1, linewidth = 5)
plt.plot(CI2, linewidth = 5)

#%%
peak_diff = [ peaks[i+1]-peaks[i] for i in range(len(peaks)-1) ]#在每個RR之間利用插分尋找interval
RR = []
for i in range(len(peak_diff)):
    resm_RR = peak_diff[i]*1000/fs #要把取樣除回去
    RR.append(resm_RR)

#%%
al_cutoff = cutoff / nyq
    b, a =import numpy as np
from scipy.signal import butter, lfilter, freqz
import matplotlib.pyplot as plt


def butter_lowpass(cutoff, fs, order=6):
    nyq = 0.5 * fs
    norm butter(order, normal_cutoff, btype='low', analog=False)
    return b, a

def butter_lowpass_filter(data, cutoff, fs, order=6):
    b, a = butter_lowpass(cutoff, fs, order=order)
    y = lfilter(b, a, data)
    return y


# Filter requirements.
order = 6
#fs = 500.0       # sample rate, Hz
cutoff = 53  # desired cutoff frequency of the filter, Hz

# Get the filter coefficients so we can check its frequency response.
b, a = butter_lowpass(cutoff, fs, order)

# Plot the frequency response.
w, h = freqz(b, a, worN=8000)
plt.subplot(2, 1, 1)
plt.plot(0.5*fs*w/np.pi, np.abs(h), 'b')
plt.plot(cutoff, 0.5*np.sqrt(2), 'ko')
plt.axvline(cutoff, color='k')
plt.xlim(0, 0.5*fs)
plt.title("Lowpass Filter Frequency Response")
plt.xlabel('Frequency [Hz]')
plt.grid()


# Demonstrate the use of the filter.
# First make some data to be filtered.
T = 30         # seconds
n = int(T * fs) # total number of samples
t = np.linspace(0, T, n, endpoint=False)
# "Noisy" data.  We want to recover the 1.2 Hz signal from this.
#data = np.sin(15*2*np.pi*t) + 1.5*np.cos(20*2*np.pi*t) + 0.5*np.sin(12.0*2*np.pi*t)

# Filter the data, and plot both the original and filtered signals.
y = butter_lowpass_filter(ecg, cutoff, fs, order)

plt.subplot(2, 1, 2)
plt.plot(t, ecg, 'b-', label='data')
plt.plot(t, y, 'g-', linewidth=2, label='filtered data')
plt.xlabel('Time [sec]')
plt.grid()
plt.legend()

plt.subplots_adjust(hspace=0.35)
plt.show()
#%%做平均補點法

#f= signal.resample(y,700)