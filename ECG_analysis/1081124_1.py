# -*- coding: utf-8 -*-
"""
Created on Mon Jul 29 07:00:45 2019

@author: asus
"""
import pandas as pd
from pandas.core.frame import DataFrame
import matplotlib.pyplot as plt
import numpy as np
import math
from scipy.signal import medfilt
from scipy import signal
from scipy import stats
from scipy.stats import entropy
#import statistics

duration=30
samplingrate=500
signal_start=4500
signal_len=duration*samplingrate
ticks_size = 14
label_size = 18

'''-------
Read file
----------'''

fname = '060402.RAW'   #取raw檔路徑
Raw_Data = open(fname, "rb").read()


RAW = []
for s in Raw_Data:
    RAW.append(s) 
    
#print (RAW)
    
xs = [i for i in range(signal_len)]
x1 = np.linspace(0, duration, len(xs))  #x軸，將point轉換成time
x_time = []     #存入x_time這個list
for x in x1:
    x_time.append(x)

vector = (RAW[signal_start:signal_start+signal_len])

#Butterworth Filter
b, a = signal.butter(10, 0.1)
y = signal.filtfilt(b, a, vector)

vector2 = [a for a in y]

#進位轉換
#standard = []
#for index2 in vector:
#    stand = (((index2 + 32768) % 65535) - 32767) / 8192
#    #x = (mod(bin_decode_singlech('x.bin')+32768,65535)-32767)./8192;
#    standard.append(stand)


col = {"HR" : y}
data = DataFrame(col)

time = (data.index/samplingrate)
data['time'] = time



'''-----------------
Feature Extraction
--------------------'''

#-----detect R-peak-----#

hrw = 0.3 #One-sided window size, as proportion of the sampling frequency
fs = 125 #The example dataset was recorded at 100Hz
mov_avg = data['HR'].rolling(int(hrw*fs)).mean() #Calculate moving average
#Impute where moving average function returns NaN, which is the beginning of the signal where x hrw

avg_hr = (np.mean(data.HR))
mov_avg = [avg_hr if math.isnan(x) else x for x in mov_avg]
mov_avg = [x*1.2 for x in mov_avg] #For now we raise the average by 20% to prevent the secondary heart contraction from interfering, in part 2 we will do this dynamically
data['HR_rollingmean'] = mov_avg #Append the moving average to the dataframe
#Mark regions of interest
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

#-----detect P、Q、S、T-----#

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

thershold = [30, 100, 150]

for index3 in peaklist:
    
    ##------peak------##
    # P-wave
    if index3 < thershold[1]:
        p_list = vector2[0:(index3 - thershold[0])]
        p_y = max(p_list)
        p_index = p_list.index(max(p_list))
        p_x = 0 + p_index
    
    else:
        p_list = vector2[(index3 - thershold[1]):(index3 - thershold[0])]
        p_y = max(p_list)
        p_index = p_list.index(max(p_list))
        p_x = index3 - thershold[1] + p_index
    px.append(p_x)  
    py.append(p_y)
       
    # Q-wave
    q_list = vector2[(index3 - thershold[0]):index3]
    q_y = min(q_list)
    q_index = q_list.index(min(q_list))
    q_x = index3 - thershold[0] + q_index
    qx.append(q_x)          
    qy.append(q_y)
    
    # S-wavw
    s_list = vector2[index3:(index3 + thershold[0])]
    s_y = min(s_list)
    s_index = s_list.index(min(s_list))
    s_x = index3 + s_index
    sx.append(s_x)          
    sy.append(s_y)
    
    # T-wave
    t_list = vector2[(index3 + thershold[0]):(index3 + thershold[2])]
    t_y = max(t_list)
    t_index = t_list.index(max(t_list))
    t_x = index3 + t_index + thershold[0]
    tx.append(t_x)          
    ty.append(t_y)
      


px_time = [x_time[a] for a in px]            
qx_time = [x_time[b] for b in qx] 
sx_time = [x_time[c] for c in sx]
tx_time = [x_time[d] for d in tx]


plt.figure(1)
plt.title("Detected peaks in signal", fontsize = 20)
plt.xticks(fontsize = ticks_size)
plt.yticks(fontsize = ticks_size)
plt.xlabel('Time (s)', fontsize = label_size)
plt.ylabel('Amplitude (mV)', fontsize = label_size)
plt.plot(x_time, data.HR) #Plot semi-transparent HR
plt.scatter(peaklist_time, ybeat, c='red') #Plot detected peaks
plt.scatter(px_time, py, c='blue')
plt.scatter(qx_time, qy, c='red')
plt.scatter(sx_time, sy, c='red')
plt.scatter(tx_time, ty, c='y')
plt.show()

'''----------------
Interval extraction (這部分還沒做)
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

#-----------------------------------
#            Cut R-peak
#-----------------------------------
plt.figure(2)   
sub = 1
sub2 = 0
epoch = 150

for index in peaklist:
       
    #add subplot
    column = math.ceil(len(peaklist)/6) 
    plt.subplot(6, column, sub + sub2)  #set row & column
    
    #cut R peak，計算切割區間(以R peak為中心的300ms)
    cut1 = (x_time[index] - (epoch/1000))*samplingrate     
    cut2 = (x_time[index] + (epoch/1000))*samplingrate
    y = []
    for k in range(len(vector[int(cut1):int(cut2)])):
        k = (k/samplingrate)
        y.append(k)
    
    plt.plot(y, vector[int(cut1):int(cut2)])
#    plt.xticks([])
#    plt.yticks([])
               
    sub2 = sub2 + 1     #畫完一張圖，新增一個subplot

#plt.xlabel('Time (ms)', fontsize = label_size)
#plt.ylabel('Amplitude (mV)', fontsize = label_size)
    

#-----------------------------------
#             Butterworth
#-----------------------------------    
    
plt.figure(3)
plt.plot(x_time, vector, 'b', alpha=0.75)
plt.plot(x_time, vector2, 'k')
plt.legend(('noisy signal','filtfilt'), loc='best')
#plt.grid(True)
plt.show()
    
#-----------------------------------
#            R-R interval
#-----------------------------------

RR_time2 = []

plt.figure(4)
#peak_diff = data.HR[peaklist].tolist()
#plt.plot(x_time, data.HR)
#plt.plot(peaklist_time,peak_diff,'o-',color = 'g')
RR = [peaklist[i+1]-peaklist[i] for i in range(len(peaklist)-1)]
RR_interval = [(i/samplingrate)*1000 for i in RR]
RR_time = [d/1000 for d in RR_interval]
RR_time_s = 0

for e in range(len(RR_time)):
    RR_time_s = RR_time_s + RR_time[e]
    RR_time2.append(RR_time_s)

plt.title("R-R interval", fontsize = 20)
plt.xticks(fontsize = ticks_size)
plt.yticks(fontsize = ticks_size)
plt.xlabel('Time (s)', fontsize = label_size)
plt.ylabel('Interval (ms)', fontsize = label_size)
plt.plot(RR_time2, RR_interval)
#peaklist_time = [x_time[j] for j in peaklist]
#RR_interval_s = (RR_interval/1000)
#RR_time.append(RR_interval/1000)

#plt.plot(RR_interval)

Mean_RR = np.mean(RR_interval)
SD_RR = np.std(RR_interval)
RMSSD = np.sqrt(np.mean(np.array(RR_interval)**2))


#-----------------------------------
#              Entropy
#-----------------------------------

def Entropy(labels, base=2):

    probs = pd.Series(labels).value_counts() / len(labels)
    en = stats.entropy(probs, base=base)
    return en


entro = []
abc = []

for h in range(0, len(vector2), 500):
    
    abc.append(h)
    entro.append(Entropy(vector2[h : h + 499])) 
        

#-----------------------------------
#              CI 95%
#-----------------------------------
#plt.figure(3)
#
#apeak = []
#avg = []
#ci1 = []
#ci2 = []
#
#def transpose(list1):       #set 轉置矩陣 function
#    return [list(row) for row in zip(*list1)]
#
##將切割好的每個波存入apeak矩陣，並轉置
#for index in peaklist:
#        
#    cut1 = (x_time[index] - (150/1000))*500      
#    cut2 = (x_time[index] + (150/1000))*500    
#    #plt.plot(y, vector[int(cut1):int(cut2)])
#    
#    apeak.append(vector[int(cut1):int(cut2)]) 
#    apeakT = transpose(apeak)
#
#    
##計算95%信賴區間
#for index2 in range(len(apeakT)):
#    X_HR = np.mean(apeakT[index2])
#    std_HR = np.std(apeakT[index2])
#    sqrt_HR = np.sqrt(len(apeakT[0]))
#    
#    CI1 = X_HR + 1.96*std_HR
#    CI2 = X_HR - 1.96*std_HR
#    
#    avg.append(X_HR)
#    ci1.append(CI1)
#    ci2.append(CI2)
#
#z = []
#for q in range(len(ci1)):
#        q = (q/samplingrate)
#        z.append(q)
#        
#plt.xlim(0, 0.3)
#plt.plot(z, avg)
#plt.plot(z, ci1, linewidth = 2, color='r')
#plt.plot(z, ci2, linewidth = 2, color='r')
#plt.xticks(fontsize = ticks_size)
#plt.yticks(fontsize = ticks_size)
#plt.xlabel('Time (s)', fontsize = label_size)
#plt.ylabel('Amplitude (mV)', fontsize = label_size)

#%%
'''----
Filter
-------'''

#------------Filter-------------#
#plt.figure(4)
#med = medfilt(data.HR, 323)
#data_array = np.array(data.HR)
#med_array = np.array(med)
#medfilter_array = data_array - med_array
##plt.plot(med)
#plt.subplot(2,1,1)
#plt.plot(data.HR)
#plt.title("Origianl signal", fontsize = 18)
#plt.subplot(2,1,2)
#plt.plot(medfilter_array)
#plt.title("Filter signal", fontsize = 18)




