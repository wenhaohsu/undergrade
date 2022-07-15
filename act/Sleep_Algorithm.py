#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov 14 17:58:40 2019

@author: hao
"""
import numpy as np

class Sleep_Algorithm():
    def posture(spin):
        post = []
        for i in range(len(spin)):
            if spin[i] >=13 or spin[i] <= 2 :
                post.append(2)                 #stand
            else:
                post.append(1)                 #lie
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
    
    def predict_sleep(act,act_threshold):
        actsum=[]
        conscious=[]
        for i in range(len(act)):
            if i>=13 and i<=len(act)-14:      #時間長度夠的情況下
                Aact=sum(act[i-13:i-2])       #往前數4個epoch(120s)的總和
                Bact=sum(act[i+2:i+13])       #往後數4個epoch(120s)的總和
                act_now=float(act[i-1])+float(act[i])+float(act[i+1])
                act_critical=Aact+Bact+act_now#當下的1個epoch(30s)
                actsum.append(act_critical)   #計算act的總和
                if act_critical>act_threshold:   #如果大於設定的threshold
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
    
    def predict_sleep2(activity,get_lie,final_stand):
        conscious = []
        actsum = []
        epoch = 4
        act_lie = activity[get_lie:final_stand]
        median_sleepact = np.median(act_lie)
        sd_sleepact = np.std(act_lie)
        sleepact_CI = median_sleepact + 1.96*sd_sleepact
        act_thre = []
        for i in range(len(act_lie)):
            act_thre.append(sleepact_CI)
        for i in range(len(activity)):
            if i>=epoch and i<=len(activity)-(epoch+1):      #時間長度夠的情況下
                Aact=sum(activity[i-epoch:i-2])       #往前數4個epoch(120s)的總和
                Bact=sum(activity[i+2:i+epoch])       #往後數4個epoch(120s)的總和
        #      print('Aact',Aact)
        #      print('Bact',Bact)
                act_now=float(activity[i])+float(activity[i-1])+float(activity[i+1])
                act_critical=Aact+Bact+act_now#當下的1個epoch(30s)
                actsum.append(act_critical)   #計算act的總和
                if act_critical>sleepact_CI:   #如果大於設定的threshold
                    if Aact<epoch and Bact<epoch:   #當往前或往後的epoch不足4個
                            conscious.append(1)   #判睡
                    else:  
                            conscious.append(2)   #判醒
                else:
                        conscious.append(1)       #判睡
            else:                             #如果window總長度不夠
                    conscious.append(1)           #判睡
                    actsum.append(0)              #活動量算0
        return conscious
    def predict_sleep3(activity,get_lie,final_stand):
        conscious = []
        actsum = []
        epoch = 4
        act_lie = activity[get_lie:final_stand]
        sleepact = np.diff(act_lie)
#        sleepact_CI = median_sleepact + 1.96*sd_sleepact
        act_thre = []
        for i in range(len(act_lie)):
            act_thre.append(sleepact_CI)
        for i in range(len(activity)):
            if i>=epoch and i<=len(activity)-(epoch+1):      #時間長度夠的情況下
                Aact=sum(activity[i-epoch:i-2])       #往前數4個epoch(120s)的總和
                Bact=sum(activity[i+2:i+epoch])       #往後數4個epoch(120s)的總和
        #      print('Aact',Aact)
        #      print('Bact',Bact)
                act_now=float(activity[i])+float(activity[i-1])+float(activity[i+1])
                act_critical=Aact+Bact+act_now#當下的1個epoch(30s)
                actsum.append(act_critical)   #計算act的總和
                if act_critical>sleepact_CI:   #如果大於設定的threshold
                    if Aact<epoch and Bact<epoch:   #當往前或往後的epoch不足4個
                            conscious.append(1)   #判睡
                    else:  
                            conscious.append(2)   #判醒
                else:
                        conscious.append(1)       #判睡
            else:                             #如果window總長度不夠
                    conscious.append(1)           #判睡
                    actsum.append(0)              #活動量算0
        return conscious    
    def sleep_time(get_lie,score):
        get_sleep = 0
        count_sleep = 0
        for i in range(get_lie,len(score)):
            if count_sleep == 3:                #如果兩分鐘處於同狀態
                break
            if score[i] == 1 & score[i-1] == 1:  #睡著的時間需經過一個單位才算
                get_sleep = i
                count_sleep += 1
            elif score[i] == 2 & score[i-1] == 2:#如果醒來，睡著時間要重算
                count_sleep = 0        
        return  get_sleep
    
    def wake_time(get_sleep,score):
        get_wake = 0
        count_wake = 0
        for i in range(get_sleep,len(score)):
            if count_wake == 3:                 #如果兩分鐘處於同狀態
                break
            if score[i] == 2 & score[i-1] == 2:  #醒來的時間需經過一個單位才算
                get_wake = i
                count_wake += 1
            elif score[i] == 1 & score[i-1] == 1:#如果睡著，清醒時間要重算
                count_wake = 0
        return get_wake
    
    def stand_time(get_wake,post):
        get_stand = 0
        count_stand = 0
        for i in range(get_wake,len(post)):
            if count_stand == 18:              #如果兩分鐘處於同狀態
                break
            if post[i] == 2 & post[i-1] == 2:  #起床的時間需經過一個單位才算
                get_stand = i
                count_stand += 1
            elif post[i] == 1 & post[i-1] == 1:#如果躺下，起床時間重算
                count_stand = 0
        return get_stand
    
    def total_sleep(get_lie,final_stand,score):
        sleep_sec = 0
        for i in range(get_lie,final_stand):
            if score[i] == 1 & score[i-1] == 1:  #躺下的時間需經過一個單位才算
                sleep_sec += 1
        return sleep_sec
    
    def sleep_efficiency(get_lie,final_stand,score):
        sleep_sec = 0
        for i in range(get_lie,final_stand):
            if score[i] == 1 & score[i-1] == 1:  #躺下的時間需經過一個單位才算
                sleep_sec += 1
        efficiency = (sleep_sec / (final_stand - get_lie)) * 100
        return efficiency