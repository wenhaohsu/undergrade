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

#%% ACT & HR
path='C:\\Users\\Jonathan Chen\\Desktop\\收案data\\介入\\氣功\\黃孟粉\\第十九週\\HRV'
path2='C:\\Users\\Jonathan Chen\\Desktop\\收案data\\介入\\氣功\\黃孟粉\\第十九週\\spO2'
ID=['0397005b','01da0040']
day='20200619'

day_list=[day,datetime.strftime(datetime.strptime(day,'%Y%m%d')-timedelta(days=1),'%Y%m%d')]
filetype=['HRV','SPO2']
#insert_name='(有側睡枕)'
sheet_name=['HR&ACT','HRV_data_remove_based_on_RR','SPO2']
resample_dic1={'ACT':'mean', 'HR':'mean', 'VAR':'mean', 'Posture': 'last'}
file1=file_read(path,ID[0],day_list[0],filetype[0])
file1=read_rename(file1,sheet_name[0])
date1=next_day(file1['Time'],day_list[0])
date_time1=pd.DataFrame({'Date':date1,'Time':file1['Time']})
date_time1=pd.DatetimeIndex(pd.to_datetime(date_time1.Date+' '+date_time1.Time))
ECG=pd.concat([file1['ACT'],file1['HR']
          ,file1['VAR'],file1['Posture']],axis=1,ignore_index=False)
ECG=ECG.set_index(date_time1)
ECG=ECG.resample('10s').agg(resample_dic1)
ECG=ECG.reset_index(inplace=False)
ECG=ECG.rename(columns={'index':'Time'})

CACT_act=ECG['ACT'].fillna(method='ffill')
CACT_HR=ECG['HR'].fillna(method='ffill')
CACT_var=ECG['VAR'].fillna(method='ffill')
CACT_post=ECG['Posture'].fillna(method='ffill')
CACT=pd.DataFrame({'Act':CACT_act,'HR':CACT_HR,
                   'Var':CACT_var,'Post':CACT_post,'Time':ECG.Time})
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