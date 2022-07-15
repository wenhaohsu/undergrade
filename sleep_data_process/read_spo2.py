#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 20 14:11:31 2020

@author: hao
"""

from datetime import datetime, timedelta
import pandas as pd
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()
import numpy as np
import matplotlib.pyplot as plt

def file_read(get_path,get_ID,get_day,get_filetype):
    return get_path+'/'+get_ID.upper()+'_'+get_day+'('+get_filetype+').xlsx' 
def read_rename(data,sheet):
    read_data=pd.read_excel(data,sheet_name=sheet)
    rename_data=read_data.rename(columns={'Unnamed: 0':'Time'})
    return rename_data
def next_day(time,day):
    date=[]
    for i in range(len(time)):
        if pd.to_datetime(time[i])>=pd.to_datetime('00:00:00') and pd.to_datetime(time[i])<pd.to_datetime('12:00:00'):
            date.append(day_list[0])
        else:
            date.append(day_list[1])
    return date
def getSleepScore(Sleepstage):
    if ('REM' in Sleepstage) or ('R' in Sleepstage):
        score=4
    elif ('S0' in Sleepstage) or ('Wake' in Sleepstage) or ('W' in Sleepstage): # wake
        score=5
    elif ('S1' in Sleepstage) or ('N1' in Sleepstage): 
        score=3
    elif ('S2' in Sleepstage) or ('N2' in Sleepstage):
        score=2
    elif ('S3' in Sleepstage) or ('S4' in Sleepstage) or ('N3' in Sleepstage): #sleep stage3
        score=1
    else:
        score=0
    return score

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
#def filter_band(data):
#    output1 = []
#    max_heart=120
#    min_heart=40
#    for i in range(len(data)):
#        if data[i]>max_heart or data[i]<min_heart:
#            output1.append(np.mean(data))
#        else:
#            output1.append(data[i])
#    return output1
def HR_window(SpO2,window):
    SD_HR=[]
    start = 0
    for i in range(0,len(SpO2),window):
        SD=np.std(SpO2[start:start+window])
        start = start + window
        SD_HR.append(SD)
    return SD_HR

def sliding_overlap_filter(HR,window):
    SD_HR=[]
    for i in range(len(HR)):
        if i > len(HR)-(window+1):
            SD_HR.append(np.std(HR[i::]))
        else:
            SD_HR.append(np.std(HR[i:i+window]))
    return SD_HR

#%%
path='/Users/hao/Desktop/實驗資料/健康組/季緯'
ID='01d60040'
day='20191227'
day_list=[day,str(int(day)-1)]
filetype='SPO2'
sheet_name='SPO2'
resample_dic={'ACT':'mean', 'HR':'mean', 'O2':'mean'}
file=file_read(path,ID,day_list[0],filetype)
file=read_rename(file,sheet_name)
date=next_day(file['Time'],day_list[0])
date_time=pd.DataFrame({'Date':date,'Time':file['Time']})
date_time=pd.DatetimeIndex(pd.to_datetime(date_time.Date+' '+date_time.Time))
SpO2=pd.DataFrame({'Time':date_time,'O2':file.O2,'HR':file.HR,'ACT':file.ACT})
#%%
name=day[4:8]
data=path+'/'+name+'.txt'
TD1_data=pd.read_csv(data,engine='python',skiprows=range(0,19),encoding='big5',delim_whitespace=True)#,sep=" ")#, header=None)
sleep=TD1_data['Sleep'].tolist()
score=[getSleepScore(sleep[i]) for i in range(len(sleep))]
TD1_data=TD1_data.replace(to_replace ="下午", value ="PM")
TD1_data=TD1_data.replace(to_replace ="上午", value ="AM")
clock=[(str(TD1_data.Time[i]+' '+TD1_data.Stage[i])) for i in range(len(TD1_data))]
time_TD1=pd.to_datetime(clock).strftime('%H:%M:%S')
date_TD1=next_day(time_TD1,day_list[0])
date_time_TD1=pd.DataFrame({'Date':date_TD1,'Time':time_TD1})
date_time_TD1=pd.DatetimeIndex(pd.to_datetime(date_time_TD1.Date+' '+date_time_TD1.Time))
TD1=pd.DataFrame({'Time':date_time_TD1,'Score':score})
#%%
#filter_HR=filter_band(SpO2.HR)  
#測試
#SpO2_2=pd.DataFrame({'O2':file.O2,'HR':file.HR,'ACT':file.ACT})
#SpO2_2=SpO2_2.set_index(date_time)
TD1_2=pd.DataFrame({'Score':score})
TD1_2=TD1_2.set_index(date_time_TD1)
TD1_2=TD1_2.resample('1s').ffill()
TD1_21=TD1_2.resample('10s').ffill()
TD1_21=TD1_21.reset_index(inplace=False)
TD1_21=TD1_21.rename(columns={'index':'Time'})
TD1_22=TD1_2.resample('30s').ffill()
TD1_22=TD1_22.reset_index(inplace=False)
TD1_22=TD1_22.rename(columns={'index':'Time'})


SpO2_10s=[SpO2.Time[i] for i in range(0,len(SpO2),10)]
SpO2_std_10=HR_window(SpO2.HR,10)
SpO2_30s=[SpO2.Time[i] for i in range(0,len(SpO2),30)]
SpO2_std_30=HR_window(SpO2.HR,30)
yy=np.array([1,2,3,4,5])
yticks1 = ["N3","N2","N1","REM","Wake"]
#%%
std2_10s=sliding_overlap_filter(SpO2.HR,10)
std2_30s=sliding_overlap_filter(SpO2.HR,30)

fig1=plt.figure(figsize=(15,15))
fign=6
fig1.add_subplot(fign,1,1)
plt.plot(SpO2.Time,SpO2.HR)
plt.yticks(fontsize=12,fontname="Arial")
plt.ylabel('Heart rate',fontsize=12,fontname="Arial")
plt.xlim(SpO2.Time[0],SpO2.Time[len(SpO2)-1])
plt.title(str(day),fontsize=18,fontname="Arial")
#plt.xticks([])
fig1.add_subplot(fign,1,2)
plt.plot(SpO2_10s,SpO2_std_10)
plt.yticks(fontsize=12,fontname="Arial")
plt.ylabel('SD\n10sec HR',fontsize=12,fontname="Arial")
plt.xlim(SpO2_10s[0],SpO2_10s[-1])
#plt.xticks([])
plt.ylim(0,10)
fig1.add_subplot(fign,1,3)
plt.plot(SpO2_30s,SpO2_std_30)
plt.yticks(fontsize=12,fontname="Arial")
plt.ylabel('SD\n30sec HR',fontsize=12,fontname="Arial")
plt.xlim(SpO2_30s[0],SpO2_30s[-1])
plt.ylim(0,10)
#plt.xticks([])
fig1.add_subplot(fign,1,4)
plt.plot(SpO2.Time,std2_10s)
plt.yticks(fontsize=12,fontname="Arial")
plt.ylabel('SD 10sec\noverlap HR',fontsize=12,fontname="Arial")
plt.xlim(SpO2.Time[0],SpO2.Time[len(SpO2)-1])
#plt.xticks([])
plt.ylim(0,10)
fig1.add_subplot(fign,1,5)
plt.plot(SpO2.Time,std2_30s)
plt.yticks(fontsize=12,fontname="Arial")
plt.ylabel('SD 30sec\noverlap HR',fontsize=12,fontname="Arial")
plt.xlim(SpO2.Time[0],SpO2.Time[len(SpO2)-1])
plt.ylim(0,10)
#plt.xticks([])
fig1.add_subplot(fign,1,6)
plt.plot(TD1_2.Score)
plt.yticks(yy,yticks1,fontsize=12,fontname="Arial")
plt.xlim(SpO2_30s[0],SpO2_30s[-1])
plt.xticks(fontsize=12,fontname="Arial")
#%%



#fig2=plt.figure(figsize=(15,15))
#fign=3
#fig2.add_subplot(fign,1,1)
#plt.plot(SpO2.Time,std2_10s)
#plt.yticks(fontsize=12,fontname="Arial")
#plt.ylabel('SD\n10sec HR',fontsize=12,fontname="Arial")
#plt.xlim(SpO2.Time[0],SpO2.Time[len(SpO2)-1])
##plt.xticks([])
#plt.ylim(0,10)
#fig2.add_subplot(fign,1,2)
#plt.plot(SpO2.Time,std2_30s)
#plt.yticks(fontsize=12,fontname="Arial")
#plt.ylabel('SD\n30sec HR',fontsize=12,fontname="Arial")
#plt.xlim(SpO2.Time[0],SpO2.Time[len(SpO2)-1])
#plt.ylim(0,10)
##plt.xticks([])
#fig2.add_subplot(fign,1,3)
#plt.plot(TD1_2.Score)
#plt.yticks(yy,yticks1,fontsize=12,fontname="Arial")
#plt.xlim(SpO2.Time[0],SpO2.Time[len(SpO2)-1])
#plt.xticks(fontsize=12,fontname="Arial")