#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 18 21:29:13 2020

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
def sleep_wake_score(score):
    conscious=[]
    for i in range(len(score)):
        if score[i] == 5:
            conscious.append(1)
        else:
            conscious.append(0)
    return conscious
#%% ACT & HR
path='/Users/hao/Desktop/實驗資料/健康組/嘉駿'
ID=['025b005b','0101005c','00d4040']
day='20200428'
day_list=[day,datetime.strftime(datetime.strptime(day,'%Y%m%d')-timedelta(days=1),'%Y%m%d')]
filetype=['HRV','SPO2']
sheet_name=['HR&ACT','ACT&Illuminance','HRV_data_remove_based_on_RR','SPO2']
resample_dic1={'act':'mean', 'HR':'mean', 'var':'mean', 'post': 'last'}
resample_dic2={'W_act':'mean'}
file1=file_read(path,ID[0],day_list[0],filetype[0])
file1=read_rename(file1,sheet_name[0])
date1=next_day(file1['Time'],day_list[0])
date_time1=pd.DataFrame({'Date':date1,'Time':file1['Time']})
date_time1=pd.DatetimeIndex(pd.to_datetime(date_time1.Date+' '+date_time1.Time))
ECG=pd.DataFrame({'act':file1.ACT,'HR':file1.HR,'var':file1.VAR
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
date_time_1 = date_time_TD1.drop_duplicates()
#interpret=11
#interpretTD1=[5 for i in range(interpret)]
#score1=interpretTD1+score
#del score1[len(score1)-(interpret+1):len(score1)-1]
TD1=pd.DataFrame({'Time':date_time_TD1,'Score':score})
TD1=TD1.dropna(axis=1,how='any')
TD12=TD1.drop_duplicates()
TD12=TD12.set_index(TD12.Time,inplace=False)
TD12=TD12.resample('10s').ffill()
del TD12['Time']
TD12=TD12.reset_index(inplace=False)

#%%combine data
combine=pd.merge(ECG,TD1,on='Time',how='inner')
combine.Score=combine['Score'].fillna(5)
#%%
n2=2
yy=[0,1]
my_yticks7 = ["Sleep","Wake"]
fig3=plt.figure(figsize=(15,10))
fig3.add_subplot(n2,1,2)
plt.plot(combine.Time,combine.act)
plt.yticks(fontname="Arial",fontsize=12)
plt.xlim(combine.Time[0],combine.Time[len(combine.Time)-1])
plt.ylim(0,max(combine.act))
plt.ylabel('Activity',fontname="Arial",fontsize=16)
plt.xticks(fontname="Arial",fontsize=12)
fig3.add_subplot(n2,1,1)
plt.plot(combine.Time,sleep_wake_score(combine.Score))
#plt.yticks(yy,my_yticks7,fontname="Arial",fontsize=12)
plt.xlim(combine.Time[0],combine.Time[len(combine.Time)-1])
plt.xticks(fontname="Arial",fontsize=12)
plt.ylabel('Scored by TD1',fontname="Arial",fontsize=16)
plt.tick_params(axis='y',which='both',bottom=False,top=False,length=0)
plt.title('Compare activity with TD1 score',fontname="Arial",fontsize=18)
plt.tight_layout()
#%%
combine=combine.set_index('Time', drop=True)
combine.to_excel(day+".xlsx",sheet_name='whole data')