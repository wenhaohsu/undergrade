#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 12 17:20:19 2020

@author: hao
"""
import pandas as pd
def insert_data(data,end):
  ACT=[] #移除有問題資料後
  HMS=[]
  Hours=[]
  Minute=[]
  Second=[]
  for x in range(len(data)):
    Hours.append(data[x][1].split(":")[0])
    Minute.append(data[x][1].split(":")[1])
    Second.append(data[x][1].split(":")[2])
    HMS.append(data[x][1])
    ACT.append(float(data[x][2]))
  insertpointnumber=0  # 插入資料點數
  span=[]  #擴增的時間範圍
  Timeleak=[] # 缺少那些時間資料點
  insert_how_many=[] #插入多少點，存放insertpointnumber 的陣列
  time_in_s=[]  # 存放時間轉為秒數
  
  #將時間轉為秒數
  for i in range(len(HMS)):
    time_in_s.append(int(Hours[i])*60*60+int(Minute[i])*60+int(Second[i])) 
    
  temptd=time_in_s[0]
  for i in range(len(Second)):
    td=int(time_in_s[i])-temptd    
    if td>10:   # 秒數相減大於10秒
      insertpointnumber=int(td/10) #插入相減值除以10
      insert_how_many.append(insertpointnumber)   
      if i-1>=0:
        a=str(Hours[i-1])+":"+str(Minute[i-1])+":"+str(Second[i-1])+"-"+str(Hours[i])+":"+str(Minute[i])+":"+str(Second[i])
        Timeleak.append(a)
    temptd=int(time_in_s[int(i)])
  if (int(end.split(":")[0])*3600+int(end.split(":")[1])*60+int(end.split(":")[2])-time_in_s[len(time_in_s)-1])>10:
    td=int(end.split(":")[0])*3600+int(end.split(":")[1])*60+int(end.split(":")[2])-time_in_s[len(time_in_s)-1]
    if td>10:   # 秒數相減大於10秒
      insertpointnumber=int(td/10) #插入相減值除以10
      insert_how_many.append(insertpointnumber)   
    a=str(Hours[len(time_in_s)-1])+":"+str(Minute[len(time_in_s)-1])+":"+str(Second[len(time_in_s)-1])+"-"+end
    Timeleak.append(a)
  for j in range(len(Timeleak)):
    insertstarttime=Timeleak[j].split("-")[0]
  
    if HMS.index(insertstarttime)>=0:
      k_index=0  
      for n in range(1,int(insert_how_many[j])): 
          k_index=HMS.index(insertstarttime) 
          Second.insert(k_index+n,str(int(Second[k_index+n-1])+10))
          Minute.insert(k_index+n,str(int(Minute[k_index+n-1])))
          Hours.insert(k_index+n,str(int(Hours[k_index+n-1])))
          
          HMS.insert(k_index+n,Hours[k_index+n]+":"+Minute[k_index+n]+":"+Second[k_index+n])
          
          if insert_how_many[j]==1:
            actvalue=(float(ACT[k_index])+float(ACT[k_index+1]))/2    
            ACT.insert(k_index+n,float(actvalue))

          else:
            ACT.insert(k_index+n,float(1))

          if int(Second[k_index+n])>59:
            Second[k_index+n]=str(int(Second[k_index+n])-60)    
            Minute[k_index+n]=str(int(Minute[k_index+n])+1)
            HMS[k_index+n]=Hours[k_index+n]+":"+Minute[k_index+n]+":"+Second[k_index+n]
          if int(Minute[k_index+n])>59:
            Minute[k_index+n]=str(0)
            Hours[k_index+n]=str(int(Hours[k_index+n])+1)
            HMS[k_index+n]=Hours[k_index+n]+":"+Minute[k_index+n]+":"+Second[k_index+n]
          if int(Hours[k_index+n])>23:
            Hours[k_index+n]=str(0)
            HMS[k_index+n]=Hours[k_index+n]+":"+Minute[k_index+n]+":"+Second[k_index+n]
          S=str(Hours[k_index+n])+":"+str(Minute[k_index+n])+":"+str(Second[k_index+n])
          span.append(S)
  return HMS,ACT

data='/Users/hao/Desktop/實驗資料/健康組/品雯/029B005C_20200108(HRV).xlsx'
act_data= pd.read_excel(data,sheet_name='ACT&Illuminance')
