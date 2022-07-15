#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov  6 11:07:02 2019

@author: hao
"""

import pandas as pd
import matplotlib.pyplot as plt
#from matplotlib.font_manager import FontProperties
import scipy.stats as sci
import numpy as np
#import seaborn as sns
import os
from Sleep_Algorithm import Sleep_Algorithm as SA
from sklearn import metrics
path='/Users/hao/Desktop/python/act/processeddata2output/'

#%%
    
lista=os.listdir(path)
sleep_parameter={}
#sleep_list = []
#sleep2_list = []
#wake_list = []
#wake2_list = []
for i in range(len(lista)):
    if('.xls' in lista[i]):
        xls = pd.ExcelFile(path + '/' + lista[i])
        sheetX = xls.parse('data')
        sheetX = sheetX.dropna(axis=0,how='any')
        predict = SA.predict_sleep(sheetX['ACT'],73)
        predict2 = SA.predict_sleep2(sheetX['ACT'])#,threshold)
        score = sheetX['score']
        score = list(map(int,score))
        post = SA.posture(sheetX['spin'])
        lie = SA.lie_time(post)
        sleep = SA.sleep_time(lie,predict)
        sleep2 = SA.sleep_time(lie,predict2)
        sleep_score = SA.sleep_time(lie,score)
        wake = SA.wake_time(sleep,predict)
        wake2 = wake_time(sleep2,predict2)
        wake_score = wake_time(sleep_score,score)
#        sleep_list.append(sleep)
#        sleep2_list.append(sleep2)
#        wake_list.append(wake)
#        wake2_list.append(wake2)
        sleep_parameter[lista[i].split('.')[0]]={
                "sleeptime":sleep,"sleeptime2":sleep2,"sleeptime_score":sleep_score,
                "waketime":wake,"waketime2":wake2,"waketime_score":wake_score
                }
listb=os.listdir(path)
sleep_parameter = {}
corr_SL = []
corr_WASO = []
corr_SE = []
SL_list = []
WASO_list = []
SE_list = []
SL_score_list = []
WASO_score_list = []
SE_score_list = []
threshold_list = []
pvalue_SL = []
pvalue_WASO = []
pvalue_SE = []
count_threshold = 0
for i in range(act_threshold):

    if count_threshold > act_threshold:
        break
    else:
        for i in range(len(listb)):
            if('.xls' in listb[i]):
                xls = pd.ExcelFile(path + '/' + listb[i])
                sheetX = xls.parse('data')
                sheetX = sheetX.dropna(axis=0,how='any')
                TRT,TST,SL,WASO,SE = predict_sleep(sheetX['ACT'],sheetX['spin'],act_threshold-count_threshold)
                TRT_2,TST,SL_2,WASO_2,SE_2 = standard_sleep(sheetX['score'],sheetX['spin'])
                SL_list.append(SL)
                WASO_list.append(WASO)
                SE_list.append(SE)
                SL_score_list.append(SL_2)
                WASO_score_list.append(WASO_2)
                SE_score_list.append(SE_2)
                r_SL, p_SL = sci.pearsonr(SL_list,SL_score_list)
                r_WASO, p_WASO = sci.pearsonr(WASO_list,WASO_score_list)
                r_SE, p_SE= sci.pearsonr(SE_list,SE_score_list)
        corr_SL.append(r_SL)
        pvalue_SL.append(p_SL)
        corr_WASO.append(r_WASO)
        pvalue_WASO.append(p_WASO)
        corr_SE.append(r_SE)
        pvalue_SE.append(p_SE)
        threshold_list.append(act_threshold--count_threshold)
        sleep_parameter[listb[i].split('.')[0]]={
                "Threshold":threshold_list,"corr_SL":corr_SL,"p_SL":pvalue_SL,
                "Corr_WASO":corr_WASO,"p_WASO":pvalue_WASO,"Corr_SE":corr_SE,"p_SE":pvalue_SE,
                }
        count_threshold += 1
        
fig2 = plt.figure(figsize=(10,5))

x1 = threshold_list
#y1 = corr_SL
y2 = corr_WASO
#y3 = corr_SE
#plt.plot(x1,y1,label='Corr_SL')
plt.plot(x1,y2,label='Corr_WASO')
#plt.plot(x1,y3,label='Corr_SE')
plt.xlabel('Threshold')
plt.ylabel('Correlation coefficient')
plt.title("Correlation of activity threshold")
plt.legend(loc="upper right")
