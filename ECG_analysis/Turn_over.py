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
from datetime import datetime
import math
import numpy as np
np.seterr(divide='ignore', invalid='ignore')
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()
def file_read(get_path,get_ID,get_day,get_filetype):
    return get_path+'/'+get_ID.upper()+'_'+get_day+'('+get_filetype+').xlsx'

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
#定義沒有配戴的時間
#def getNonWearingTime(acttime,threshold):
#  nonweartime=[]
#  for i in range(len(acttime)):
#    if i!=len(acttime)-1:
#      if transStringTodatetimeraw(acttime[i+1])-transStringTodatetimeraw(acttime[i])>threshold:
#        nonweartime.append(str(acttime[i]).replace("/","-")+"~"+str(acttime[i+1]).replace("/","-"))
#  return nonweartime

# 判斷站姿
def getTilt(v1,v2):
  return math.atan2(v1,v2)/math.pi*180
def getRoll(v1,v2):
  return math.atan2(v1,v2)/math.pi*360
path='/Users/hao/Desktop/實驗資料/健康組/名仁'
ID='0211005b'
ID2='019a005c'
day='20200227'
filetype='HRV'
data=file_read(path,ID,day,filetype)
data2=file_read(path,ID2,day,filetype)
CACT_data = pd.read_excel(data,sheet_name='HR&ACT')
WACT_data = pd.read_excel(data2,sheet_name='ACT&Illuminance')
#%%
data_len = len(CACT_data)-1
data_from = 0
CACT_data = CACT_data.rename(columns={'Unnamed: 0':'Time'})#將column取名為date
CACT_time = CACT_data['Time'].tolist()
CACT_act = np.array(CACT_data['ACT'])
CACT_illuminance=np.array(CACT_data["Illuminance"])
CACT_var=np.array(CACT_data["VAR"])
X_axis = np.array(CACT_data['X'].tolist())
Y_axis = np.array(CACT_data['Y'].tolist())
Z_axis = np.array(CACT_data['Z'].tolist())
YZ_plane = np.sqrt(Y_axis**2+Z_axis**2)
#xs = [datetime.strptime(i, '%H:%M:%S') for i in Time]

CACT_tilt = [getTilt(X_axis[i],YZ_plane[i]) for i in range(len(CACT_data))]
CACT_roll = [getTilt(Y_axis[i],Z_axis[i]) for i in range(len(CACT_data))]
#%%
data_len2 = len(WACT_data)-1
WACT_data = WACT_data.rename(columns={'Unnamed: 0':'Time'})#將column取名為date
WACT_time = WACT_data['Time'].tolist()
WACT_act = np.array(WACT_data['ACT'])
WACT_illuminance=np.array(WACT_data["Illuminance"])
CACT_var=np.array(CACT_data["VAR"])
xs = [datetime.strptime(i, '%H:%M:%S') for i in CACT_time]
#%%

def get_post(tilt,roll):
    state = []
    posture=[]
    method =45
    for i in range(len(tilt)):
        if tilt[i] >= method or tilt[i] <= -(method):
            posture.append(5)
            state.append(2)
        else:
            if roll[i]<(method) and roll[i]> -(method):
                if Y_axis[i]>= 0:
                    posture.append(1) #right
                    state.append(1)
                else:
                    posture.append(3) #left
                    state.append(1)
            else:
                if Z_axis[i]>= 0:
                    posture.append(2) #supine
                    state.append(1)
                else:
                    posture.append(4) #prone
                    state.append(1)
    return posture,state

#ax=plt.gca()
#ax.xaxis.set_major_formatter(md.DateFormatter('%H:%M'))#將時間做表轉為一個小時一個點
#ax.xaxis.set_major_locator(md.HourLocator())
CACT_post,CACT_state=get_post(CACT_tilt,CACT_roll)
#thre1=np.mean(act)+1.96*np.std(act)
#state2=[]
#for i in range(len(act)):
#    if act[i]>thre1:
#        state2.append(2)
#    else:
#        state2.append(1)
lietime=lie_time(CACT_state)
standtime=final_stand(CACT_state)
turn_over = [CACT_roll[i]-CACT_roll[i-1] for i in range(len(CACT_roll))]
#turn_over2 = [roll[i]-roll[i-2] for i in range(len(roll))]
#turn_over3 = [roll[i]-roll[i-3] for i in range(len(roll))]
#turn_over若為正為右翻，反之左翻
fig1 = plt.figure(figsize=(20,20))
fig1_n=2  
fig1.add_subplot(fig1_n,1,1)
yy4=np.array([-1,0,1])
my_yticks3 = ["-1","X","1"]
plt.yticks(yy4, my_yticks3)
#plt.xticks([])
plt.plot(xs,X_axis)
#plt.xlim(data_from,data_len) 
plt.ylim(-1,1)
#fig1.add_subplot(fig1_n,1,2)
#plt.xticks([])
#yy4=np.array([-1,0,1])
#my_yticks3 = ["-1","Y","1"]
#plt.yticks(yy4, my_yticks3)
#plt.plot(Y_axis)
#plt.xlim(data_from,data_len) 
#plt.ylim(-1,1)
#fig1.add_subplot(fig1_n,1,3)
#yy4=np.array([-1,0,1])
#my_yticks3 = ["-1","Z","1"]
#plt.yticks(yy4, my_yticks3)
#plt.xticks([])
#plt.plot(Z_axis)
#plt.xlim(data_from,data_len) 
#plt.ylim(-1,1)
#fig1.add_subplot(fig1_n,1,4)
#yy4=np.array([-90,0,90])
#my_yticks3 = ["-90˚","Tilt","90˚"]
#plt.yticks(yy4, my_yticks3)
#plt.xticks([])
#plt.plot(CACT_tilt)
#plt.xlim(data_from,data_len) 
#plt.ylim(-90,90)
#fig1.add_subplot(fig1_n,1,5)
#plt.xticks([])
#plt.plot(CACT_post)
#plt.xlim(data_from,data_len) 
#yy=np.array([1,2,3,4,5])
#my_yticks = ["Right","Supine","Left","Prone","Stand"]
#plt.yticks(yy, my_yticks)
#fig1.add_subplot(fig1_n,1,6)
#yy4=np.array([-180,0,180])
#my_yticks3 = ["-180˚","Roll","180˚"]
#plt.yticks(yy4, my_yticks3)
#plt.xticks([])
#plt.plot(xs,CACT_roll)
#plt.plot(xs[lietime:standtime],CACT_roll[lietime:standtime])
#plt.xlim(xs[data_from],xs[data_len]) 
#plt.ylim(-180,180)
#fig1.add_subplot(fig1_n,1,7)
##ax=plt.gca()
#ax.xaxis.set_major_formatter(md.DateFormatter('%H:%M'))#將時間做表轉為一個小時一個點
#ax.xaxis.set_major_locator(md.HourLocator())
#plt.plot(turn_over)
#plt.plot(turn_over[lietime:standtime])
#yy3=np.array([-360,0,360])
#my_yticks2 = ["Left","Turn over","Right"]
#plt.xlim(xs[data_from],xs[data_len]) 
#plt.ylim(-360,360)
#plt.yticks(yy3, my_yticks2)

#%%

#fig2 = plt.figure(figsize=(20,20))
#img2_n=3
#fig2.add_subplot(img2_n,1,2)
#plt.plot(CACT_time,CACT_act)
#plt.xlim(CACT_time[data_from],CACT_time[data_len])
#plt.xticks([])
#plt.ylim(0,100)
#plt.ylabel('CACT act')
##fig2.add_subplot(img2_n,1,4)
##plt.plot(CACT_time,CACT_illuminance)
##plt.xlim(CACT_time[data_from],CACT_time[data_len])
##plt.ylabel('CACT illuminance')
#fig2.add_subplot(img2_n,1,1)
#plt.plot(WACT_time,WACT_act)
#plt.xlim(WACT_time[data_from],WACT_time[data_len2])
#plt.xticks([])
#plt.ylim(0,200)
#plt.ylabel('WACT act')
##fig2.add_subplot(img2_n,1,3)
##plt.plot(WACT_time,WACT_illuminance)
##plt.xlim(WACT_time[data_from],WACT_time[data_len2])
##plt.xticks([])
##plt.ylabel('WACT illuminance')
#fig2.add_subplot(img2_n,1,3)
#yy4=np.array([-1,0,1])
#my_yticks3 = ["-1","X","1"]
#plt.yticks(yy4, my_yticks3)
##plt.xticks([])
#plt.plot(CACT_time,X_axis)
#plt.xlim(CACT_time[data_from],CACT_time[data_len])
#plt.ylim(-1,1)
#%%
#mean_CACT=np.mean(CACT_act)
#print(mean_CACT)
#mean_WACT=np.mean(WACT_act)
#print(mean_WACT)
