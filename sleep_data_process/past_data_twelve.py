#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar  8 19:08:30 2020

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
        ('Arousal' in Sleepstage) or ('Lights ' in Sleepstage)
        score='nan'
    return score
#%% ACT & HR
path='/Users/hao/Desktop/實驗資料/健康組/品雯/不能用'
ID=['019a005b']#,'029c005c','00ff0040']
day='20191210'
day_list=[day,str(int(day)-1)]
filetype=['HRV','SPO2']
#sheet_name=['HR&ACT','ACT&Illuminance','HRV_data_remove_based_on_RR','SPO2']
#resample_dic1={'ACT':'mean', 'HR':'mean', 'VAR':'mean'}
#resample_dic2={'ACT':'mean', 'Illuminance':'mean', 'VAR':'mean'}
#file1=file_read(path,ID[0],day_list[0],filetype[0])
#file1=read_rename(file1,sheet_name[0])
#date1=next_day(file1['Time'],day_list[0])
#date_time1=pd.DataFrame({'Date':date1,'Time':file1['Time']})
#date_time1=pd.DatetimeIndex(pd.to_datetime(date_time1.Date+' '+date_time1.Time))
#ECG=pd.concat([file1['ACT'],file1['HR']
#          ,file1['VAR']],axis=1,ignore_index=False)
#ECG=ECG.set_index(date_time1)
#ECG=ECG.resample('10s').agg(resample_dic1)
#ECG=ECG.reset_index(inplace=False)
#ECG=ECG.rename(columns={'index':'Time'})
#
#CACT_act=ECG['ACT'].fillna(method='ffill')
#CACT_ill=ECG['HR'].fillna(method='ffill')
#CACT_var=ECG['VAR'].fillna(method='ffill')
#CACT=pd.DataFrame({'ACT':CACT_act,'HR':CACT_ill,
#                   'var':CACT_var,'Time':ECG.Time})

#%%
sheet_name=['HR&ACT','ACT&Illuminance','HRV_data_remove_based_on_RR','SPO2']
resample_dic1={'ACT':'mean', 'Illuminance':'mean', 'VAR':'mean', 'Posture': 'last'}
file1=file_read(path,ID[0],day_list[0],filetype[0])
file1=read_rename(file1,sheet_name[0])
date1=next_day(file1['Time'],day_list[0])
date_time1=pd.DataFrame({'Date':date1,'Time':file1['Time']})
date_time1=pd.DatetimeIndex(pd.to_datetime(date_time1.Date+' '+date_time1.Time))
ECG=pd.concat([file1['ACT'],file1['Illuminance']
          ,file1['VAR'],file1['Posture']],axis=1,ignore_index=False)
ECG=ECG.set_index(date_time1)
ECG=ECG.resample('10s').agg(resample_dic1)
ECG=ECG.reset_index(inplace=False)
ECG=ECG.rename(columns={'index':'Time'})
CACT_act=ECG['ACT'].fillna(method='ffill')
CACT_ill=ECG['Illuminance'].fillna(method='ffill')
CACT_var=ECG['VAR'].fillna(method='ffill')
CACT_post=ECG['Posture'].fillna(method='ffill')
CACT=pd.DataFrame({'C_Act':CACT_act,'C_Illuminance':CACT_ill,
                   'C_Var':CACT_var,'C_Post':CACT_post,'Time':ECG.Time})

#%%SpO2
#resample_dic3={'ACT':'mean', 'HR':'mean', 'O2':'mean'}
#file3=file_read(path,ID[2],day_list[0],filetype[1])
#file3=read_rename(file3,sheet_name[3])
#date3=next_day(file3['Time'],day_list[0])
#date_time3=pd.DataFrame({'Date':date3,'Time':file3['Time']})
#date_time3=pd.DatetimeIndex(pd.to_datetime(date_time3.Date+' '+date_time3.Time))
#SpO2=pd.concat([file3['ACT'],file3['HR']
#          ,file3['O2']],axis=1,ignore_index=False)
#SpO2=SpO2.set_index(date_time3)
#SpO2=SpO2.resample('10s').agg(resample_dic3)
#SpO2=SpO2.reset_index(inplace=False)
#SpO2=SpO2.rename(columns={'index':'Time'})
#O2=SpO2['O2'].fillna(method='ffill')
#SpO2_ACT=SpO2['ACT'].fillna(method='ffill')
#PPG=SpO2['HR'].fillna(method='ffill')
#SpO2=pd.DataFrame({'O2':O2,'PPG':PPG,'Time':SpO2.Time})
#%%解TD1
name='1210'
data=path+'/'+name+'.txt'
resample_dic2={'Score':'mean'}
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
TD1=TD1.dropna(axis=1,how='any')
TD12=TD1.drop_duplicates()
TD12=TD12.set_index(TD12.Time,inplace=False)
TD12=TD12.resample('10s').ffill()
del TD12['Time']
TD12=TD12.reset_index(inplace=False)
#print(TD12)
#%%combine data
#ACT_com=pd.merge(CACT,WACT,on='Time',how='inner')
#Sleep_wake=pd.merge(ACT_com,SpO2,on='Time',how='outer')
combine=pd.merge(CACT,TD12,on='Time',how='outer')
#combine=pd.merge(Sleep_wake,TD1,on='Time',how='outer')
combine=combine.set_index("Time", drop=True)
combine.Score=combine['Score'].fillna(5)
#combine.O2=combine['O2'].fillna(99)
#combine.PPG=combine['PPG'].fillna(np.mean(PPG))
combine.to_excel(day+".xlsx",
              sheet_name='whole data')
#%%