#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 20 11:27:54 2019

@author: hao
"""
#%%

import pandas as pd
import os
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
import numpy as np
import scipy.stats as sci
import seaborn as sns
import fnmatch
font = FontProperties(fname=r"/Users/hao/Desktop/fonts/STHeiti Medium.ttc", size=14)
from Sleep_Algorithm import Sleep_Algorithm as SA

#%%
path='/Users/hao/Desktop/python/act/processeddata2output/'
lista = os.listdir(path)
sleep_parameter = {}
SL_list = []
WASO_list = []
SE_list = []
SL_pre_list = []
WASO_pre_list = []
SE_pre_list = []
for i in range(len(lista)):
    if('.xls' in lista[i]):
        xls = pd.ExcelFile(path+'/'+lista[i])
        sheet = xls.parse('data')
        sheet = sheet.dropna(axis=0, how='any')
#        score = sheet['score'].tolist()
        score= list(map(int,sheet['score']))
        act = sheet['ACT'].tolist()
        post = SA.posture(sheet['spin'])
        lie = SA.lie_time(post)
        final = SA.final_stand(post)
        sleep = SA.sleep_time(lie,score)
        wake = SA.wake_time(sleep,score)
        stand = SA.stand_time(wake,post)
        SL = sleep - lie
        WASO = wake - sleep
        SE = SA.sleep_efficiency(lie,final,score)
        pre = SA.predict_sleep2(act,lie,final)
        sleep_pre = SA.sleep_time(lie,pre)
        wake_pre = SA.wake_time(sleep,pre)
        stand_pre = SA.stand_time(wake_pre,post)
        SL_pre = sleep_pre - lie
        WASO_pre = wake_pre - sleep_pre
        SE_pre = SA.sleep_efficiency(lie,final,pre)
        
        SL_list.append(SL)
        WASO_list.append(WASO)
        SE_list.append(SE)
        SL_pre_list.append(SL_pre)
        WASO_pre_list.append(WASO_pre)
        SE_pre_list.append(SE_pre)
#        sleep_parameter[lista[i].split('.')[0]]={
#                'SL':SL,'WASO':WASO,'SE':SE,
#                'SL_pre':SL_pre,'WASO_pre':WASO_pre,'SE_pre':SE_pre}
#%%
r_SL, p_SL = sci.pearsonr(SL_list,SL_pre_list)
r_WASO, p_WASO = sci.pearsonr(WASO_list,WASO_pre_list)
r_SE, p_SE= sci.pearsonr(SE_list,SE_pre_list)