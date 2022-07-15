#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Dec  7 21:17:29 2019

@author: hao
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as md
from datetime import datetime

#file_path = '/Users/hao/Desktop/python/ECG_analysis/ECG_identifier/'
data = '019A005B_20191205(HRV).xlsx' #用ECG identify的程式抓下來的資料
data2 = '018E005C_20191205(ACT).xlsx'
ECG_data = pd.read_excel(data,sheet_name='data')
ACT_data = pd.read_excel(data2,sheet_name='data')
#%%
#ECG_data.reset_index(inplace=True)#把index轉為其中一個column
ECG_data = ECG_data.rename(columns={'Unnamed: 0':'Time'})#將column取名為date
ECG_data.set_index("Time",inplace=False)
ACT_data = ACT_data.rename(columns={'Unnamed: 0':'Time'})
ACT_data.set_index("Time",inplace=False)
#%%
Time = ECG_data['Time']
xs = [datetime.strptime(i, '%H:%M:%S') for i in Time]
Time2 = ACT_data['Time']
xs2 = [datetime.strptime(i, '%H:%M:%S') for i in Time2]
ACT = ECG_data['ACT']
ACT2 = ACT_data['ACT']
#%%
def lain(posture):
    post = []
    for i in range(len(posture)):
        if posture[i]<0.8 and posture[i]>-0.8:
            post.append(1)
        else:
            post.append(2)
    return post
def lie_time(post):
    get_lie = 0
    count_lie = 0
    for i in range(1,len(post)):
        if count_lie == 18:                #如果兩分鐘處於同狀態
            break
        if post[i] == 1 & post[i-1] == 1:  #躺下的時間需經過一個單位才算
            get_lie = i
            count_lie += 1
        elif post[i] == 2 & post[i-1] == 2:#如果起身，躺下時間重算
            count_lie = 0
    return get_lie
def final_stand(post):
    final_lie_index = 0
    final_count_stand = 0
    for i in range(len(post)-1,0,-1):
        if final_count_stand == 18:        #如果兩分鐘處於同狀態
            break
        if post[i] == 1 & post[i-1] == 1:  #躺下的時間需經過一個單位才算
            final_lie_index = i
            final_count_stand += 1
        elif post[i] == 2 & post[i-1] == 2:#如果起身，躺下時間重算
            final_lie_index = 0
    return final_lie_index


X1 = ECG_data['Y']
X2 = ACT_data['Y']
Lain1 = lain(X1)
Lain2 = lain(X2)
Lie_down1 = lie_time(Lain1)
Lie_down2 = lie_time(Lain2)
Final1 = final_stand(Lain1)
Final2 = final_stand(Lain2)


fig1 = plt.figure(figsize=(18,15))
fig1.add_subplot(2,1,1)
xs = Time[Lie_down1:Final1]
y1 = Lain1[Lie_down1:Final1]
ax=plt.gca()
ax.xaxis.set_major_formatter(md.DateFormatter('%H'))#將時間做表轉為一個小時一個點
ax.xaxis.set_major_locator(md.HourLocator())
plt.plot(xs,y1)

fig1.add_subplot(2,1,2)
xs2 = Time2[Lie_down2:Final2]
y2 = Lain2[Lie_down2:Final2]
ax=plt.gca()
ax.xaxis.set_major_formatter(md.DateFormatter('%H'))
ax.xaxis.set_major_locator(md.HourLocator())
plt.plot(xs2,y2)

#fig1.add_subplot(4,1,3)
#y3 = LF_percent[0:len(LF_percent)]
#ax=plt.gca()
#ax.xaxis.set_major_formatter(md.DateFormatter('%H'))
#ax.xaxis.set_major_locator(md.HourLocator())
#plt.plot(xs2, y3)
#
#fig1.add_subplot(4,1,4)
#y4 = RR[0:len(RR)]
#ax=plt.gca()
#ax.xaxis.set_major_formatter(md.DateFormatter('%H'))
#ax.xaxis.set_major_locator(md.HourLocator())
#plt.plot(xs2, y4)