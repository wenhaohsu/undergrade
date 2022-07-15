#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 14 23:49:05 2020

@author: chenghan
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime



def get_mode(arr):
    mode = []
    arr_appear = dict((a, arr.count(a)) for a in arr)
    if max(arr_appear.values()) == 1:  # 如果最大的出現為1
        return  # 則沒有眾數
    else:
        for k, v in arr_appear.items():  # 否則，出現次數最大的數字，就是眾數
            if v == max(arr_appear.values()):
                mode.append(k)
    return mode

def getstate_filter(state,window_size):#window_size決定你的過濾窗格大小，使用奇數
    window=[]
    state_len=window_size+1
    window_epoch=window_size//2
    for i in range(len(state)):
        if i < window_size or i > len(state)-state_len:
            window.append(1)
        else:
            state_sum=sum(state[i-window_epoch:i+window_epoch]) 
            if state_sum>=window_epoch:
                window.append(1)
            else:
                window.append(0)
    return window 







filename='CHGH002.txt'#'01110040_20200112(SPO2).xlsx'
rawtxt=''

Threshold=3
Activity_Threshold=2
Duration_Time=75


if '.xls' in filename:
    xls = pd.ExcelFile(filename)
    sheetname='SPO2'#input("Please enter sheetname: ")
    sheetX = xls.parse(sheetname)
    sheetkeys=sheetX.keys()
    sheetX=sheetX.set_index(sheetkeys[0])
    data_df=sheetX
    
elif '.txt' in filename:
    with open(filename, 'r') as f:
        text = []
        data_dic={}
        for line in f:
            text.append(line)
        for  i in range(len(text)):
            text[i]=text[i].replace("\n","")
            templist=text[i].split(",")
            
            try:
                timeformat='%Y-%m-%d %H:%M:%S'
                datetime.strptime(templist[0],timeformat)
                data_dic[templist[0]]={'O2':int(templist[1]),'HR':int(templist[2]),'ACT':float(templist[3])}
            except:
                print(templist)
                continue
    data_df=pd.DataFrame.from_dict(data_dic).T
elif rawtxt!='':
    rawtxt=rawtxt.replace("/","-")
    rawlist=rawtxt.split("\r\n")
    for  i in range(len(rawlist)):
        templist=rawlist[i].split(",")
        if templist[0]==";O2" and int(templist[2])>0 and int(templist[2])<100:
            templist.remove(";O2")
            data_dic[templist[0]]={'O2':int(templist[1]),'HR':int(templist[2]),'ACT':int(templist[3])/2}

    data_df=pd.DataFrame.from_dict(data_dic).T


listdatakey=data_df.index
TimeInBed = len(listdatakey)

a=[datetime.strptime(listdatakey[i],'%y-%m-%d %H:%M:%s') for i in range(len(listdatakey))]
    

SPO2_denoise=[]
SPO2_under90=[]
SPO2_origin_loc=[]


sleepandwake=[]

threshold=np.median(data_df['ACT'])+0.2*np.std(data_df['ACT'])

for i in range(TimeInBed):
    if data_df['ACT'][listdatakey[i]]>threshold:
        sleepandwake.append(1)
    else:
        sleepandwake.append(0)

plt.subplot(5,1,1)
plt.plot(listdatakey[1:500],sleepandwake[1:500])
#
sleepandwakea=getstate_filter(sleepandwake,5)
plt.subplot(5,1,2)
plt.plot(listdatakey[1:500],sleepandwakea[1:500])
#
#
#sleepandwakeb=getstate_filter(sleepandwakea,10)
#plt.subplot(5,1,3)
#plt.plot(sleepandwakeb)
#
#sleepandwakec=getstate_filter(sleepandwakeb,15)
#plt.subplot(5,1,4)
#plt.plot(sleepandwakec)
#
#sleepandwaked=getstate_filter(sleepandwakec,30)
#plt.subplot(5,1,5)
#plt.plot(sleepandwaked)


#a=[ list(x[1]) for x in itertools.groupby(sleepandwake, lambda x: x == 0) if not x[0] ]
#
#
#sleepandwakea=[]
#for j in range(len(sleepandwake)-10):
#    if sum(sleepandwake[j:j+10])>5:
#        sleepandwakea.append(1)
#    else:
#        sleepandwakea.append(0)
#
#plt.subplot(3,1,2)
#plt.plot(sleepandwakea)
#
#sleepandwakeb=[]
#
#for j in range(len(sleepandwake)-30):
#    if sum(sleepandwake[j:j+30])>15:
#        sleepandwakeb.append(1)
#    else:
#        sleepandwakeb.append(0)
#plt.subplot(3,1,3)
#plt.plot(sleepandwakeb)
#    if data_df['O2'][listdatakey[i]]==0 or data_df['O2'][listdatakey[i]]==-1 or data_df['O2'][listdatakey[i]]>100 or data_df['O2'][listdatakey[i]]<70 or data_df['ACT'][listdatakey[i]]>2:
#        TimeInBed-=1
#        continue
#    SPO2_denoise.append(data_df['O2'][listdatakey[i]])
#    SPO2_origin_loc.append(i)
#    if data_df['O2'][listdatakey[i]]<90:
#        SPO2_under90.append(data_df['O2'][listdatakey[i]])
        
        
    

#diffSPO2=np.diff(np.array(SPO2_denoise))#ISPO2 in Charlie thesis
#NPSPO2=[]
#RealIdx=[]
#
#
#for i in range(len(diffSPO2)):
#    if diffSPO2[i]!=0:
#        NPSPO2.append(SPO2_denoise[i+1])
#        RealIdx.append(i+1)
#        
#NPNPSPO2=np.diff(np.array(NPSPO2))
#IndMin=[]
#IndMax=[]
#
##SPO2_mark_location = np.full([1,TimeInBed],np.nan).T.tolist()
#
#SPO2_mark_location =[np.nan] * TimeInBed
##for i in range(len(NPNPSPO2)-1):
##    if NPNPSPO2[i+1]*NPNPSPO2[i]>0:
##        IndMin.append(i+1)   #trough 
##    else:
##        IndMax.append(i+1)   #peak
#
#for i in range(len(NPNPSPO2)-1):
#    if np.sign(NPNPSPO2[i+1]) - np.sign(NPNPSPO2[i])>0:
#        IndMin.append(i+1)   #trough 
#    elif np.sign(NPNPSPO2[i+1]) - np.sign(NPNPSPO2[i])<0:
#        IndMax.append(i+1)   #peak
#        
#peak_values=[]
#peak_values_idx=[]
#trough_values=[]
#trough_values_idx=[]
#
#for i in range(len(IndMax)):
#    peak_values.append(NPSPO2[IndMax[i]])
#    peak_values_idx.append(RealIdx[IndMax[i]])
#    SPO2_mark_location[RealIdx[IndMax[i]]] = 'peak,' +str(SPO2_origin_loc[RealIdx[IndMax[i]]]) + ',' + str(NPSPO2[IndMax[i]])
#    
#for i in range(len(IndMin)):
#    trough_values.append(NPSPO2[IndMin[i]])
#    trough_values_idx.append(RealIdx[IndMin[i]])
#    SPO2_mark_location[RealIdx[IndMin[i]]] = 'trough,' + str(SPO2_origin_loc[RealIdx[IndMin[i]]]) + ',' + str(NPSPO2[IndMin[i]])
#    
#peak_count=len(peak_values)
#trough_count=len(trough_values)
#count_diff=abs(peak_count-trough_count)
#
#SPO2_mark_location = [x for x in SPO2_mark_location if str(x) != 'nan']
#
#if NPNPSPO2[0]>0:
#    if count_diff ==1:
#        peak_values.pop()
#        peak_values_idx.pop()
#        SPO2_mark_location.pop();
#else:
#    if count_diff == 1:
#        trough_values.pop(0)
#        trough_values_idx.pop(0)
#        SPO2_mark_location.pop(0)
#    else:
#        peak_values.pop()
#        peak_values_idx.pop()
#        trough_values.pop(0)
#        trough_values_idx.pop(0)
#        SPO2_mark_location.pop();
#        SPO2_mark_location.pop(0);
#        
#amp=[]
#duration=[]
#O2_delta=[]
#ODI=[]
#AHI=[]
#O2_delta_4=[]
#
#for i in range(len(peak_values)):
#    if abs(peak_values_idx[i]-trough_values_idx[i]) <=Duration_Time:
#        amp.append(peak_values[i]-trough_values[i])
#        if peak_values[i]-trough_values[i]>=3:
#            O2_delta.append(peak_values[i]-trough_values[i])
#        if peak_values[i]-trough_values[i]>=4:
#            O2_delta_4.append(peak_values[i]-trough_values[i])
#            
#            
##    // json
##    var SPO2_event = {};
##    var SPO2_event_count = 0;
##    for (var i = 0; i < SPO2_mark_location.length; i += 2) {
##        if (Math.abs(peak_values_index[i/2] - trough_values_index[i/2]) <= DurationTime) {
##            if (Number(SPO2_mark_location[i].split(',')[2]) - Number(SPO2_mark_location[i+1].split(',')[2]) >= Threshold) {
##                SPO2_event[String(SPO2_event_count)] = {};
##                SPO2_event[String(SPO2_event_count)].time = data['Time'][SPO2_mark_location[i].split(',')[1]];
##                SPO2_event[String(SPO2_event_count)].duration = Math.abs(Number(SPO2_mark_location[i].split(',')[1]) - Number(SPO2_mark_location[i+1].split(',')[1]));
##                // SPO2_event[String(SPO2_event_count)].PA = [];
##                // SPO2_event[String(SPO2_event_count)].index = SPO2_mark_location[i];
##                // for (var k = 0; k < SPO2_event[String(SPO2_event_count)].duration; k++) {
##                //     SPO2_event[String(SPO2_event_count)].PA.push(data['PA'][Number(SPO2_mark_location[i].split(',')[1]) + k]);
##                // }
##                SPO2_event_count++;
##            }
##        }
##    }
#ODE = len(O2_delta);
#ODE4 = len(O2_delta_4);
#ODE_new = (ODE+ODE)/2
#
#AHI = ODE/TimeInBed*3600
#AHI_new = ODE_new/TimeInBed*3600
#
#osa_level=''
#
#if AHI_new>=30:
#    osa_level='Severe'
#elif AHI_new>=15 and AHI_new<30:
#    osa_level='Moderate'
#elif AHI_new>=5 and AHI_new<=15:
#    osa_level='Mild'
#elif AHI_new<5:
#    osa_level='Normal'
#    
#Total_Record_time=round(TimeInBed/3600,2)
#Record_start=listdatakey[0]
#Record_end=listdatakey[-1]
#baseline=get_mode(SPO2_denoise)
#meanSPO2=round(np.mean(SPO2_denoise),2)
#LowestSPO2=min(SPO2_denoise)
#ratio_under90=round(len(SPO2_under90)/len(SPO2_denoise)*100,2)
#
