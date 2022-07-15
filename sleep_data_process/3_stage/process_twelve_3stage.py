#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 30 11:45:32 2020

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
        if pd.to_datetime(time[i])>=pd.to_datetime('00:00:00') and pd.to_datetime(time[i])<pd.to_datetime('13:00:00'):
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
def HR_window(HR,window):
    SD_HR=[]
    start = 0
    for i in range(0,len(HR),window):
        SD=np.std(HR[start:start+window])
        start = start + window
        SD_HR.append(SD)
    return SD_HR
#%% ACT & HR
path='/Users/hao/Desktop/實驗資料/健康組/子富'
ID=['0358005b','029c005c','01d60040']
day='20200405'
day_list=[day,str(int(day)-1)]
filetype=['HRV','SPO2']
sheet_name=['HR&ACT','ACT&Illuminance','HRV_data_remove_based_on_RR','SPO2']
resample_dic1={'act':'mean', 'ill':'mean', 'var':'mean', 'post': 'last'}
resample_dic2={'W_act':'mean'}
file1=file_read(path,ID[0],day_list[0],filetype[0])
file1=read_rename(file1,sheet_name[0])
date1=next_day(file1['Time'],day_list[0])
date_time1=pd.DataFrame({'Date':date1,'Time':file1['Time']})
date_time1=pd.DatetimeIndex(pd.to_datetime(date_time1.Date+' '+date_time1.Time))
ECG=pd.DataFrame({'act':file1.ACT,'ill':file1.Illuminance,'var':file1.VAR
                  ,'post':file1.Posture})
ECG=ECG.set_index(date_time1)
ECG=ECG.resample('10s').mean()
ECG=ECG.fillna(method='ffill')
ECG=ECG.reset_index(inplace=False)
ECG=ECG.rename(columns={'index':'Time'})

#file2=file_read(path,ID[1],day_list[0],filetype[0])
#file2=read_rename(file2,sheet_name[1])
#date2=next_day(file2['Time'],day_list[0])
#date_time2=pd.DataFrame({'Date':date2,'Time':file2.Time})
#date_time2=pd.DatetimeIndex(pd.to_datetime(date_time2.Date+' '+date_time2.Time))
#ACT=pd.DataFrame({'W_act':file2.ACT})
#ACT=ACT.set_index(date_time2)
#ACT=ACT.resample('10s').mean()
#ACT=ACT.fillna(method='ffill')
#ACT=ACT.reset_index(inplace=False)
#ACT=ACT.rename(columns={'index':'Time'})

act_index=[0,100]
#act_ticks = ["0",str(100)]
post_index=([1,2,3,4,5])
post_ticks = ["Right","Supine","Left","Prone","Stand"]
#%%SpO2
resample_dic3={'O2':'mean', 'HR':'mean'}
file3=file_read(path,ID[2],day_list[0],filetype[1])
file3=read_rename(file3,sheet_name[3])
date3=next_day(file3['Time'],day_list[0])
date_time3=pd.DataFrame({'Date':date3,'Time':file3['Time']})
date_time3=pd.DatetimeIndex(pd.to_datetime(date_time3.Date+' '+date_time3.Time))
SpO2=pd.DataFrame({'Time':date_time3,'O2':file3.O2,'HR':file3.HR})
SpO2_10s=[SpO2.Time[i] for i in range(0,len(SpO2),10)]
SD_HR=HR_window(SpO2.HR,10)
SD_O2=HR_window(SpO2.O2,10)
STD_SpO2=pd.DataFrame({'SD_O2':SD_O2,'SD_HR':SD_HR})
STD_SpO2=STD_SpO2.set_index(pd.DatetimeIndex(SpO2_10s))
STD_SpO2=STD_SpO2.resample('10s').mean()
STD_SpO2=STD_SpO2.fillna(method='ffill')
STD_SpO2=STD_SpO2.reset_index(inplace=False)
STD_SpO2=STD_SpO2.rename(columns={'index':'Time'})
#%%解TD1
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
#interpretTD1=[5 for i in range(20)]
#score1=interpretTD1+score
#del score1[len(score1)-21:len(score1)-1]
TD1=pd.DataFrame({'Time':date_time_TD1,'Score':score})
TD1=TD1.dropna(axis=1,how='any')
TD12=TD1.drop_duplicates()
TD12=TD12.set_index(TD12.Time,inplace=False)
TD12=TD12.resample('10s').ffill()
del TD12['Time']
TD12=TD12.reset_index(inplace=False)
#stage_index=([1,2,3,4,5])
#stage_ticks = ["N3","N2","N1","REM","Wake"]
#%%combine data
#fig1=plt.figure(figsize=(20,20))
#fig1n=5
#fig1.add_subplot(fig1n,1,1)
#plt.title(str(day),fontsize=18,fontname="Arial")
#plt.plot(TD1.Time,TD1.Score)
#plt.yticks(stage_index,stage_ticks,fontsize=12,fontname="Arial")
#plt.xlim(SpO2.Time[0],SpO2.Time[len(SpO2)-1])
#plt.xticks(fontsize=12,fontname="Arial")
#plt.tick_params(axis='y',which='both',bottom=False, top=False,length = 0)
#fig1.add_subplot(fig1n,1,2)
#plt.plot(ECG.Time,ECG.act)
#plt.xlim(SpO2.Time[0],SpO2.Time[len(SpO2)-1])
#plt.ylim(0,20)
#plt.ylabel('Activity',fontname="Arial",fontsize=16)
#plt.xticks(fontsize=12,fontname="Arial")
#plt.yticks(fontsize=12,fontname="Arial")
#fig1.add_subplot(fig1n,1,3)
#plt.plot(ACT.Time,ACT.W_act)
#plt.yticks(act_index,act_ticks,fontname="Arial",fontsize=12)
#plt.xlim(SpO2.Time[0],SpO2.Time[len(SpO2)-1])
##plt.xlim(ECG.Time[0],ECG.Time[len(ECG)-1])
#plt.ylim(0,100)
#plt.ylabel('Activity',fontname="Arial",fontsize=16)
#plt.xticks(fontsize=12,fontname="Arial")
#fig1.add_subplot(fig1n,1,4)
#plt.plot(ECG.Time,ECG.post)
#plt.yticks(post_index,post_ticks,fontname="Arial",fontsize=12)
#plt.xlim(SpO2.Time[0],SpO2.Time[len(SpO2)-1])
#plt.xticks(fontsize=12,fontname="Arial")
#plt.tick_params(axis='y',which='both',bottom=False, top=False,length = 0)
#fig1.add_subplot(fig1n,1,4)
#plt.plot(SpO2_10s,SD_O2)
#plt.yticks(fontsize=12,fontname="Arial")
#plt.ylabel('Variability\nof oxigen',fontsize=16,fontname="Arial")
#plt.xlim(SpO2.Time[0],SpO2.Time[len(SpO2)-1])
#plt.xticks(fontsize=12,fontname="Arial")
#plt.ylim(0,2)
#fig1.add_subplot(fig1n,1,5)
#plt.plot(SpO2_10s,SD_HR)
#plt.yticks(fontsize=12,fontname="Arial")
#plt.ylabel('Variability\nof heart',fontsize=16,fontname="Arial")
#plt.xlim(SpO2.Time[0],SpO2.Time[len(SpO2)-1])
#plt.xticks(fontsize=12,fontname="Arial")
#plt.ylim(0,5)
#%%combine data
O2_HR=pd.merge(ECG,STD_SpO2,on='Time',how='outer')
combine=pd.merge(O2_HR,TD1,on='Time',how='outer')
combine=combine.set_index('Time', drop=True)
combine.Score=combine['Score'].fillna(5)
combine.to_excel(day+".xlsx",sheet_name='whole data')