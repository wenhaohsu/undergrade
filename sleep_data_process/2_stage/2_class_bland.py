#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 25 22:48:43 2020

@author: hao
"""

import pandas as pd
import os
import matplotlib.pyplot as plt
import numpy as np
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()
#import itertools
#from sklearn.metrics import roc_curve,roc_auc_score,confusion_matrix,accuracy_score,cohen_kappa_score
#%%

def sleep_wake_act2(posture,activity):
    state=[]
    lie_act=[]       
    conscious=[]
    for i in range(len(posture)):
        if posture[i]==5:
            state.append(2)
        else:
            state.append(1)
            lie_act.append(activity[i])
    threshold=np.median(lie_act)+0.2*np.std(lie_act)
    for i in range(len(activity)):
        if activity[i]>= threshold:
            conscious.append(1)
        else:
            conscious.append(0)
    return conscious

def sleep_wake_score(score):
    conscious=[]
    for i in range(len(score)):
        if score[i] == 5:
            conscious.append(1)
        else:
            conscious.append(0)
    return conscious

def state(post):
    get_state=[]
    for i in range(len(post)):
        if post[i] == 5:
            get_state.append(2)
        else:
            get_state.append(1)
    return get_state

def lie_time(post):
    get_lie = 0
    count_lie = 0
    for i in range(1,len(post)):
         if count_lie == 30:                #如果五分鐘處於同狀態
             break
         if post[i] == 1 & post[i-1] == 1:  #躺下的時間需經過一個單位才算
             get_lie = i
             count_lie += 1
         elif post[i] == 2 & post[i-1] == 2:#如果起身，躺下時間重算
             count_lie = 0
    return get_lie

def final_stand(post):
    final_stand = 0
    final_count_stand = 0
    for i in range(len(post)-1,0,-1):
        if final_count_stand == 18:        #如果兩分鐘處於同狀態
            break
        if post[i] == 1 & post[i-1] == 1:  #躺下的時間需經過一個單位才算
            final_stand = i
            final_count_stand += 1
        elif post[i] == 2 & post[i-1] == 2:#如果起身，躺下時間重算
            final_stand = 0
    return final_stand

def sleep_time(get_lie,score):
    get_sleep = 0
    count_sleep = 0
    for i in range(get_lie,len(score)):
        if count_sleep == 18:                #如果兩分鐘處於同狀態
            break
        if score[i] == 0 & score[i-1] == 0:  #睡著的時間需經過一個單位才算
            get_sleep = i
            count_sleep += 1
        elif score[i] == 1 & score[i-1] == 1:#如果醒來，睡著時間要重算
            count_sleep = 0        
    return  get_sleep

def final_wake_time(final_stand,score):
    get_final_wake = 0
    count_wake = 0
    for i in range(final_stand-1,0,-1):
        if count_wake == 6:                 #如果兩分鐘處於同狀態
            break
        if score[i] == 0 & score[i-1] == 0:  #睡著的時間需經過一個單位才算
            get_final_wake = i
            count_wake += 1
        elif score[i] == 1 & score[i-1] == 1:#如果醒來，睡著時間要重算
            count_wake = 0
    return get_final_wake

def sleep_latency(lie_time,sleep_time):
    return (sleep_time-lie_time)*10/60

def Wake_after_sleep_onset(sleep_time,wake_time,score):
    wake_sec = 0
    for i in range(sleep_time,wake_time):
        if score[i] == 1 & score[i-1] == 1:  #躺下的時間需經過一個單位才算
            wake_sec += 1
    return wake_sec*10/60

def sleep_efficiency(get_lie,final_stand,score):
    sleep_sec = 0
    for i in range(get_lie,final_stand):
        if score[i] == 0 & score[i-1] == 0:  #躺下的時間需經過一個單位才算
            sleep_sec += 1
    efficiency = sleep_sec/(final_stand-get_lie)*100
    return efficiency
    
#def getstate_filter(state,window_size):#window_size決定你的過濾窗格大小，使用奇數
#    window=[]
#    state_len=window_size+1
#    window_epoch=window_size//2
#    for i in range(len(state)):
#        if i < window_size or i > len(state)-state_len:
#            window.append(1)
#        else:
#            state_sum=sum(state[i-window_epoch:i+window_epoch]) 
#            if state_sum>=window_epoch:
#                window.append(1)
#            else:
#                window.append(0)
#    return window 

#def plot_hypogram(time,score,post,xticks=True):
#    lie_down=lie_time(state(post))
#    stand_up=final_stand(state(post))
#    sleep=sleep_time(lie_down,score)
#    wake_up=final_wake_time(stand_up,score)
#    plt.plot(time,score)
#    plt.plot(time[lie_down:stand_up],score[lie_down:stand_up])
#    plt.plot(time[sleep:wake_up],score[sleep:wake_up])
#    plt.xlim(time[0],time[-1])
#    plt.tick_params(axis='y',which='both',bottom=False,top=False,length = 0)
#    plt.yticks([0,1],["Sleep","Wake"],fontname="Arial",fontsize=14)
#    if  xticks:
#        plt.xticks(fontname="Arial",fontsize=16)
#    else:
#        plt.xticks([])
        
#def multi_filter(post,act):
#    layer1=3
#    window=2
#    layer2=layer1+window  
#    layer3=layer2+window
#    layer4=layer3+window
#    layer5=layer4+window
#    unfilter=sleep_wake_act2(post,act)
#    first_layer=getstate_filter(unfilter,layer1)
#    second_layer=getstate_filter(first_layer,layer2)
#    third_layer=getstate_filter(second_layer,layer3)
#    fourth_layer=getstate_filter(third_layer,layer4)
#    fifth_layer=getstate_filter(fourth_layer,layer5)
#    return unfilter,first_layer,second_layer,third_layer,fourth_layer,fifth_layer

def bland_altman_plot(data1,data2,fontname='Arial',xlabel=False,*args, **kwargs):
    data1=np.asarray(data1)
    data2=np.asarray(data2)
    mean =np.mean([data1,data2],axis=0)
    diff =data1 - data2                   # Difference between data1 and data2
    md   =np.mean(diff)                   # Mean of the difference
    sd   =np.std(diff,axis=0)            # Standard deviation of the difference
    y_ci_5=md - 1.96*sd
    y_ci_95=md + 1.96*sd
    plt.scatter(mean,diff,*args,**kwargs)
    plt.axhline(md,    color='gray',linestyle='--')
    plt.axhline(y_ci_5,color='gray',linestyle='--')
    plt.axhline(y_ci_95,color='gray',linestyle='--')
    plt.xticks([round(min(mean)),round((min(mean)+max(mean))/2),round(max(mean))],fontname='Arial',fontsize=16)
    plt.yticks([round(y_ci_5),round(md),round(y_ci_95)],fontname='Arial',fontsize=16)
    if xlabel:
        plt.xlabel('Average of TD1 scored and proposed method',fontname='Arial',fontsize=18)

#%%
#path='/Users/hao/Desktop/python/sleep_data_process/2_stage/health_pre'
path2='/Users/hao/Desktop/python/sleep_data_process/2_stage/ann_output'
lista = os.listdir(path)
listb = os.listdir(path2)
Score_list=[]
Score_len=[]
#act_list=[]
#act_len=[]
Time_list=[]
Post_list=[]
Post_len=[]
lie_list=[]
stand_list=[]
#multi_layer_list=[]
lr_list=[]
svm_list=[]
#for i in range(len(lista)):
#    if('.xls' in lista[i]):
#        sheet=pd.read_excel(path+'/'+lista[i],sheet_name='whole data')
#        sheet=sheet.dropna(axis=0, how='any')
#        Score=list(map(int,sheet['Score']))
#        lie_down=lie_time(state(sheet['post']))
#        stand_up=final_stand(state(sheet['post']))
#        act=sheet['act'].tolist()
#        Time=sheet['Time'].tolist()
#        Pre_post=sheet['post'].tolist()
#        Pre_lr=sheet['pre_lr'].tolist()
#        Pre_svm=sheet['pre_svm'].tolist()
#        Post=state(Pre_post)
#        TD1=sleep_wake_score(Score)
#        multi_layer=multi_filter(sheet['post'],sheet['act'])
#        Score_list.append(TD1)
#        Score_len+=TD1
#        Post_len+=Post
#        Post_list.append(Post)
#        act_len+=act
#        act_list.append(act)
#        Time_list.append(Time)
#        lie_list.append(lie_down)
#        stand_list.append(stand_up)
#        multi_layer_list.append(multi_layer)
#        lr_list.append(Pre_lr)
#        svm_list.append(Pre_svm)
        
predict_list=[]
for i in range(len(listb)):
    if('.xls' in listb[i]):
        sheet=pd.read_excel(path2+'/'+listb[i],sheet_name='predict_output')
        sheet=sheet.dropna(axis=0, how='any')
        Score=list(map(int,sheet['score']))
        predict=sheet['predict'].tolist()
        lie_down=lie_time(state(sheet['post']))
        stand_up=final_stand(state(sheet['post']))
        Time=sheet['Time'].tolist()
        Pre_post=sheet['post'].tolist()
        Post=state(Pre_post)
        Post=state(Pre_post)
        Time_list.append(Time)
        lie_list.append(lie_down)
        stand_list.append(stand_up)
        predict_list.append(predict)
        Score_list.append(Score)
        
#multi_layer_len=multi_filter(Post_len,act_len)
sleep_TD1_list=[sleep_time(lie_list[i],Score_list[i]) for i in range(len(Score_list))]
wake_TD1_list=[final_wake_time(stand_list[i],Score_list[i]) for i in range(len(Score_list))]
#sleep_unfilter_list=[sleep_time(lie_list[i],multi_layer_list[i][0]) for i in range(len(multi_layer_list))]
#wake_unfilter_list=[final_wake_time(stand_list[i],multi_layer_list[i][0]) for i in range(len(multi_layer_list))]
#sleep_filter_list=[sleep_time(lie_list[i],multi_layer_list[i][5]) for i in range(len(multi_layer_list))]
#wake_filter_list=[final_wake_time(stand_list[i],multi_layer_list[i][5]) for i in range(len(multi_layer_list))]
sleep_filter_list=[sleep_time(lie_list[i],predict_list[i]) for i in range(len(predict_list))]
wake_filter_list=[final_wake_time(stand_list[i],predict_list[i]) for i in range(len(predict_list))]

''''''
n=7
#fig0n=2
#yy=[0,1]
#yy2=[0,20]
#my_yticks = ["Sleep","Wake"]
#fig0=plt.figure(figsize=(15,10))
#fig0.add_subplot(fig0n,1,2)
#plt.plot(Time_list[n],Score_list[n])
#plt.yticks(yy,my_yticks,fontname="Arial",fontsize=14)
#plt.xlim(Time_list[n][0],Time_list[n][-1])
#
#plt.xticks(fontname="Arial",fontsize=14)
#plt.ylabel('Scored by technician',fontname="Arial",fontsize=20)
#plt.tick_params(axis='y',which='both',bottom=False, top=False,length = 0)
#fig0.add_subplot(fig0n,1,1)
#plt.plot(Time_list[n],act_list[n])
#plt.yticks(fontname="Arial",fontsize=14)
#plt.xlim(Time_list[n][0],Time_list[n][-1])
#plt.ylim(0,max(act_list[n]))
#plt.ylabel('Activity',fontname="Arial",fontsize=20)
#plt.xticks([])
#plt.yticks([0,max(act_list[n])/4,max(act_list[n])/2,max(act_list[n])*3/4,max(act_list[n])]
#            ,fontname="Arial",fontsize=14)
##plt.title('Compare activity with TD1 score',fontname="Arial",fontsize=24)
#plt.tight_layout()

''''''

#fig1=plt.figure(figsize=(20,20))
#fig1n=7
#fig1.add_subplot(fig1n,1,fig1n)
#plot_hypogram(Time_list[n],Score_list[n],Post_list[n],xticks=True)
#plt.ylabel("Scored by\ntechnician",fontname="Arial",fontsize=16)
##plt.title('Multilayer filter algorithm',fontname="Arial",fontsize=24)
#fig1.add_subplot(fig1n,1,1)
#plot_hypogram(Time_list[n],multi_layer_list[n][0],Post_list[n],xticks=False)
#plt.ylabel("Scored by\nalgorithm",fontname="Arial",fontsize=16)
#fig1.add_subplot(fig1n,1,2)
#plot_hypogram(Time_list[n],multi_layer_list[n][1],Post_list[n],xticks=False)
#plt.ylabel("The 1st\nlayer",fontname="Arial",fontsize=16)
#fig1.add_subplot(fig1n,1,3)
#plot_hypogram(Time_list[n],multi_layer_list[n][2],Post_list[n],xticks=False)
#plt.ylabel("The 2nd\nlayer",fontname="Arial",fontsize=16)
#fig1.add_subplot(fig1n,1,4)
#plot_hypogram(Time_list[n],multi_layer_list[n][3],Post_list[n],xticks=False)
#plt.ylabel("The 3rd\nlayer",fontname="Arial",fontsize=16)
#fig1.add_subplot(fig1n,1,5)
#plot_hypogram(Time_list[n],multi_layer_list[n][4],Post_list[n],xticks=False)
#plt.ylabel("The 4th\nlayer",fontname="Arial",fontsize=16)
#fig1.add_subplot(fig1n,1,6)
#plot_hypogram(Time_list[n],multi_layer_list[n][5],Post_list[n],xticks=False)
#plt.ylabel("The 5th\nlayer",fontname="Arial",fontsize=16)
#plt.tight_layout()
''''''

TIB_TD1=[[sleep_latency(lie_list[i],stand_list[i]) for i in range(len(Time_list))]]
TST_TD1=[[sleep_latency(sleep_TD1_list[i],wake_TD1_list[i]) for i in range(len(Time_list))]]
SL_TD1=[sleep_latency(lie_list[i],sleep_TD1_list[i]) for i in range(len(Time_list))]
WASO_TD1=[Wake_after_sleep_onset(sleep_TD1_list[i],wake_TD1_list[i],Score_list[i]) for i in range(len(Time_list))]
SE_TD1=[sleep_efficiency(lie_list[i],stand_list[i],Score_list[i]) for i in range(len(Time_list))]
SL_act2=[sleep_latency(lie_list[i],sleep_filter_list[i]) for i in range(len(Time_list))]
#WASO_act2=[Wake_after_sleep_onset(sleep_filter_list[i],wake_filter_list[i],multi_layer_list[i][5]) for i in range(len(Time_list))]
#SE_act2=[sleep_efficiency(lie_list[i],stand_list[i],multi_layer_list[i][5]) for i in range(len(Time_list))]
WASO_act2=[Wake_after_sleep_onset(sleep_filter_list[i],wake_filter_list[i],predict_list[i]) for i in range(len(Time_list))]
SE_act2=[sleep_efficiency(lie_list[i],stand_list[i],predict_list[i]) for i in range(len(Time_list))]


''''''
fig3=plt.figure(figsize=(20,10))

fig3.add_subplot(3,1,1)
#fig3.add_subplot(2,3,4)
bland_altman_plot(SL_act2,SL_TD1)
plt.title('Sleep latency (min)',fontname='Arial',fontsize=24)
#plt.ylabel('Difference between TD1\nand after 4th layer',fontname='Arial',fontsize=18)  
fig3.add_subplot(3,1,2)
#fig3.add_subplot(2,3,5)
bland_altman_plot(WASO_act2,WASO_TD1)
plt.title('Wake after sleep onset (min)',fontname='Arial',fontsize=24)
plt.ylabel('Difference between scored and proposed method',fontname='Arial',fontsize=18)  
fig3.add_subplot(3,1,3)
#fig3.add_subplot(2,3,6)
bland_altman_plot(SE_act2,SE_TD1,xlabel=True)
plt.title('Sleep efficency (%)',fontname='Arial',fontsize=24)
#plt.ylabel('Difference between TD1\nand after 4th layer',fontname='Arial',fontsize=18)  
#plt.tight_layout()
#%%
#fig4=plt.figure(figsize=(20,20))
#fig4n=2
#fig4.add_subplot(fig4n,1,fig4n)
#plot_hypogram(Time_list[n],Score_list[n],Post_list[n],xticks=True)
#plt.ylabel("Scored\nby technician",fontname="Arial",fontsize=16)
##plt.title('Multilayer filter algorithm',fontname="Arial",fontsize=24)
#fig4.add_subplot(fig4n,1,1)
#plot_hypogram(Time_list[n],multi_layer_list[n][1],Post_list[n],xticks=False)
#plt.ylabel("After 1th layer",fontname="Arial",fontsize=16)
#plt.tight_layout()