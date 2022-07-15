#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 11 20:36:33 2020

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
#%% 基本呼叫名稱
path='/Users/hao/Desktop/實驗資料/健康組/昕緣'
ID=['0358005b','029c005c']
day='20200424'
day_list=[day,str(int(day)+1)]
filetype=['HRV','SPO2']
sheet_name=['HR&ACT','ACT&Illuminance','HRV_data_remove_based_on_RR']
resample_dic={'ACT':'mean', 'Illuminance':'mean', 'VAR':'mean', 'Posture': 'last'}
#%%讀取資料與合併
data1_1=file_read(path,ID[0],day_list[0],filetype[0])
ECG_data_1=read_rename(data1_1,sheet_name[0])
data1_2=file_read(path,ID[0],day_list[1],filetype[0])
ECG_data_2=read_rename(data1_2,sheet_name[0])
data2_1=file_read(path,ID[1],day_list[0],filetype[0])
ACT_data_1=read_rename(data2_1,sheet_name[1])
data2_2=file_read(path,ID[1],day_list[1],filetype[0])
ACT_data_2=read_rename(data2_2,sheet_name[1])

#%%把日期跟時間做合併，圖才不會畫錯
date_time1_1=pd.DataFrame({'Date': [day_list[0] for i in range(len(ECG_data_1['Time']))],'Time':ECG_data_1['Time']})
ECG_datetime1=pd.DatetimeIndex(pd.to_datetime(date_time1_1.Date+' '+date_time1_1.Time))
ECG_1=pd.concat([ECG_data_1['ACT'],ECG_data_1['Illuminance']
          ,ECG_data_1['VAR'],ECG_data_1['Posture']],axis=1,ignore_index=False)
ECG_1=ECG_1.set_index(ECG_datetime1)
ECG_1=ECG_1.resample('10s').agg(resample_dic)
date_time1_2=pd.DataFrame({'Date': [day_list[1] for i in range(len(ECG_data_2['Time']))],'Time':ECG_data_2['Time']})
ECG_datetime2=pd.DatetimeIndex(pd.to_datetime(date_time1_2.Date+' '+date_time1_2.Time))
ECG_2=pd.concat([ECG_data_2['ACT'],ECG_data_2['Illuminance']
          ,ECG_data_2['VAR'],ECG_data_2['Posture']],axis=1,ignore_index=False)
ECG_2=ECG_2.set_index(ECG_datetime2)
ECG_2=ECG_2.resample('10s').agg(resample_dic)
ECG=pd.concat([ECG_1,ECG_2],axis=0,ignore_index=False)

date_time2_1=pd.DataFrame({'Date': [day_list[0] for i in range(len(ACT_data_1['Time']))],'Time':ACT_data_1['Time']})
ACT_datetime1=pd.DatetimeIndex(pd.to_datetime(date_time2_1.Date+' '+date_time2_1.Time))
ACT_1=pd.concat([ACT_data_1['ACT'],ACT_data_1['Illuminance']
          ,ACT_data_1['VAR'],ACT_data_1['Posture']],axis=1,ignore_index=False)
ACT_1=ACT_1.set_index(ACT_datetime1)
ACT_1=ACT_1.resample('10s').agg(resample_dic)
date_time2_2=pd.DataFrame({'Date': [day_list[1] for i in range(len(ACT_data_2['Time']))],'Time':ACT_data_2['Time']})
ACT_datetime2=pd.DatetimeIndex(pd.to_datetime(date_time2_2.Date+' '+date_time2_2.Time))
ACT_2=pd.concat([ACT_data_2['ACT'],ACT_data_2['Illuminance']
          ,ACT_data_2['VAR'],ACT_data_2['Posture']],axis=1,ignore_index=False)
ACT_2=ACT_2.set_index(ACT_datetime2)
ACT_2=ACT_2.resample('10s').agg(resample_dic)
ACT=pd.concat([ACT_1,ACT_2],axis=0,ignore_index=False)
#%% 進行補點
ACT_fill=ACT['ACT'].fillna(method='ffill')
ECG_fill=ECG['ACT'].fillna(method='ffill')
state_1=[]
for i in range(len(ACT)):
    if ACT_fill[i] > 5:
        state_1.append(2)
    else:
        state_1.append(1)
state_2=[]
for i in range(len(ECG)):
    if ECG_fill[i] > 5:
        state_2.append(2)
    else:
        state_2.append(1)

fig1=plt.figure(figsize=(20,20))
fig1.add_subplot(2,1,1)
plt.plot(state_1)
fig1.add_subplot(2,1,2)
plt.plot(state_2)

#  conscious1=filter_conscious(s_w,act_time,datetime.timedelta(0,wake_second),datetime.timedelta(0,sleep_second))
#  con1=conscious1.copy()
#  conscious2=filter_conscious(con1,act_time,datetime.timedelta(0,20),datetime.timedelta(0,60))
#  con2=conscious2.copy()
#  conscious3=filter_conscious(con2,act_time,datetime.timedelta(0,60),datetime.timedelta(0,180))
#  con3=conscious3.copy()
