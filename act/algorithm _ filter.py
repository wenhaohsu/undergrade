#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 16 10:27:15 2019

@author: hao
"""
#匯入函數
import pandas as pd
import scipy.stats as stats
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
import scipy.stats as sci
import numpy as np
import seaborn as sns
import os
import fnmatch
from sklearn import metrics
#%% 建立資料
#def build_file(file_path):
file_path='/Users/hao/Desktop/python/act/patch_wei/processeddata2output/'
date = '140415.xlsx'
score1 = pd.read_excel(file_path + date)
score1 = score1.dropna(axis=0, how='any')
score1 = score1.rename(columns={'Unnamed: 0':'time'})

#%%
def sleep_stage_ACT(act,thre):
    conscious=[]
    actsum=[]
    input_thre= thre
    for i in range(len(act)):             #整個時間軸的sliding window
        if i>=13 and i<=len(act)-14:      #時間長度夠的情況下
            Aact=sum(act[i-13:i-2])       #往前數4個epoch(120s)的總和
            Bact=sum(act[i+2:i+13])       #往後數4個epoch(120s)的總和
    #      print('Aact',Aact)
    #      print('Bact',Bact)
            act_now=float(act[i-1])+float(act[i])+float(act[i+1])
            act_critical=Aact+Bact+act_now#當下的1個epoch(30s)
            actsum.append(act_critical)   #計算act的總和
            if act_critical>input_thre:   #如果大於設定的threshold
                if Aact<12 and Bact<12:   #當往前或往後的epoch不足4個
                    conscious.append(1)   #判睡
                else:  
                    conscious.append(2)   #判醒
            else:
                conscious.append(1)       #判睡
        else:                             #如果window總長度不夠
            conscious.append(1)           #判睡
            actsum.append(0)              #活動量算0
    return conscious

def posture(spin):
    post = []
    for i in range(len(spin)):
        if spin[i] >=13 or spin[i] <= 2 :
            post.append(2)                 #stand
        else:
            post.append(1)                 #lie
    return post

def lie_time(file,post):
    stand_index = 0
    count_lie = 0
    for i in range(1,len(post)):
         if count_lie == 18:                #如果兩分鐘處於同狀態
             break
         if post[i] == 1 & post[i-1] == 1:  #躺下的時間需經過一個單位才算
             stand_index = i
             count_lie += 1
         elif post[i] == 2 & post[i-1] == 2:#如果起身，躺下時間重算
             count_lie = 0
#    time_to_lie = stand_index - count_lie
#    return file.index[time_to_lie]
    return stand_index

def sleep_time(stand_index,score):
    wake_index = 0
    count_sleep = 0
    for i in range(stand_index,len(score)):
        if count_sleep == 18:                #如果兩分鐘處於同狀態
            break
        if score[i] == 1 & score[i-1] == 1:  #睡著的時間需經過一個單位才算
            wake_index = i
            count_sleep += 1
        elif score[i] == 2 & score[i-1] == 2:#如果醒來，睡著時間要重算
            count_sleep = 0        
#    time_to_sleep = wake_index - count_sleep
#    return file.index[time_to_sleep]
    return  wake_index

def wake_time(wake_index,score):
    sleep_index = 0
    count_wake = 0
    for i in range(wake_index,len(score)):
        if count_wake == 18:                 #如果兩分鐘處於同狀態
            break
        if score[i] == 2 & score[i-1] == 2:  #醒來的時間需經過一個單位才算
            sleep_index = i
            count_wake += 1
        elif score[i] == 1 & score[i-1] == 1:#如果睡著，清醒時間要重算
            count_wake = 0
#    time_to_wake = sleep_index - count_wake
#    return file.index[time_to_wake]
    return sleep_index

def stand_time(sleep_index,post):
    lie_index = 0
    count_stand = 0
    for i in range(sleep_index,len(post)):
        if count_stand == 18:              #如果兩分鐘處於同狀態
            break
        if post[i] == 2 & post[i-1] == 2:  #起床的時間需經過一個單位才算
            lie_index = i
            count_stand += 1
        elif post[i] == 1 & post[i-1] == 1:#如果躺下，起床時間重算
            count_stand = 0
#    time_to_stand = lie_index - count_stand
#    return file.index[time_to_stand]
    return lie_index

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

def total_sleep(stand_index,final_lie_index,score):
    sleep_sec = 0
    for i in range(stand_index,final_lie_index):
        if score[i] == 1 & score[i-1] == 1:  #躺下的時間需經過一個單位才算
            sleep_sec += 1
    return sleep_sec
    

def sleep_efficiency(stand_index,final_lie_index,score):
    sleep_sec = 0
    for i in range(stand_index,final_lie_index):
        if score[i] == 1 & score[i-1] == 1:  #躺下的時間需經過一個單位才算
            sleep_sec += 1
    efficiency = (sleep_sec / (final_lie_index - stand_index)) * 100
    return efficiency



#%%
spin = score1['spin'].tolist()
post1 = posture(spin)
TRT1 = len(score1)
sleep_score = list(map(int,score1['score']))
lie1 = lie_time(score1,post1)
thre_try=73
sleep_act=sleep_stage_ACT(score1['ACT'],thre_try)
sleep1 = sleep_time(lie1, sleep_score)
wake1 = wake_time(sleep1,sleep_score)
stand1 = stand_time(wake1,post1)
final1 = final_stand(post1)
SL1 = (sleep1-lie1)
TST1 = (final1-lie1)
WASO1 = (wake1-sleep1)
SE1 = sleep_efficiency(lie1,final1,sleep_score)
print(SL1)
print(WASO1)
print(SE1)

#%% 
time = score1['time'].tolist()
act = score1['ACT'].tolist()
act_lie = act[lie1:final1]
mean_act = np.median(act_lie)
sd_act = np.std(act_lie)
act_CI = mean_act + 1.64*sd_act
act_thre = []
actsum = []
for i in range(len(act_lie)):
    act_thre.append(act_CI)
conscious2 = []
n = 2
for i in range(len(act)):
        if i>=n and i<=len(act)-(n+1):      #時間長度夠的情況下
            Aact=sum(act[i-n:i-1])
       #往前數4個epoch(120s)的總和
            Bact=sum(act[i+1:i+n])       #往後數4個epoch(120s)的總和
#            Bact=float(act[i]+1)
    #      print('Aact',Aact)
    #      print('Bact',Bact)
            act_now=float(act[i])
            act_critical=Aact+Bact+act_now#當下的1個epoch(30s)
            actsum.append(act_critical)   #計算act的總和
            if act_critical>act_CI:   #如果大於設定的threshold
                if Aact<n and Bact<n:   #當往前或往後的epoch不足4個
                    conscious2.append(1)   #判睡
                else:  
                    conscious2.append(2)   #判醒
            else:
                conscious2.append(1)       #判睡
        else:                             #如果window總長度不夠
            conscious2.append(1)           #判睡
            actsum.append(0)              #活動量算0
sleep2 = sleep_time(lie1, conscious2)
wake2 = wake_time(sleep2,conscious2)
stand2 = stand_time(wake2,post1)
SL2 = (sleep2 - lie1)
WASO2 = (wake2 - sleep2)
SE2 = sleep_efficiency(lie1,final1,conscious2) #問承翰哥
print(SL2)
print(WASO2)
print(SE2)



#%%

act_lie = np.array(act_lie)
rms_act = np.sqrt(np.mean(act_lie**2))
conscious3 = []
n = 4
for i in range(len(act)):
    if act[i] > rms_act:
        conscious3.append(2)
    else:
        conscious3.append(1)
sleep3 = sleep_time(lie1, conscious3)
wake3 = wake_time(sleep3,conscious3)
stand3 = stand_time(wake3,post1)
SL3 = (sleep3 - lie1)
WASO3 = (wake3 - sleep3)
SE3 = sleep_efficiency(lie1,final1,conscious3) #問承翰哥

wake_act2 = []
sleep_act2 = []
for i in range(len(score1)):
    if post1[i] == 2:
        wake_act2.append(act[i])
    else:
        sleep_act2.append(act[i])
Thre1=np.mean(wake_act2)-np.mean(sleep_act2)
conscious4=[act[i]-act[i-3] for i in range(len(act))]            
#plt.plot(conscious4)
state_test = []
for i in range(len(conscious4)):
    if conscious4[i] > Thre1:
        state_test.append(2)
    else:
        state_test.append(1)
#%%
#fig1 = plt.figure(figsize=(18,12))
#fig1.add_subplot(3,1,1)
##plt.subplots_adjust(hspace=1)
#plt.title(date.split('.xlsx')[0],fontsize=20)
#yy=np.array([1,2])
#plt.ytick = ['Sleep','Wake']
#x1 = time[lie1:final1]
#y1 = sleep_score[lie1:final1]
#plt.plot(x1,y1)
#plt.yticks(yy, plt.ytick)
#plt.xlim((time[lie1], time[final1]))
#plt.xticks([]) 
#plt.ylabel('Score by \n sleeptechcian')
#
#
#
#fig1.add_subplot(3,1,2)
#yy=np.array([1,2])
#plt.ytick = ['Sleep','Wake']
#y2 = sleep_act[lie1:final1]
#plt.yticks(yy, plt.ytick)
#plt.plot(x1,y2)
#plt.xlim((time[lie1], time[final1]))
#plt.xticks([]) 
#plt.ylabel('Score by \n method 1')
#
#fig1.add_subplot(3,1,3)
#y1_3 = act[lie1:final1]
#plt.xlim((time[lie1], time[final1]))
#plt.ylim([0,100])
#plt.plot(x1,y1_3)
#plt.subplots_adjust(hspace=0)
#plt.ylabel('Activity')
#%%
fig2 = plt.figure(figsize=(18,15))
fig2.add_subplot(6,1,1)
plt.subplots_adjust(hspace=0.1)
plt.title(date.split('.xlsx')[0],fontsize=20)
yy=np.array([1,2])
plt.ytick = ['Sleep','Wake']
x1 = time[lie1:final1]
y1 = sleep_score[lie1:final1]
plt.plot(x1,y1)
plt.yticks(yy, plt.ytick)
plt.xlim((time[lie1], time[final1]))
plt.xticks([]) 
plt.ylabel('Score by \n sleeptechcian')
#thre = 73
fig2.add_subplot(6,1,2)
yy=np.array([1,2])
plt.ytick = ['Sleep','Wake']
y2 = sleep_act[lie1:final1]
plt.yticks(yy, plt.ytick)
plt.plot(x1,y2)
plt.xlim((time[lie1], time[final1]))
plt.xticks([])
plt.ylabel('Score by \n threshold')
#thre = mean + 1.96std
fig2.add_subplot(6,1,4)
yy=np.array([1,2])
plt.ytick = ['Sleep','Wake']
y3 = conscious2[lie1:final1]
plt.plot(x1,y3)
plt.yticks(yy, plt.ytick)
plt.xlim((time[lie1], time[final1]))
plt.xticks([]) 
plt.ylabel('Score by \n mean+2SD')
#thre = RMS
fig2.add_subplot(6,1,3)
yy=np.array([1,2])
plt.ytick = ['Sleep','Wake']
y4 = conscious3[lie1:final1]
plt.yticks(yy, plt.ytick)
plt.xlim((time[lie1], time[final1]))
plt.plot(x1,y4)
plt.xticks([]) 
plt.ylabel('Score by \n Root mean square')

fig2.add_subplot(6,1,6)
y1_3 = act[lie1:final1]
plt.xlim((time[lie1], time[final1]))
plt.ylim([0,100])
plt.plot(x1,y1_3)
#plt.xticks([]) 
plt.ylabel('Activity')

fig2.add_subplot(6,1,5)
yy=np.array([1,2])
plt.ytick = ['Sleep','Wake']
y5 = state_test[lie1:final1]
plt.yticks(yy, plt.ytick)
plt.xlim((time[lie1], time[final1]))
plt.xticks([])
plt.ylabel('Score by \n test')
plt.plot(x1,y5)
#%%
#利用活動量作為醒睡的標準(threshold=55)
#在patch的資料中利用活動量做出新的predict後與TD1的資料做相關比較

#state_test = state_test[lie1:final1]
#plt.plot(x1,state_test)
