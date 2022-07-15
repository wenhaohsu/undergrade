#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov  5 22:40:51 2019

@author: hao
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as md
import matplotlib.ticker as ticker
from datetime import datetime, timedelta
import math
import numpy as np

np.seterr(divide='ignore', invalid='ignore')
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()
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
def get_post(tilt,roll,Y_axis,Z_axis):
    state = []
    posture=[]
    method1=45
#    method2=60
    method2=135
#    method3=165
    for i in range(len(tilt)):
        if abs(tilt[i]) >= method1:
            posture.append(5)
            state.append(2)
        else:
            if abs(roll[i])>(method1) and abs(roll[i])<(method2):
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

def final_stand(post):
    get_final_stand = 0
    final_count_stand = 0
    for i in range(len(post)-1,0,-1):
        if final_count_stand == 18:        #如果三分鐘處於同狀態
            break
        if post[i] == 1 & post[i-1] == 1:  #躺下的時間需經過一個單位才算
            get_final_stand = i
            final_count_stand += 1
        elif post[i] == 2 & post[i-1] == 2:#如果起身，躺下時間重算
            get_final_stand = 0
    return get_final_stand
#判斷躺床時間
def lie_time(post):
    get_lie = 0
    count_lie = 0
    for i in range(1,len(post)):
         if count_lie == 18:                #如果三分鐘處於同狀態
             break
         if post[i] == 1 & post[i-1] == 1:  #躺下的時間需經過一個單位才算
             get_lie = i
             count_lie += 1
         elif post[i] == 2 & post[i-1] == 2:#如果起身，躺下時間重算
             count_lie = 0
    return get_lie

# 判斷站姿
def getTilt(v1,v2):
  return math.atan2(v1,v2)/math.pi*180

path='/Users/hao/Desktop'
ID=['0244005b']
day='20200110'
day_list=[day,str(int(day)-1)]
filetype=['HRV']
sheet_name=['HR&ACT','HRV_data_remove_based_on_RR']

#%%
file=file_read(path,ID[0],day_list[0],filetype[0])
file1=read_rename(file,sheet_name[0])
file2=read_rename(file,sheet_name[1])
date1=next_day(file1['Time'],day_list[0])
date_time1=pd.DataFrame({'Date':date1,'Time':file1['Time']})
date_time1=pd.DatetimeIndex(pd.to_datetime(date_time1.Date+' '+date_time1.Time))

#%%
data_len = len(file1)-1
data_from = 0
#CACT_data = CACT_data.rename(columns={'Unnamed: 0':'Time'})#將column取名為date
#CACT_time = CACT_data['Time'].tolist()
X_axis = np.array(file1['X'].tolist())
Y_axis = np.array(file1['Y'].tolist())
Z_axis = np.array(file1['Z'].tolist())
YZ_plane = np.sqrt(Y_axis**2+Z_axis**2)

CACT_tilt = [getTilt(X_axis[i],YZ_plane[i]) for i in range(len(file1))]
CACT_roll = [getTilt(Y_axis[i],Z_axis[i]) for i in range(len(file1))]
#%%

CACT_post,CACT_state=get_post(CACT_tilt,CACT_roll,Y_axis,Z_axis)
lietime=lie_time(CACT_state)
standtime=final_stand(CACT_state)
turn_over = [CACT_roll[i]-CACT_roll[i-1] for i in range(len(CACT_roll))]
#turn_over若為正為右翻，反之左翻
''''''
fig1 = plt.figure(figsize=(20,15))
fig1_n=6
fig1.add_subplot(fig1_n,1,1)
yy4=np.array([-1,0,1])
my_yticks3 = ["-1","X","1"]
plt.yticks(yy4, my_yticks3,fontname="Arial",fontsize=14)
plt.xticks([])
plt.plot(X_axis)
plt.xlim(data_from,data_len) 
plt.ylim(-1,1)
plt.tick_params(axis='y',which='both',bottom=False, top=False,length = 0)
fig1.add_subplot(fig1_n,1,2)
plt.xticks([])
yy4=np.array([-1,0,1])
my_yticks3 = ["-1","Y","1"]
plt.yticks(yy4, my_yticks3,fontname="Arial",fontsize=14)
plt.plot(Y_axis)
plt.xlim(data_from,data_len) 
plt.ylim(-1,1)
plt.tick_params(axis='y',which='both',bottom=False, top=False,length = 0)
fig1.add_subplot(fig1_n,1,3)
yy4=np.array([-1,0,1])
my_yticks3 = ["-1","Z","1"]
plt.yticks(yy4, my_yticks3,fontname="Arial",fontsize=14)
plt.xticks([])
plt.plot(Z_axis)
plt.xlim(data_from,data_len) 
plt.ylim(-1,1)
plt.tick_params(axis='y',which='both',bottom=False, top=False,length = 0)
fig1.add_subplot(fig1_n,1,4)
yy4=np.array([-90,0,90])
my_yticks3 = ["-90˚","Tilt","90˚"]
plt.yticks(yy4, my_yticks3,fontname="Arial",fontsize=14)
plt.xticks([])
plt.plot(CACT_tilt)
plt.xlim(data_from,data_len) 
plt.ylim(-90,90)
plt.tick_params(axis='y',which='both',bottom=False, top=False,length = 0)
fig1.add_subplot(fig1_n,1,5)
yy4=np.array([-180,0,180])
my_yticks3 = ["-180˚","Roll","180˚"]
plt.yticks(yy4, my_yticks3,fontname="Arial",fontsize=14)
plt.xticks([])
plt.plot(date_time1,CACT_roll)
plt.xlim(date_time1[0],date_time1[-1])
plt.ylim(-180,180)
plt.tick_params(axis='y',which='both',bottom=False, top=False,length = 0)
fig1.add_subplot(fig1_n,1,6)
plt.plot(date_time1,CACT_post)
plt.plot(date_time1[lietime:standtime],CACT_post[lietime:standtime])
plt.xlim(date_time1[0],date_time1[-1]) 
yy=np.array([1,2,3,4,5])
my_yticks = ["Supine","Right","Left","Prone","Stand"]
plt.gca().yaxis.set_major_locator(plt.NullLocator())
plt.xticks(fontname="Arial",fontsize=14)
plt.yticks(yy, my_yticks,fontname="Arial",fontsize=14)
plt.tick_params(axis='y',which='both',bottom=False, top=False,length = 0)
#%%
#posture2=[]
#Time1=pd.to_timedelta(file1.Time)
#Time2=pd.to_timedelta(file2.Time)
#for i in range(len(Time2)):
#    time_array=np.array(Time1)
#    diff_select=abs(time_array-Time2[i])
#    time_select=np.where(diff_select==min(abs(time_array-Time2[i])))
#    posture2.append(((pd.Series(CACT_post).iloc[time_select]).values)[0])
#file1['Posture2']=CACT_post
#file2['Posture2']=posture2
##print(file2)
##file1.to_excel(day+"HRV_2.xlsx",sheet_name='Posture_HRV')
#file2.to_excel(day+"HRV_2.xlsx",sheet_name='Posture_HRV')