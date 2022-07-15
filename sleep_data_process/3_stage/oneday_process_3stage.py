#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 30 11:45:31 2020

@author: hao
"""

from datetime import datetime, timedelta
import pandas as pd
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
#def next_day(time,day):
#    date=[]
#    for i in range(len(time)):
#        if pd.to_datetime(time[i])>=pd.to_datetime('00:00:00') and pd.to_datetime(time[i]-1)<pd.to_datetime('23:59:59'):
#            day += 1
#            date.append(day)
#        else:
#            date.append(day)
#    return date
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
#%%
path='/Users/hao/Desktop/實驗資料/健康組/威儒'
ID=['0211005b','029b005c','012c0040']
day='20200110'
day_list=[day,str(int(day)-1)]
filetype=['HRV','SPO2']
sheet_name=['HR&ACT','ACT&Illuminance','HRV_data_remove_based_on_RR','SPO2']
resample_dic1={'C_act':'mean', 'ill':'mean', 'var':'mean', 'post': 'last'}
resample_dic2={'W_act':'mean'}#, 'Illuminance':'mean', 'VAR':'mean'}
data1=file_read(path,ID[0],day,filetype[0])
ECG_data=read_rename(data1,sheet_name[0])
data2=file_read(path,ID[1],day,filetype[0])
ACT_data=read_rename(data2,sheet_name[1])
date_time1=pd.DataFrame({'Date': [day for i in range(len(ECG_data['Time']))],'Time':ECG_data['Time']})
ECG_datetime=pd.DatetimeIndex(pd.to_datetime(date_time1.Date+' '+date_time1.Time))
ECG=pd.DataFrame({'C_act':ECG_data.ACT,'ill':ECG_data.Illuminance,'var':ECG_data.VAR
                  ,'post':ECG_data.Posture})
ECG=ECG.set_index(ECG_datetime)
ECG=ECG.resample('10s').mean()
ECG=ECG.fillna(method='ffill')
ECG=ECG.reset_index(inplace=False)
ECG=ECG.rename(columns={'index':'Time'})

#date_time2=pd.DataFrame({'Date': [day for i in range(len(ACT_data['Time']))],'Time':ACT_data['Time']})
#ACT_datetime=pd.DatetimeIndex(pd.to_datetime(date_time2.Date+' '+date_time2.Time))
#ACT=pd.DataFrame({'W_act':ACT_data.ACT})
#ACT=ACT.set_index(date_time2)
#ACT=ACT.resample('10s').agg(resample_dic2)
#ACT.W_act=ACT['W_act'].fillna(method='ffill')
#ACT=ACT.reset_index(inplace=False)
#ACT=ACT.rename(columns={'index':'Time'})
#%%
resample_dic3={'O2':'mean', 'HR':'mean'}#, 'O2':'mean'}
file3=file_read(path,ID[2],day_list[0],filetype[1])
file3=read_rename(file3,sheet_name[3])
date_time3=pd.DataFrame({'Date': [day for i in range(len(file3['Time']))],'Time':file3['Time']})
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
interpretTD1=[5 for i in range(10)]
score=interpretTD1+score
del score[len(score)-11:len(score)-1]
TD1=pd.DataFrame({'Time':date_time_TD1,'Score':score})
TD1=TD1.dropna(axis=1,how='any')
TD12=TD1.drop_duplicates()
TD12=TD12.set_index(TD12.Time,inplace=False)
TD12=TD12.resample('10s').ffill()
del TD12['Time']
TD12=TD12.reset_index(inplace=False)
#%%combine data
O2_HR=pd.merge(ECG,STD_SpO2,on='Time',how='outer')
combine=pd.merge(O2_HR,TD1,on='Time',how='outer')
#combine=pd.merge(ACT_com,TD1,on='Time',how='outer')
combine=combine.set_index('Time', drop=True)
combine.Score=combine['Score'].fillna(5)
combine.to_excel(day+"_2.xlsx",sheet_name='whole data')