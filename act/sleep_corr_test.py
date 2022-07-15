#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 17 11:36:13 2019

@author: hao
"""
#匯入函數
import scipy
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
import scipy.stats as sci
import numpy as np
#import seaborn as sns
import os
import fnmatch
from sklearn import metrics
#%% 建立資料

file_path='/Users/hao/Desktop/python/act/processeddata2output/'
fil

#%%
def predict_sleep(act,score,spin,act_threshold):
    stand_index = 0
    count_lie = 0
    conscious=[]
    post = []
    wake_index = 0
    count_sleep = 0
    final_lie_index = 0
    final_count_stand = 0
    sleep_index = 0
    count_wake = 0
    lie_index = 0
    count_stand = 0
    sleep_sec = 0
#    SE = []
#    SL = []
#    WASO=[]
    for i in range(len(act)):
        if i>=13 and i<=len(act)-14:      #時間長度夠的情況下
            Aact=sum(act[i-13:i-2])       #往前數4個epoch(120s)的總和
            Bact=sum(act[i+2:i+13])       #往後數4個epoch(120s)的總和
            act_now=float(act[i-1])+float(act[i])+float(act[i+1])
            act_critical=Aact+Bact+act_now#當下的1個epoch(30s)
            if act_critical>act_threshold:   #如果大於設定的threshold
                if Aact<12 and Bact<12:   #當往前或往後的epoch不足4個
                    conscious.append(1)   #判睡
                else:  
                    conscious.append(2)   #判醒
            else:
                conscious.append(1)       #判睡
                
    for i in range(len(spin)):
        if spin[i] >=13 or spin[i] <= 2 :
            post.append(2)                 #stand
        else:
            post.append(1)                 #lie
    for i in range(1,len(post)):
        if count_lie == 18:                #如果兩分鐘處於同狀態
            break
        if post[i] == 1 & post[i-1] == 1:  #躺下的時間需經過一個單位才算
            stand_index = i
            count_lie += 1
        elif post[i] == 2 & post[i-1] == 2:#如果起身，躺下時間重算
            count_lie = 0
    for i in range(stand_index,len(conscious)):
        if count_sleep == 18:                #如果兩分鐘處於同狀態
            break
        if conscious[i] == 1 & conscious[i-1] == 1:  #睡著的時間需經過一個單位才算
            wake_index = i
            count_sleep += 1
        elif conscious[i] == 2 & conscious[i-1] == 2:#如果醒來，睡著時間要重算
            count_sleep = 0        
            
    for i in range(wake_index,len(conscious)):
        if count_wake == 18:                 #如果兩分鐘處於同狀態
            break
        if conscious[i] == 2 & conscious[i-1] == 2:  #醒來的時間需經過一個單位才算
            sleep_index = i
            count_wake += 1
        elif conscious[i] == 1 & conscious[i-1] == 1:#如果睡著，清醒時間要重算
            count_wake = 0
            
    for i in range(sleep_index,len(post)):
        if count_stand == 18:              #如果兩分鐘處於同狀態
            break
        if post[i] == 2 & post[i-1] == 2:  #起床的時間需經過一個單位才算
            lie_index = i
            count_stand += 1
        elif post[i] == 1 & post[i-1] == 1:#如果躺下，起床時間重算
            count_stand = 0
            
    for i in range(len(post)-1,0,-1):
        if final_count_stand == 18:        #如果兩分鐘處於同狀態
            break
        if post[i] == 1 & post[i-1] == 1:  #躺下的時間需經過一個單位才算
            final_lie_index = i
            final_count_stand += 1
        elif post[i] == 2 & post[i-1] == 2:#如果起身，躺下時間重算
            final_lie_index = 0
            
    for i in range(stand_index,final_lie_index):
        if conscious[i] == 1 & conscious[i-1] == 1:  #躺下的時間需經過一個單位才算
            sleep_sec += 1
    efficiency = (sleep_sec / (final_lie_index - stand_index)) * 100
    latency = wake_index - stand_index
    wake_after_sleep_onset = final_lie_index - wake_index
#    SE.append(efficiency)
#    SL.append(sleep_latency)
#    WASO.append(wake_after_sleep_onset)

    sleep_threshold = 40.5
    conscious_score = []
    wake_index_score = 0
    count_sleep = 0
    stand_index_score = 0
    final_lie_index_score = 0
    sleep_index_score = 0
    count_wake_score = 0
    count_sleep_score = 0
    lie_index_score = 0
    count_stand_score = 0
    sleep_sec_score = 0
    stand_index_score = 0
#    SE_score=[]
#    SL_score=[]
#    WASO_score=[]
    for i in range(len(score)):
        if i>=13 and i<=len(score)-14:      #時間長度夠的情況下
            Ascore=sum(score[i-13:i-2])       #往前數4個epoch(120s)的總和
            Bscore=sum(score[i+2:i+13])       #往後數4個epoch(120s)的總和
            score_now=float(score[i-1])+float(score[i])+float(score[i+1])
            score_critical=Ascore+Bscore+score_now#當下的1個epoch(30s)
#            scoresum.append(score_critical)   #計算act的總和
            if score_critical>sleep_threshold:   #如果大於設定的threshold
                if Ascore<12 and Bscore<12:   #當往前或往後的epoch不足4個
                    conscious_score.append(1)   #判睡
                else:  
                    conscious_score.append(2)   #判醒
            else:
                conscious_score.append(1)       #判睡
    for i in range(stand_index,len(conscious_score)):
        if count_sleep_score == 18:                #如果兩分鐘處於同狀態
            break
        if conscious_score[i] == 1 & conscious_score[i-1] == 1:  #睡著的時間需經過一個單位才算
            wake_index_score = i
            count_sleep_score += 1
        elif conscious_score[i] == 2 & conscious_score[i-1] == 2:#如果醒來，睡著時間要重算
            count_sleep_score = 0        
    for i in range(wake_index_score,len(conscious_score)):
        if count_wake_score == 18:                 #如果兩分鐘處於同狀態
            break
        if conscious_score[i] == 2 & conscious_score[i-1] == 2:  #醒來的時間需經過一個單位才算
            sleep_index_score = i
            count_wake_score += 1
        elif conscious_score[i] == 1 & conscious_score[i-1] == 1:#如果睡著，清醒時間要重算
            count_wake_score = 0
    for i in range(sleep_index_score,len(post)):
        if count_stand_score == 18:              #如果兩分鐘處於同狀態
            break
        if post[i] == 2 & post[i-1] == 2:  #起床的時間需經過一個單位才算
            lie_index_score = i
            count_stand_score += 1
        elif post[i] == 1 & post[i-1] == 1:#如果躺下，起床時間重算
            count_stand_score = 0
    for i in range(stand_index_score,final_lie_index):
        if conscious_score[i] == 1 & conscious_score[i-1] == 1:  #躺下的時間需經過一個單位才算
            sleep_sec_score += 1
    efficiency_score = (sleep_sec_score / (final_lie_index - stand_index)) * 100
    latency_score = wake_index_score - stand_index_score
    wake_after_sleep_onset_score = final_lie_index - wake_index_score
#    SE_score.append(efficiency_score)
#    WASO_score.append(wake_after_sleep_onset_score)
#    SL_score.append(latency_score)
#    r_SL, p_SL = sci.pearsonr(SL_score,SL)
#    r_WASO, p_WASO = sci.pearsonr(WASO_score,WASO)
#    r_SE,p_SE = sci.pearsonr(SE_score,SE)
    return latency, wake_after_sleep_onset, efficiency, latency_score, wake_after_sleep_onset_score, efficiency_score
#%%
#sleep_score = list(map(int,TD1_score['score']))
SL,WASO,SE,SL_score,WASO_score,SE_score = predict_sleep(TD1_score['ACT'], TD1_score['score'], TD1_score['spin'])
print(SL,WASO,SE,SL_score,WASO_score,SE_score)
#%%

#%% pearson
#def corr_sleep_stat(file):
#    spin = file['spin']
#    score = file['score']
#    act = ['ACT']
#    count_threshold=0
#    act_threshold = 139
#    corr_SL = []
#    corr_WASO = []
#    corr_SE = []
#    for i in range(act_threshold):
#        if count_threshold > act_threshold:
#            break
#        else:
#            for i in range(file):
#                predict_sleep(spin,act,score,act_threshold)
#        r_SL, p_SL = sci.pearsonr(latency,latency_score)
#        r_WASO, p_WASO = sci.pearsonr(wake_after_sleep_onset,wake_after_sleep_onset_score)
#        r_SE, p_SE= sci.pearsonr(efficiency,efficiency_score)
#        corr_SL.append(r_SL)
#        corr_WASO.append(r_WASO)
#        corr_SE.append(r_SE)
#        count_threshold += 1
#    return corr_SL,corr_WASO, corr_SE
#%%
    