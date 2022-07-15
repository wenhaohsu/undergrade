#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar 29 01:18:39 2020

@author: hao
"""

import pandas as pd
import os
import matplotlib.pyplot as plt
import numpy as np
import itertools
from sklearn.metrics import confusion_matrix
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()
#%%
def sleep_wake_act2(posture,activity):
    state=[]
    lie_act=[]       
    conscious=[]
    for i in range(len(posture)-1):
        if posture[i] == 4:
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
            conscious.append(2)
        elif score[i] == 4:
            conscious.append(1)
        else:
            conscious.append(0)
    return conscious

def plot_confusion_matrix(cm, classes,
                          normalize=True,
                          title='Confusion matrix',
                          cmap=plt.cm.Blues,
                          fontname="Arial",
                          xlabel=True,
                          ylabel=True):
    if normalize:
        cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]

    plt.imshow(cm, interpolation='nearest', cmap=cmap)
    plt.title(title,fontsize=18)
    tick_marks = np.arange(len(classes))
    plt.xticks(tick_marks, classes,fontsize=14)
    plt.yticks(tick_marks, classes,fontsize=14)

    fmt = '.2f' if normalize else 'd'
    thresh = cm.max() / 2.
    for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
        plt.text(j, i, format(cm[i, j], fmt),fontsize=14,
                 horizontalalignment="center",
                 color="white" if cm[i, j] > thresh else "black")
    plt.xlim(-0.5,len(classes)-0.5)
    plt.ylim(len(classes)-0.5,-0.5)
    if ylabel:
        plt.ylabel('Scored by TD1',fontname="Arial",fontsize=16)
    if xlabel:
        plt.xlabel('Scored by algorithm',fontname="Arial",fontsize=16)

def state(post):
    get_state=[]
    for i in range(len(post)):
        try:
            if post[i] == 5:
                get_state.append(2)
            else:
                get_state.append(1)
        except KeyError:
            pass 
    return get_state

def lie_time(post):
    get_lie = 0
    count_lie = 0
    for i in range(len(post)):
         if count_lie == 18:                #如果兩分鐘處於同狀態
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
        if count_sleep == 6:                #如果兩分鐘處於同狀態
            break
        if score[i] == 0 & score[i-1] == 1:  #睡著的時間需經過一個單位才算
            get_sleep = i
            count_sleep += 1
        elif score[i] == 1 & score[i-1] == 2:#如果醒來，睡著時間要重算
            count_sleep = 0        
    return  get_sleep

def final_wake_time(final_stand,score):
    get_final_wake = 0
    count_wake = 0
    for i in range(final_stand-1,0,-1):
        if count_wake == 6:                 #如果兩分鐘處於同狀態
            break
        if score[i] == 0 & score[i-1] == 1:  #醒來的時間需經過一個單位才算
            get_final_wake = i
            count_wake += 1
        elif score[i] == 1 & score[i-1] == 2:#如果睡著，清醒時間要重算
            count_wake = 0
    return get_final_wake

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

def multi_filter(post,act):
    layer1=3
    layer2=5  
    layer3=7
    layer4=9
    layer5=11
    unfilter=sleep_wake_act2(post,act)
    first_layer=getstate_filter(unfilter,layer1)
    second_layer=getstate_filter(first_layer,layer2)
    third_layer=getstate_filter(second_layer,layer3)
    fourth_layer=getstate_filter(third_layer,layer4)
    fifth_layer=getstate_filter(fourth_layer,layer5)
    return unfilter,first_layer,second_layer,third_layer,fourth_layer,fifth_layer

def plot_hypogram(time,score,post,xticks=True):
    lie_down=lie_time(state(post))
    stand_up=final_stand(state(post))
    sleep=sleep_time(lie_down,score)
    wake_up=final_wake_time(stand_up,score)
    plt.plot(time,score)
    plt.plot(time[lie_down:stand_up],score[lie_down:stand_up])
    plt.plot(time[sleep:wake_up],score[sleep:wake_up])
    plt.xlim(time[0],time[-1])
    plt.tick_params(axis='y',which='both',bottom=False, top=False,length = 0)
    if  xticks:
        plt.xticks(fontname="Arial",fontsize=12)
    else:
        plt.xticks([])
        
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
        plt.xlabel('Average of\nTD1 scored and algorithm',fontname='Arial',fontsize=18)  
#%%
path='/Users/hao/Desktop/python/sleep_data_process/3_stage/health'
lista = os.listdir(path)
Score_list=[]
Score_len=[]
act_list=[]
act_len=[]
Time_list=[]
Post_list=[]
Post_len=[]
lie_list=[]
stand_list=[]
multi_layer_list=[]
CACT_list = []
O2_list=[]
O2_len=[]
HR_list=[]
HR_len=[]
CACT_len=[]

for i in range(len(lista)):
    if('.xls' in lista[i]):
#        xls=pd.ExcelFile(path+'/'+lista[i])
#        sheet=xls.parse('whole data')
        sheet=pd.read_excel(path+'/'+lista[i],sheet_name='whole data')
        sheet=sheet.dropna(axis=0, how='any')
        Score=list(map(int,sheet['Score']))
        
#        CACT2=sheet['act']
        Time=[sheet['Time']]
        HR=[sheet['ill']]
#        Var=sheet['var'].tolist()
        Pre_post=sheet['post'].tolist()
        CACT=sleep_wake_act2(Pre_post,sheet['act'])
#        HR=sheet['SD_HR']
#        O2=sheet['SD_O2']
        Post=state(Pre_post)
        TD1=sleep_wake_score(Score)
        Score_list.append(TD1)
        Score_len+=TD1
        CACT_list.append(CACT)
        CACT_len+=CACT
        Post_len+=Post
#        O2_list.append(O2)
#        O2_len+=O2
#        HR_list.append(HR)
#        HR_len+=HR
#        VAR_len+=Var
        Time_list.append(Time)
#        Post_list.append(Post)
 
multi_layer_len=multi_filter(Post_len,act_len)
sleep_TD1_list=[sleep_time(lie_list[i],Score_list[i]) for i in range(len(Score_list))]
wake_TD1_list=[final_wake_time(stand_list[i],Score_list[i]) for i in range(len(Score_list))]
sleep_unfilter_list=[sleep_time(lie_list[i],multi_layer_list[i][0]) for i in range(len(multi_layer_list))]
wake_unfilter_list=[final_wake_time(stand_list[i],multi_layer_list[i][0]) for i in range(len(multi_layer_list))]
sleep_filter_list=[sleep_time(lie_list[i],multi_layer_list[i][5]) for i in range(len(multi_layer_list))]
wake_filter_list=[final_wake_time(stand_list[i],multi_layer_list[i][5]) for i in range(len(multi_layer_list))]       
#%%
n=0
yy1=[0,1,2]
my_yticks1 = ["NREM","REM","Wake"]
fig3n=5
fig3=plt.figure(figsize=(15,10))
fig3.add_subplot(fig3n,1,1)
plt.plot(CACT_list[n])
plt.yticks(fontname="Arial",fontsize=12)
plt.xlim(Time_list[n][0],Time_list[n][-1])
plt.ylim(0,20)
plt.ylabel('Activity',fontname="Arial",fontsize=16)
plt.xticks([])
plt.title('Compare activity with TD1 score',fontname="Arial",fontsize=18)
fig3.add_subplot(fig3n,1,2)
plt.plot(Post_list[n])
plt.yticks(fontname="Arial",fontsize=12)
plt.xlim(Time_list[n][0],Time_list[n][-1])
plt.ylim(0,5)
plt.ylabel('Heart rate',fontname="Arial",fontsize=16)
plt.xticks([])
fig3.add_subplot(fig3n,1,3)
plt.plot(HR_list[n])
plt.yticks(fontname="Arial",fontsize=12)
plt.xlim(Time_list[n][0],Time_list[n][-1])
plt.ylim(0,5)
plt.ylabel('Heart rate',fontname="Arial",fontsize=16)
plt.xticks([])
fig3.add_subplot(fig3n,1,4)
plt.plot(O2_list[n])
plt.yticks(fontname="Arial",fontsize=12)
plt.xlim(Time_list[n][0],Time_list[n][-1])
plt.ylim(0,2)
plt.ylabel('Oxigen',fontname="Arial",fontsize=16)
plt.xticks([])
fig3.add_subplot(fig3n,1,fig3n)
plt.plot(Time_list[n],Score_list[n])
plt.yticks(yy1,my_yticks1,fontname="Arial",fontsize=12)
plt.xlim(Time_list[n][0],Time_list[n][-1])
plt.xticks(fontname="Arial",fontsize=12)
plt.ylabel('Scored by TD1',fontname="Arial",fontsize=16)
plt.tick_params(axis='y',which='both',bottom=False, top=False,length = 0)
plt.tight_layout()
#%%
lie_down=lie_time(state(Post_list[n]))
stand_up=final_stand(state(Post_list[n]))
multi_layer_len=multi_filter(Post_len,act_len)
my_yticks1 = ["Sleep","Wake"]
fig1=plt.figure(figsize=(20,20))
fig1n=7
fig1=plt.figure(figsize=(20,20))
fig1.add_subplot(fig1n,1,1)
plot_hypogram(Time_list[n],Score_list[n],Post_list[n],xticks=False)
plt.yticks(yy1,my_yticks1,fontname="Arial",fontsize=14)
plt.ylabel("Scored\nby TD1",fontname="Arial",fontsize=16)
plt.title('Multilayer filter algorithm',fontname="Arial",fontsize=24)
fig1.add_subplot(fig1n,1,2)
plot_hypogram(Time_list[n],multi_layer_list[n][0],Post_list[n],xticks=False)
plt.yticks(yy1,my_yticks1,fontname="Arial",fontsize=14)
plt.ylabel("Scored by\nalgorithm",fontname="Arial",fontsize=16)
fig1.add_subplot(fig1n,1,3)
plot_hypogram(Time_list[n],multi_layer_list[n][1],Post_list[n],xticks=False)
plt.yticks(yy1,my_yticks1,fontname="Arial",fontsize=14)
plt.ylabel("The 1st\nlayer",fontname="Arial",fontsize=16)
fig1.add_subplot(fig1n,1,4)
plot_hypogram(Time_list[n],multi_layer_list[n][2],Post_list[n],xticks=False)
plt.yticks(yy1,my_yticks1,fontname="Arial",fontsize=14)
plt.ylabel("The 2nd\nlayer",fontname="Arial",fontsize=16)
fig1.add_subplot(fig1n,1,5)
plot_hypogram(Time_list[n],multi_layer_list[n][3],Post_list[n],xticks=False)
plt.yticks(yy1,my_yticks1,fontname="Arial",fontsize=14)
plt.ylabel("The 3rd\nlayer",fontname="Arial",fontsize=16)
fig1.add_subplot(fig1n,1,6)
plot_hypogram(Time_list[n],multi_layer_list[n][4],Post_list[n],xticks=False)
plt.yticks(yy1,my_yticks1,fontname="Arial",fontsize=14)
plt.ylabel("The 4th\nlayer",fontname="Arial",fontsize=16)
fig1.add_subplot(fig1n,1,7)
plot_hypogram(Time_list[n],multi_layer_list[n][5],Post_list[n],xticks=True)
plt.yticks(yy1,my_yticks1,fontname="Arial",fontsize=14)
plt.ylabel("The 5th\nlayer",fontname="Arial",fontsize=16)
plt.tight_layout()
#%%
TIB_TD1=[[sleep_latency(lie_list[i],stand_list[i]) for i in range(len(Time_list))]]
TST_TD1=[[sleep_latency(sleep_TD1_list[i],wake_TD1_list[i]) for i in range(len(Time_list))]]
SL_TD1=[sleep_latency(lie_list[i],sleep_TD1_list[i]) for i in range(len(Time_list))]
WASO_TD1=[Wake_after_sleep_onset(sleep_TD1_list[i],wake_TD1_list[i],Score_list[i]) for i in range(len(Time_list))]
SE_TD1=[sleep_efficiency(lie_list[i],stand_list[i],Score_list[i]) for i in range(len(Time_list))]
SL_act1=[sleep_latency(lie_list[i],sleep_unfilter_list[i]) for i in range(len(Time_list))]
WASO_act1=[Wake_after_sleep_onset(sleep_unfilter_list[i],wake_unfilter_list[i],multi_layer_list[i][0]) for i in range(len(Time_list))]
SE_act1=[sleep_efficiency(lie_list[i],stand_list[i],multi_layer_list[i][0]) for i in range(len(Time_list))]
SL_act2=[sleep_latency(lie_list[i],sleep_filter_list[i]) for i in range(len(Time_list))]
WASO_act2=[Wake_after_sleep_onset(sleep_filter_list[i],wake_filter_list[i],multi_layer_list[i][5]) for i in range(len(Time_list))]
SE_act2=[sleep_efficiency(lie_list[i],stand_list[i],multi_layer_list[i][5]) for i in range(len(Time_list))]

fig3=plt.figure(figsize=(20,20))
fig3.add_subplot(2,3,1)
bland_altman_plot(SL_act1,SL_TD1)#,ylabel=True)
plt.title('Sleep latency',fontname='Arial',fontsize=24)
plt.ylabel('Difference between\nTD1 and Unfilter activity',fontname='Arial',fontsize=18)  
fig3.add_subplot(2,3,2)
bland_altman_plot(WASO_act1,WASO_TD1)
plt.title('Wake after sleep onset',fontname='Arial',fontsize=24)
fig3.add_subplot(2,3,3)
bland_altman_plot(SE_act1,SE_TD1)
plt.title('Sleep efficency',fontname='Arial',fontsize=24)
fig3.add_subplot(2,3,4)
bland_altman_plot(SL_act2,SL_TD1,xlabel=True)#,ylabel=True)
plt.ylabel('Difference between TD1\nand after 4th layer',fontname='Arial',fontsize=18)  
fig3.add_subplot(2,3,5)
bland_altman_plot(WASO_act2,WASO_TD1,xlabel=True)
fig3.add_subplot(2,3,6)
bland_altman_plot(SE_act2,SE_TD1,xlabel=True)
plt.tight_layout()