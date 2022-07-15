#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  5 23:41:04 2020

@author: hao
"""

from datetime import datetime, timedelta
import pandas as pd
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()
import numpy as np
import matplotlib.pyplot as plt

def file_read(get_path,get_ID,get_day,get_filetype):
    return get_path+'\\'+get_ID.upper()+'_'+get_day+'('+get_filetype+').xlsx' 
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
def get_post(tilt,roll,Y_axis,Z_axis):
    state = []
    posture=[]
    method1=45
    method2=135
    for i in range(len(tilt)):
        if abs(tilt[i]) >= method1:
            posture.append(5)
            state.append(2)
        else:
            if abs(roll[i])<(method1) or abs(roll[i])>(method2):
                if Y_axis[i]>= 0:
                    posture.append(2) #right
                    state.append(1)
                else:
                    posture.append(3) #left
                    state.append(1)
            else:
                if Z_axis[i]>= 0:
                    posture.append(1) #supine
                    state.append(1)
                else:
                    posture.append(4) #prone
                    state.append(1)
    return posture,state
#%% ACT & HR
path='/Users/hao/Desktop'
path2='/Users/hao/Desktop'
ID=['0397005b','01da0040']
day='20200619'

day_list=[day,datetime.strftime(datetime.strptime(day,'%Y%m%d')-timedelta(days=1),'%Y%m%d')]
filetype=['HRV','SPO2']
#insert_name='(有側睡枕)'
sheet_name=['HR&ACT','HRV_data_remove_based_on_RR','SPO2']
resample_dic1={'ACT':'mean', 'HR':'mean', 'VAR':'mean', 'Posture': 'last','Posture2': 'last'}
file1=file_read(path,ID[0],day_list[0],filetype[0])
file1=read_rename(file1,sheet_name[0])
date1=next_day(file1['Time'],day_list[0])
date_time1=pd.DataFrame({'Date':date1,'Time':file1['Time']})
date_time1=pd.DatetimeIndex(pd.to_datetime(date_time1.Date+' '+date_time1.Time))
CACT_post2,CACT_state2=get_post(file1['tilt_derive'],file1['roll_derive'],file1['Y'],file1['Z'])
file1['Posture2']=CACT_post2
ECG=pd.concat([file1['ACT'],file1['HR']
          ,file1['VAR'],file1['Posture'],file1['Posture2']],axis=1,ignore_index=False)
ECG=ECG.set_index(date_time1)
ECG=ECG.resample('10s').agg(resample_dic1)
ECG=ECG.fillna(method='ffill')
ECG=ECG.reset_index(inplace=False)
ECG=ECG.rename(columns={'index':'Time'})
CACT=pd.DataFrame({'Act':ECG['ACT'],'HR':ECG['HR'],
                   'Var':ECG['VAR'],'Post':ECG['Posture'],'Posture2':ECG['Posture2'],'Time':ECG['Time']})
#%%SpO2
resample_dic3={'ACT':'mean', 'HR':'mean', 'O2':'mean'}
file3=file_read(path2,ID[1],day_list[0],filetype[1])
file3=read_rename(file3,sheet_name[2])
date3=next_day(file3['Time'],day_list[0])
date_time3=pd.DataFrame({'Date':date3,'Time':file3['Time']})
date_time3=pd.DatetimeIndex(pd.to_datetime(date_time3.Date+' '+date_time3.Time))
SpO2=pd.concat([file3['ACT'],file3['HR']
          ,file3['O2']],axis=1,ignore_index=False)
SpO2=SpO2.set_index(date_time3)
SpO2=SpO2.reset_index(inplace=False)
SpO2=SpO2.rename(columns={'index':'Time'})
O2=SpO2['O2'].fillna(method='ffill')
SpO2=pd.DataFrame({'O2':O2,'Time':SpO2.Time})

#%%combine data
combine=pd.merge(CACT,SpO2,on='Time',how='inner')
combine=combine.set_index("Time", drop=True)
combine.O2=combine['O2'].fillna(99)

#%% to excel
combine.to_excel(day+".xlsx",
              sheet_name='whole data')