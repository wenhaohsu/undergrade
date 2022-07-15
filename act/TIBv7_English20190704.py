# -*- coding: utf-8 -*-
"""
Created on Fri Aug 24 09:49:24 2018

@author: Albert
"""
import xlsxwriter
from matplotlib.font_manager import FontProperties 
import pandas as pd
import matplotlib.pyplot as plt
import timeit
import time
import datetime
import os
import sys
import numpy as np
import matplotlib.dates as md
import matplotlib.patches as mpatches


# 將秒數轉成時分秒的形式(00:00:00)
def parseHMS(second):
  h=int(second/3600)
  m=int(second%3600/60)
  s=int(second%3600%60)
  return "{0:02.0f}:{1:02.0f}:{2:02.0f}".format(h,m,s)

def trandatetime(t):
  return datetime.time(int(t.split(' ')[1].split(":")[0]),int(t.split(' ')[1].split(":")[1]),int(t.split(' ')[1].split(":")[2]))
#  醒睡濾波
def getday(file):
  f=file.split(".txt")[0].split("/")[-1].split("_")[1]
  year=f[0:4]
  month=f[4:6]
  day=f[6:8]
  yday=datetime.date(int(year),int(month),int(day)) - datetime.timedelta(days=1)
  return str(yday).replace('-','/')

def filter_conscious(conscious,hms,wake_threshold,sleep_threshold):
  count_conscious=0    # 醒的次數
  count_unconscious=0  # 睡的次數
  conscious_time=[]    # 醒的時間
  unconscious_time=[]  # 睡的時間
  maxconscious_count=0 # 最大清醒次數
  maxunconscious_count=0 #最大睡的次數 
  max_con=[]  #存放最大清醒次數陣列
  max_uncon=[] #存放最大睡的次數陣列
  count_max_uncon=0
#  wake_threshold=2 # 20 秒
#  sleep_threshold=30
  if(conscious[0]==0):
    wake=0
  else:
    wake=1  
  for i in range(len(conscious)):
    if conscious[i]==1:
      count_conscious+=1
      if count_conscious>=wake_threshold:   # 大於等於40秒 為醒
        wake=1
     
      conscious_time.append(hms[i])
      maxconscious_count=count_conscious
      if maxunconscious_count!=0 :
        max_uncon.append(maxunconscious_count)
        unconscious_time.append(hms[i])
        count_max_uncon+=1
      if i==len(conscious)-1:
        max_con.append(maxconscious_count)
        
      if maxunconscious_count<sleep_threshold and wake==1:
        for j in range(maxunconscious_count):
          conscious[i-j-1]=1
          
#          print("Wake_Time: ",Time[i-j-1])
          conscious_time.append(hms[i-j-1])
      maxunconscious_count=0
      count_unconscious=0

    else:
      count_unconscious+=1
      maxunconscious_count=count_unconscious
      if count_unconscious>=sleep_threshold :  # 大於等於 15分鐘為睡
        wake=0

      if maxconscious_count!=0 :  
        max_con.append(maxconscious_count)
        if maxconscious_count<=wake_threshold and wake==0:
          for j in range(maxconscious_count):
            conscious[i-j-1]=0
      maxconscious_count=0
      count_conscious=0
      

def validate_date_str(date_str):
    try:
        datetime.datetime.strptime(date_str, '%H:%M:%S')
        return True
    except ValueError:
        return False


def extension(conscious,act_status,act):
    count_conscious=0
    count_unconscious=0
    exbefore=9
    exafter1=18
    exafter2=9
    ext1=False
    ext2=False

    detect_after=60
    for i in range(len(conscious)):
      if conscious[i]==1:
        count_conscious+=1
        count_unconscious=0
      else:
        count_unconscious+=1
        count_conscious=0
        
      if (act_status[i]==1 or act_status[i]==2) and conscious[i]==1:
        ext1=True
        ext2=False
      if act_status==0  and conscious[i]==1:
        ext2=True
        ext1=False  
        

        
      if count_conscious==1 and i>9 and len(conscious)-i>18 and ext1==True and conscious[i]==1 :
        count_index=0
        countact1=0
        if i+detect_after <len(conscious):
          for m in range(i,i+detect_after):
            if countact1==0 and act[m]==1:
              countact1+=1
              
            if act[m]>1 and countact1==1: 
              count_index=m
              break
          
        for j in range(exbefore):
          conscious[i-j-1]=1
          
        if count_index!=0:
          for k in range(exafter1):
            conscious[count_index+k]=1
#          print(count_index-i)
          for n in range(i,count_index):
            conscious[n]=1
        else:
          for k in range(exafter1):
            conscious[i+k]=1

      if count_conscious==1 and i>9 and len(conscious)-i>9 and ext2==True  and conscious[i]==1 :
        for j in range(exbefore):
          conscious[i-j-1]=1
        for k in range(exafter2):
          conscious[i+k]=1



def L5M10_draw(s,file,tib_start,tib_end,input_thre,wake_thres,sleep_thres): #s:command, wake:1(10s),sleep:18(10s)
  input_thre=float(input_thre)
  wake_thres=int(wake_thres)
  sleep_thres=int(sleep_thres)
  
  hst,mst,sst=map(int,tib_start.split(':'))
  hed,med,sed=map(int,tib_end.split(':'))
  stib_start="{0:02.0f}:{1:02.0f}:{2:02.0f}".format(hst,mst,sst)
  stib_end="{0:02.0f}:{1:02.0f}:{2:02.0f}".format(hed,med,sed)
  start = time.time()
  devicID=file.split(".txt")[0].split("/")[-1]
  y_bo=[]
  Time=[]
  Act=[]
  Time_before=[]
  Act_before=[]
  beforedata=[]
  date_before=[]
  date_after=[]
  syday=''
  
  allday=[]
  allday_time=[]
  allday_act=[]
  #將上床起床時間轉成 datetime格式
  tib_begin=datetime.time(int(tib_start.split(":")[0]),int(tib_start.split(":")[1]),int(tib_start.split(":")[2]))
  
  tib_ending=datetime.time(int(tib_end.split(":")[0]),int(tib_end.split(":")[1]),int(tib_end.split(":")[2]))
  print("tib_begin",tib_begin)
  print("tib_end",tib_end)
  day_begin=datetime.time(12,0,0)
  day_after=datetime.time(12,0,0)
  
  doc_name="sleep_"+devicID
  #os.chdir("..")
  cwd = os.getcwd()
#  directory=cwd+"/Sleep Report"+"/"+devicID.split('_')[0]
  directory0=cwd+"/"+devicID.split('_')[0]+"/Sleep Report"
  print(cwd)
  # directory0=devicID.split('_')[0]+"/Sleep_Report"
  try:
    os.stat(directory0)
  except:
    os.mkdir(directory0)
#  try:
#    os.stat(directory)
#  except:
#    os.mkdir(directory)
  #判斷上床時間是前一天還是當天 True則讀取前一天資料
  try:
#  if datetime.time(12,0,0)<tib_begin<datetime.time(23,59,59):
#    print("file",file.split(".txt")[0].split("\\")[-1].split("_")[1])
    f=file.split(".txt")[0].split("/")[-1].split("_")[1]
#    print('f:',f)
    year=f[0:4]
    month=f[4:6]
    day=f[6:8]

    yday=datetime.date(int(year),int(month),int(day)) - datetime.timedelta(days=1)
    syday=str(yday).replace('-','')
#    print('sday',syday)
    dbefore=file.split(f)[0]+syday+".txt"
    print('get yseterday ',dbefore)
  except:
    print("bug")
#      Date.append(line.split(' ')[0].split(',')[1])
#      Time.append(line.split(' ')[1].split(',')[0])
#      Act.append(line.split(',')[2])




  try:
    with open(dbefore, 'r', encoding='UTF-8',errors='ignore') as file0:
      for line in file0:
        if line.split(',')[0]==';PA':
          y_bo.append(line)
#          print(line)
  except:
    if datetime.time(12,0,0)<tib_begin<datetime.time(23,59,59):
      resultpath=cwd+"/web/"+devicID.split('_')[0]+"/"+"result.txt"
     
      if os.path.isfile(resultpath):
        with open(resultpath,'r+') as cf:
          line=cf.read()
#            line.insert(0,str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))+" "+dbefore+" not exist"+'\n')
          with open(resultpath,'w+') as cf:
           
            cf.write(str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))+" "+dbefore+" not exist"+'\n')
            cf.write(line)

      else:
        with open(resultpath,'w') as f :
          f.write(str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))+" "+dbefore+" not exist"+'\n')
#            print('創立 '+resultpath)
    tib_start='00:00:00'
    stib_start='00:00:00'
    tib_begin=datetime.time(0,0,0)
        
  for line in y_bo:
#      print(line)
    if line=="\n":
      continue
    hhh=line.split(" ")[1].split(",")[0].split(":")[0]
    mmm=line.split(" ")[1].split(",")[0].split(":")[1]
    sss=line.split(" ")[1].split(",")[0].split(":")[2]
    if datetime.time(int(hhh),int(mmm),int(sss))>day_begin:
      allday.append(line)
      allday_time.append(line.split(',')[1])
      allday_act.append(line.split(',')[2])
#        date_before_ALL.append(line.split(' ')[0].split(',')[1])
      
      
    if  datetime.time(int(hhh),int(mmm),int(sss))>tib_begin:
      beforedata.append(line)
      Time_before.append(line.split(',')[1])
      Act_before.append(line.split(',')[2])
      date_before.append(line.split(' ')[0].split(',')[1])
    
  if  Time_before==[]:
    
    new_syday=syday[0:4]+'/'+syday[4:6]+'/'+syday[6:8]
    Time_before.append(new_syday+" 23:59:50")
    Act_before.append(1)
    date_before.append(new_syday)

  else:

    Time_before.insert(len(Time_before),Time_before[0].split(' ')[0]+" 23:59:50")
#      print("OMGG")
    Act_before.insert(len(Time_before),"1")
#    print("Time_before[0]",Time_before[0])
  h0,m0,s0=Time_before[0].split(" ")[1].split(":")
    
#    print("h0:m0:s0  "+h0+m0+s0)
  if (int(h0)*3600+int(m0)*60+int(s0))-(int(tib_start.split(":")[0])*3600+int(tib_start.split(":")[1])*60+int(tib_start.split(":")[2]))>10:
    Time_before.insert(0,Time_before[0].split(' ')[0]+" "+tib_start)
#      print("OMGG")
    Act_before.insert(len(Time_before),"1")
#    print("Time_before[0]",Time_before[0])
  else:
    f=file.split(".txt")[0].split("/")[-1].split("_")[1]
    
    year=f[0:4]
    month=f[4:6]
    day=f[6:8]

    yday=datetime.date(int(year),int(month),int(day)) - datetime.timedelta(days=1)
    syday=str(yday)

    dbefore=file.split(f)[0]+syday+".txt"
#    print('dbefore'+dbefore)
    try:
      with open(dbefore, 'r', encoding='UTF-8',errors='ignore') as file0:
        for line in file0:
          if line.split(',')[0]==';PA':
            y_bo.append(line)
   
      for line in y_bo:
#        print(line)
        if line=="\n":
          continue
        hhh=line.split(" ")[1].split(",")[0].split(":")[0]
        mmm=line.split(" ")[1].split(",")[0].split(":")[1]
        sss=line.split(" ")[1].split(",")[0].split(":")[2]
        if datetime.time(int(hhh),int(mmm),int(sss))>day_begin:
          allday.append(line)
          allday_time.append(line.split(',')[1])
          allday_act.append(line.split(',')[2])
      if  allday_time==[]:
        new_syday=syday[0:4]+'/'+syday[4:6]+'/'+syday[6:8]
        allday_time.append(new_syday+" 23:59:50")
        allday_act.append(1)
        
    except:
      allday_time.append(getday(file)+" 23:50:50")
      allday_act.append(1)
#  print("allday_time",allday_time)
  if  allday_time==[]:
    new_syday=syday[0:4]+'/'+syday[4:6]+'/'+syday[6:8]
    allday_time.append(new_syday+" 23:59:50")
    allday_act.append(1)
  if allday_time[len(allday_time)-1].split(' ')[1]!=" 23:50:50":
    allday_time.insert(0,allday_time[len(allday_time)-1].split(' ')[0]+" 23:50:50")
    allday_act.insert(0,"1")
    # 讀取當天資料

  y_o=[]
  time_after=[]
  Act_after=[]
  
  with open(file,'r',encoding='utf-8',errors='ignore') as d:

    for line in d:
      
      if line=="\n":
        continue
#      print(line)
      if line.split(',')[0]==';PA':
#        print(line)
        y_o.append(line)
        time_after.append(line.split(',')[1])
        Act_after.append(line.split(',')[2])
        date_after.append(line.split(' ')[0].split(',')[1])
    d.close()
  print(time_after)
  if time_after[0].split(' ')[1]!="00:00:00":
    time_after.insert(0,time_after[0].split(' ')[0]+" 00:00:00")
#    print("OMG",time_after[0])
    Act_after.insert(0,"1")
#      date_after.append(line.split(";")[0].split(" ")[0])
  Time_after=[]
  All_Time_after=[]
  for i in range(len(time_after)):
    if datetime.time(int(time_after[i].split(' ')[1].split(":")[0]),int(time_after[i].split(' ')[1].split(":")[1]),int(time_after[i].split(' ')[1].split(":")[2]))<day_after:
      All_Time_after.append(time_after[i])
    if datetime.time(int(time_after[i].split(' ')[1].split(":")[0]),int(time_after[i].split(' ')[1].split(":")[1]),int(time_after[i].split(' ')[1].split(":")[2]))<tib_ending:
      Time_after.append(time_after[i])

  ACT=[]
  Hours=[]
  Minute=[]
  Second=[]
  #將前一天資料與當天資料併再一起，如果沒有就只有當天資料
  if datetime.time(12,0,0)<tib_begin<datetime.time(23,59,59):
    Act=Act_before+Act_after
    Time=Time_before+Time_after
  else:
    Act=Act_after
    Time=Time_after
#  print("Time",Time)
#  print("Time_after ",Time_after)
  AllDay_ACT=allday_act+Act_after
  AllDay=allday_time+ All_Time_after
  #  判斷第一個資料是不是00:00:00 開始
#  print("Time AFTER",Time_after)
  if datetime.time(0,0,0)<tib_begin<datetime.time(12,0,0):
    if Time[0].split(' ')[1]!="00:00:00":
      Time.insert(0,Time[0].split(' ')[0]+" 00:00:00")
      Act.insert(0,"1")
#  print(Time_before)
  if trandatetime(AllDay[0])>day_begin:
      AllDay.insert(0,AllDay[0].split(' ')[0]+" 12:00:00")
      AllDay_ACT.insert(0,"1")
  if trandatetime(AllDay[len(AllDay)-1])<day_begin:
      AllDay.insert(0,AllDay[len(AllDay)-1].split(' ')[0]+" 11:59:59")
      AllDay_ACT.insert(0,"1")
  checkh=0
#  print("TimeXX",Time[150:200])
#  print('allday_time',allday_time)
#  print('Time_after',Time_after)
#  print("Time",Time[len(Time)-1])

  #將有重複的時間剔除掉
  for check in Time :  
    if checkh==23 and int(check.split(":")[0].split(' ')[1])==0:
      continue
    if checkh>int(check.split(":")[0].split(' ')[1])  :   
      bug_index=Time.index(check)
     # print(Time[bug_index])
      Time.pop(bug_index)
      Act.pop(bug_index)
  for check in AllDay :  
    if checkh==23 and int(check.split(":")[0].split(' ')[1])==0:
      continue
    if checkh>int(check.split(":")[0].split(' ')[1])  :   
      bug_index=AllDay.index(check)
     # print(Time[bug_index])
      AllDay.pop(bug_index)
      AllDay_ACT.pop(bug_index)    
      
    checkh=int(check.split(":")[0].split(' ')[1])
   
  HMS=[]
  checkh=0

  data=[]    
  data2=[]
#  print("TIME",Time[150:200])
  #用時間將資料排序
  for i in range(len(AllDay)):
    data2.append([AllDay[i].split(" ")[0],AllDay[i].split(";")[0].split(' ')[1],AllDay_ACT[i]])
  
  for i in range(len(Time)):
    data.append([Time[i].split(" ")[0],Time[i].split(";")[0].split(' ')[1],Act[i]])
 
  data.sort( key=lambda x: (int(x[0].split("/")[0]),int(x[0].split("/")[1]),int(x[0].split("/")[2]),int( x[1].split(":")[0]),int( x[1].split(":")[1]),int( x[1].split(":")[2])))
  data2.sort( key=lambda x: (int(x[0].split("/")[0]),int(x[0].split("/")[1]),int(x[0].split("/")[2]),int( x[1].split(":")[0]),int( x[1].split(":")[1]),int( x[1].split(":")[2])))
  tempdata=0
  tempdata2=0
  deldata=[]
  deldata2=[]
  #再剔除有問題的資料一次
  for i in range(len(data)):
    if data[i][1]==tempdata:
      deldata.append(i-1)          
    tempdata=data[i][1] 

  for i in range(len(data2)):
    if data2[i][1]==tempdata2:
      deldata2.append(i-1)          
    tempdata2=data2[i][1] 

  for i in range(len(deldata)-1,0,-1):
    data.pop(deldata[i])    

  for i in range(len(deldata2)-1,0,-1):
    data2.pop(deldata2[i])    

  #  將活動量與時分秒存入陣列
  for x in range(len(data)):
#    Date.append(data[x][0])
    Hours.append(data[x][1].split(":")[0])
    Minute.append(data[x][1].split(":")[1])
    Second.append(data[x][1].split(":")[2])
    HMS.append(data[x][1])
    ACT.append(float(data[x][2]))
    Act.append(float(data[x][2]))
    
  Hours_ALL=[]
  Minute_ALL=[]
  Second_ALL=[]
  HMS_ALL=[]
  ACT_ALL=[]
  Act_ALL=[]
  for x in range(len(data2)):
#    Date.append(data[x][0])
    Hours_ALL.append(data2[x][1].split(":")[0])
    Minute_ALL.append(data2[x][1].split(":")[1])
    Second_ALL.append(data2[x][1].split(":")[2])
    HMS_ALL.append(data2[x][1])
    ACT_ALL.append(float(data2[x][2]))
    Act_ALL.append(float(data2[x][2]))
#  print('HMS_ALL: ',HMS_ALL)
    
  insertpointnumber=0  # 插入資料點數
  span=[]  #擴增的時間範圍
  span2=[]
  Timeleak=[] # 缺少那些時間資料點
  Timeleak2=[]
  insert_how_many=[] #插入多少點，存放insertpointnumber 的陣列
  insert_how_many2=[]
  time_in_s=[]  # 存放時間轉為秒數
  time_in_s_ALL=[]
  #將時間轉為秒數
  for i in range(len(HMS)):
    time_in_s.append(int(Hours[i])*60*60+int(Minute[i])*60+int(Second[i])) 
  for i in range(len(HMS_ALL)):
    time_in_s_ALL.append(int(Hours_ALL[i])*60*60+int(Minute_ALL[i])*60+int(Second_ALL[i])) 
    
  # 判斷第一筆資料是不是前一天資料，不是則為0秒(00:00:00)
  if (datetime.time(12,0,0)<tib_begin<datetime.time(23,59,59)):
    temptd=time_in_s[0]
  else:    
    temptd=0  
  temptd2=time_in_s_ALL[0]
#  print("time_in_s 30",time_in_s[20:26])
#  zoo=[]
  #與前一筆秒數相減
  for i in range(len(Second)):
    td=int(time_in_s[i])-temptd    
    if td>10:   # 秒數相減大於10秒
      insertpointnumber=int(td/10) #插入相減值除以10
      insert_how_many.append(insertpointnumber)   
      if i-1>=0:
        a=str(Hours[i-1])+":"+str(Minute[i-1])+":"+str(Second[i-1])+"-"+str(Hours[i])+":"+str(Minute[i])+":"+str(Second[i])
        Timeleak.append(a)
    temptd=int(time_in_s[int(i)])
  if (int(tib_end.split(":")[0])*3600+int(tib_end.split(":")[1])*60+int(tib_end.split(":")[2])-time_in_s[len(time_in_s)-1])>10:
    td=int(tib_end.split(":")[0])*3600+int(tib_end.split(":")[1])*60+int(tib_end.split(":")[2])-time_in_s[len(time_in_s)-1]
    if td>10:   # 秒數相減大於10秒
      insertpointnumber=int(td/10) #插入相減值除以10
      insert_how_many.append(insertpointnumber)   
    a=str(Hours[len(time_in_s)-1])+":"+str(Minute[len(time_in_s)-1])+":"+str(Second[len(time_in_s)-1])+"-"+tib_end
    Timeleak.append(a)
    
  for i in range(len(Second_ALL)):
    td=int(time_in_s_ALL[i])-temptd2    
    if td>10:   # 秒數相減大於10秒
      insertpointnumber=int(td/10) #插入相減值除以10
      insert_how_many2.append(insertpointnumber)   
      if i-1>=0:
        a=str(Hours_ALL[i-1])+":"+str(Minute_ALL[i-1])+":"+str(Second_ALL[i-1])+"-"+str(Hours_ALL[i])+":"+str(Minute_ALL[i])+":"+str(Second_ALL[i])
        Timeleak2.append(a)
    temptd2=int(time_in_s_ALL[int(i)])



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
            actvalue=(float(Act[k_index])+float(Act[k_index+1]))/2    
            ACT.insert(k_index+n,float(actvalue))
            Act.insert(k_index+n,str(actvalue))
          else:
            ACT.insert(k_index+n,float(1))
            Act.insert(k_index+n,str(1))
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

  for j in range(len(Timeleak2)):
    insertstarttime=Timeleak2[j].split("-")[0]
  
    if HMS_ALL.index(insertstarttime)>=0:
      k_index=0  
      for n in range(1,int(insert_how_many2[j])): 
          k_index=HMS_ALL.index(insertstarttime) 
          Second_ALL.insert(k_index+n,str(int(Second_ALL[k_index+n-1])+10))
          Minute_ALL.insert(k_index+n,str(int(Minute_ALL[k_index+n-1])))
          Hours_ALL.insert(k_index+n,str(int(Hours_ALL[k_index+n-1])))
          
          HMS_ALL.insert(k_index+n,Hours_ALL[k_index+n]+":"+Minute_ALL[k_index+n]+":"+Second_ALL[k_index+n])
          
          if insert_how_many2[j]==1:
            actvalue=(float(Act_ALL[k_index])+float(Act_ALL[k_index+1]))/2    
            ACT_ALL.insert(k_index+n,float(actvalue))
            Act_ALL.insert(k_index+n,str(actvalue))
          else:
            ACT_ALL.insert(k_index+n,float(1))
            Act_ALL.insert(k_index+n,str(1))
          if int(Second_ALL[k_index+n])>59:
            Second_ALL[k_index+n]=str(int(Second_ALL[k_index+n])-60)    
            Minute_ALL[k_index+n]=str(int(Minute_ALL[k_index+n])+1)
            HMS_ALL[k_index+n]=Hours_ALL[k_index+n]+":"+Minute_ALL[k_index+n]+":"+Second_ALL[k_index+n]
          if int(Minute_ALL[k_index+n])>59:
            Minute_ALL[k_index+n]=str(0)
            Hours_ALL[k_index+n]=str(int(Hours_ALL[k_index+n])+1)
            HMS_ALL[k_index+n]=Hours_ALL[k_index+n]+":"+Minute_ALL[k_index+n]+":"+Second_ALL[k_index+n]
          if int(Hours_ALL[k_index+n])>23:
            Hours_ALL[k_index+n]=str(0)
            HMS_ALL[k_index+n]=Hours_ALL[k_index+n]+":"+Minute_ALL[k_index+n]+":"+Second_ALL[k_index+n]
          S=str(Hours_ALL[k_index+n])+":"+str(Minute_ALL[k_index+n])+":"+str(Second_ALL[k_index+n])
          span2.append(S)
  time_in_second=[]
#  print(HMS_ALL)
  for i in range(len(HMS)):
#    print("Hour",Hours[i])
    if(datetime.time(int(Hours[i]),int(Minute[i]),int(Second[i]))<datetime.time(12,0,0) and datetime.time(12,0,0)<tib_begin<datetime.time(23,59,59)):
      time_in_second.append((int(Hours[i])+24)*60*60+int(Minute[i])*60+int(Second[i])) 
    else:
      time_in_second.append(int(Hours[i])*60*60+int(Minute[i])*60+int(Second[i])) 
#  print("HMS",HMS[0:500])

  x1=[]
  x2=[]
  x3=[]

 
  print("tib_start",tib_start)
 

  y1=ACT[0:len(Second)]

  end = time.time()
  elapsed = end - start
  
  if(datetime.time(12,0,0)<tib_begin<datetime.time(23,59,59)):
    tib_end_insecond=(int((tib_end.split(":")[0]))+24)*3600+int(tib_end.split(":")[1])*60+int(tib_end.split(":")[2])
  else:
    tib_end_insecond=int(tib_end.split(":")[0])*3600+int(tib_end.split(":")[1])*60+int(tib_end.split(":")[2])
  tib_start_insecond=int(tib_start.split(":")[0])*3600+int(tib_start.split(":")[1])*60+int(tib_start.split(":")[2])
  TIB=tib_end_insecond-tib_start_insecond

  if(TIB<0):
    TIB=(tib_end_insecond+24)*3600-tib_start_insecond

  count_tib=0
  count_tib_index=0
  for j in time_in_second:
    if j<tib_start_insecond:
      count_tib_index=time_in_second.index(j)  
      continue      
    elif  tib_start_insecond <= j <= tib_end_insecond :
      count_tib+=1
    else:
      break    

   
  
  start_index=0
  end_index=len(HMS)-1
  for i in range(len(HMS)):
    a=datetime.time(int(HMS[i].split(":")[0]),int(HMS[i].split(":")[1]),int(HMS[i].split(":")[2]))
#    print("a",a)
    if a>=tib_begin:
        start_index=i
        break
    
    
  for i in range(len(HMS)):
    b=datetime.time(int(HMS[i].split(":")[0]),int(HMS[i].split(":")[1]),int(HMS[i].split(":")[2]))
#    print("b",b)
    if b>=tib_ending and datetime.time(0,0,0)<b<datetime.time(12,0,0):
        end_index=i
        break
  
  start_index2=0
  end_index2=len(HMS_ALL)-1
  for i in range(len(HMS_ALL)):
    a=datetime.time(int(HMS_ALL[i].split(":")[0]),int(HMS_ALL[i].split(":")[1]),int(HMS_ALL[i].split(":")[2]))

#    print("a",a)
    if datetime.time(12,0,0)<tib_begin<datetime.time(23,59,59): #睡覺時間在23:59:59之前
      if a>=tib_begin :
        start_index2=i
        break
    else:
      if a>=tib_begin and a<(datetime.time(12,0,0)) :
        start_index2=i
        break    
    
  for i in range(len(HMS_ALL)):
    b=datetime.time(int(HMS_ALL[i].split(":")[0]),int(HMS_ALL[i].split(":")[1]),int(HMS_ALL[i].split(":")[2]))
#    print("b",b)
    if b>=tib_ending and datetime.time(0,0,0)<b<datetime.time(12,0,0):
        end_index2=i
        break



  
  
  conscious=[]
  actsum=[]
  

  for i in range(len(HMS)):         #整個時間軸的sliding window
    if i>=13 and i<=len(HMS)-14:    #時間長度夠的情況下
      Aact=sum(ACT[i-13:i-2])       #往前數4個epoch(120s)的總和
      Bact=sum(ACT[i+2:i+13])       #往後數4個epoch(120s)的總和
#      print('Aact',Aact)
#      print('Bact',Bact)
      act_now=float(ACT[i-1])+float(ACT[i])+float(ACT[i+1])
      act_critical=Aact+Bact+act_now#當下的1個epoch(30s)
      actsum.append(act_critical)   #計算act的總和
      if act_critical>input_thre:   #如果大於threshold
        if Aact<12 and Bact<12:     #當前後的epoch不足4個
          conscious.append(0)       #
        else:  
          conscious.append(1)
      else:
        conscious.append(0)
    else:
        conscious.append(0)
        actsum.append(0)

  act_status=[]

  act_low=input_thre
  for i in range(len(actsum)):
    if actsum[i]<act_low:
      act_status.append(0)
    elif act_low<=actsum[i]<=900:
      act_status.append(1)  
    else: 
      act_status.append(2)
    
    
    
    
    
#  conscious_before=conscious[start_index:end_index]
      

  filter_conscious(conscious,HMS,wake_thres,sleep_thres)

  new_conscious=conscious[start_index:end_index]
  
  new_HMS=HMS[start_index:end_index]

#  filter_conscious(new_conscious,new_HMS)
  sleep_latency=0
  sleep_time=''
  new_uncon_count=0
  sleep_time_index=0
#  print("new_HMS[0:6]",new_HMS[0:6])
  for i in range(len(new_conscious)):
    if new_conscious[i]==0:
      new_uncon_count+=1;
      if new_uncon_count==6:
        sleep_time=new_HMS[i]
        sleep_time_index=i
#        print("i",i)
        print("sleep_time",sleep_time)
        break
    else:
      new_uncon_count=0
  sleep_time_in_s=int(sleep_time.split(":")[0])*3600+int(sleep_time.split(":")[1])*60+int(sleep_time.split(":")[2])-60
  tib_in_s=(int(tib_start.split(":")[0])*3600+int(tib_start.split(":")[1])*60+int(tib_start.split(":")[2]))
#  print("sleep_time_in_s",sleep_time_in_s)
#  print("tib_in_s",tib_in_s)
  sleep_latency_in_second= (sleep_time_in_s-tib_in_s)
  
  if (sleep_latency_in_second<0) :
      
    if tib_in_s>43200 :
      if abs(sleep_latency_in_second)<60:
        sleep_latency_in_second=0  
      else:
        sleep_latency_in_second= ((int(sleep_time.split(":")[0])+24)*3600+int(sleep_time.split(":")[1])*60+int(sleep_time.split(":")[2]))-(int(tib_start.split(":")[0])*3600+int(tib_start.split(":")[1])*60+int(tib_start.split(":")[2]))
    else: 
      sleep_latency_in_second=0  
  sleep_latency=parseHMS(sleep_latency_in_second) 
  
  
  
  sleep_latency_act=0
  sleep_latency_act=sum(ACT[count_tib_index+1:count_tib_index+1+sleep_time_index])
  if sleep_latency=="00:00:00":
    sleep_latency_act=0
  print("sleep_latency_act",sleep_latency_act)
  print("count_tib_index",count_tib_index)

  print("sleep_latency",sleep_latency)



  Date=[]
#  print("len HMS",len(HMS))
  Date_ALL=[]
  for i in range(len(HMS)):
    b=datetime.time(int(HMS[i].split(":")[0]),int(HMS[i].split(":")[1]),int(HMS[i].split(":")[2]))
    if (datetime.time(12,0,0)<b<=datetime.time(23,59,59) and datetime.time(12,0,0)< tib_begin<=datetime.time(23,59,59)):
      Date.append(date_before[0])
    else:
      Date.append(date_after[0])
  for i in range(len(HMS_ALL)):
    b=datetime.time(int(HMS_ALL[i].split(":")[0]),int(HMS_ALL[i].split(":")[1]),int(HMS_ALL[i].split(":")[2]))
    if datetime.time(12,0,0)<= b <=datetime.time(23,59,59) :
      Date_ALL.append(getday(file))
    else:
      Date_ALL.append(date_after[0])
#  print("Date_All",Date_ALL)
#  print(HMS)
  waso_time=[]
  count_conscious=0

  for i in range(len(new_HMS)):
    if new_conscious[i]==1:
      count_conscious+=1
      if count_conscious==1:
        waso_time.append(new_HMS[i])
        
      else:
        continue
    else:
      count_conscious=0
      
  print("waso_time",waso_time)
  waso=len(waso_time)
  if waso==0:
    waso=1
  print("waso:",waso)
  count_conscious=0

  start=time_in_second[start_index]
  end=time_in_second[end_index]

  for i in range(len(new_HMS)):
    if new_conscious[i]==1:
      count_conscious+=1
    


  Total_sleep_time=parseHMS(((TIB)-count_conscious*10))
  print("Total_sleep_time",Total_sleep_time)
  wake_duration=parseHMS(count_conscious*10)
  print("wake_duration:",wake_duration)
  sleep_efficiency=(TIB-count_conscious*10)/TIB
  sleep_eff="{0:2.2f}".format(sleep_efficiency*100)
  print("sleep_efficiency: {0:2.2f} %".format(sleep_efficiency*100))
  wa=count_conscious*10-sleep_latency_in_second
  WASO=parseHMS(count_conscious*10-sleep_latency_in_second)
  if wa<0:
    WASO=parseHMS(0)
  
  act_in_sleep=0
  for i in range(start_index,end_index):
    act_in_sleep=ACT[i]+act_in_sleep

  calorie=act_in_sleep*1.65*10**(-4)+0.053
  scalorie="{0:2.2f}".format(calorie)

  with open(doc_name+".txt",'w') as f:
    f.write("Sleep_Efficiency(%)," + sleep_eff+"\n")
    f.write("Total_Sleep_Time,"+Total_sleep_time+"\n")
    f.write("TIB,"+parseHMS(TIB)+"\n")
    f.write("TIB_From," +stib_start+"\n")
    f.write("TIB_To,"+stib_end+"\n")
    f.write("Wake_Duration,"+wake_duration+"\n")
    f.write("Sleep_Latency,"+sleep_latency+"\n")
    f.write("WASO,"+WASO+"\n")
    f.write("Total_Activity(mG),"+"{0:2.2f}".format(act_in_sleep)+"\n")
    f.write("Activity_in_Sleep_Latency(mG),"+"{0:2.2f}".format(sleep_latency_act)+"\n")
    f.write("Activity_in_WASO(mG),"+ "{0:2.2f}".format(act_in_sleep-sleep_latency_act)+"\n")
    f.write("Calorie(cal),"+scalorie+"\n")
    f.write("Number_of_Awakenings,"+str(waso-1))
#
#  book = xlsxwriter.Workbook(directory0+"/"+doc_name+".xlsx")
#  bold = book.add_format({'bold': True,'align':'left','color': '#000000',
#    'valign': 'vcenter','text_wrap': True,'font_name':'calbri'})
#  bold1 =book.add_format({'align':'left','color': '#000000',
#    'valign': 'vcenter','text_wrap': True,'font_name':'calbri'})
#  merge_format = book.add_format({'bold': 1,'border': 1,'align': 'left','valign': 'vcenter','font_size':18,'font_name':'calbri'})
#  merge_format1 = book.add_format({'bold': 1,'border': 1,'align': 'left','valign': 'vcenter','font_size':15,'text_wrap': True,'font_name':'calbri'})
#  color1=book.add_format({'align':'right','valign': 'vcenter','font_name':'calbri','bold': 1})
#  color2=book.add_format({'align':'right','valign': 'vcenter','font_name':'calbri'})
#  superscript = book.add_format({'font_script': 8,'text_wrap': True,'align': 'left','valign': 'vcenter','font_name':'calbri'})
#  sheet_1 = book.add_worksheet('Sleep Report')
#  sheet_1.write(1,0,'')
#  sheet_1.write_rich_string(8,1,bold1,"TIB From \n","(HH:MM:SS)",superscript)
#  sheet_1.write_rich_string(9,1,bold1,'TIB To\n','(HH:MM:SS)',superscript)
#  sheet_1.write_rich_string(7,1,bold,'TIB \n','(HH:MM:SS)',superscript)
#  sheet_1.write_rich_string(12,1,bold1,'Sleep Latency \n','(HH:MM:SS)',superscript)
#  sheet_1.write_rich_string(11,1,bold,'Wake Duration\n','(HH:MM:SS)',superscript)
#  sheet_1.write_rich_string(13,1,bold1,'WASO \n','(HH:MM:SS)',superscript)
#  sheet_1.write_rich_string(5,1,bold,'Total Sleep Time\n ','(HH:MM:SS)',superscript)
#  sheet_1.write_rich_string(4,1,bold,'Sleep Efficiency\n','(%)',superscript)
#  sheet_1.write_rich_string(15,1,bold1,'Total Activity \n', '(mg)',superscript)
#  sheet_1.write_rich_string(16,1,bold1,'Activity in sleep Latentency \n', '(mg)',superscript)
#  sheet_1.write_rich_string(17,1,bold1,'Activity in WASO \n', '(mg)',superscript) 
#  sheet_1.write_rich_string(18,1,bold1,'Calorie\n','(cal)',superscript)
#  sheet_1.write_rich_string(19,1,bold1,'Number of awakenings\n')
# 
##  sheet_1.write(1,0,'Time',bold)
#  sheet_1.set_column("A:A", 5)
#  sheet_1.set_column("B:C", 23)
##  sheet_1.set_column("D:J", 15)
##  sheet_1.set_column("H:K", 20)
#  sheet_1.set_row(1, 60)
#  sheet_1.merge_range('B1:C1',"Daily Sleep Report", merge_format)
#  sheet_1.merge_range('B2:C2',"Date \n"+ Date[0] + "  "+tib_start+" ~ \n"+ Date[count_tib_index+count_tib-1] +"  "+tib_end, merge_format1)
#  
#  sheet_1.write(8,2,tib_start,color2)
#  sheet_1.write(9,2,tib_end,color2)
#  sheet_1.write(7,2,parseHMS(TIB),color1)
#  sheet_1.write(12,2,sleep_latency,color2)
#  sheet_1.write(11,2,wake_duration,color1)
#  sheet_1.write(13,2,WASO,color2)
#  sheet_1.write(5,2,Total_sleep_time,color1)
#  sheet_1.write(4,2,sleep_eff,color1)
#  sheet_1.write(15,2,act_in_sleep,color2)
#  sheet_1.write(16,2,sleep_latency_act,color2)
#  sheet_1.write(17,2,act_in_sleep-sleep_latency_act,color2)
#  sheet_1.write(18,2,scalorie,color2)
#  sheet_1.write(19,2,waso-1,color2)
#  
#  book.close()
#  print("HMS",HMS)
  day_temp=[]
  month_temp=[]
  year_temp=[]
  day_temp2=[]
  month_temp2=[]
  year_temp2=[]
  for i in range(len(HMS)):
    day_temp.append(Date[i].split("/")[2])
    month_temp.append(Date[i].split("/")[1])
    year_temp.append(Date[i].split("/")[0])
  for i in range(len(HMS_ALL)):
    day_temp2.append(Date_ALL[i].split("/")[2])
    month_temp2.append(Date_ALL[i].split("/")[1])
    year_temp2.append(Date_ALL[i].split("/")[0])

  for i in range(0,len(Second)):
    da=datetime.time(int(Hours[i]),int(Minute[i]),int(Second[i]))
    x1.append(da)
  
  x4=[]
  for i in range(count_tib_index,count_tib_index+count_tib-1):
    da=datetime.datetime(int(year_temp[i]),int(month_temp[i]),int(day_temp[i]),int(Hours[i]),int(Minute[i]),int(Second[i]))
    x4.append(da)  
    
  x5=[]
  for i in range(len(Date_ALL)):
    da=datetime.datetime(int(year_temp2[i]),int(month_temp2[i]),int(day_temp2[i]),int(Hours_ALL[i]),int(Minute_ALL[i]),int(Second_ALL[i]))
    x5.append(da)
#  print('x5',x5)
#  for i in range(10):
#    print("Draw_last_point",x4[i])
  y2=conscious [count_tib_index:count_tib_index+count_tib-1]
  y4=ACT[count_tib_index:count_tib_index+count_tib-1]
  y5=act_status[count_tib_index:count_tib_index+count_tib-1]
  y6=ACT_ALL

  fig2 = plt.figure(figsize=(7.5,5))
  fig2.subplots_adjust( hspace=0.24,right=0.98,left=0.13,top=0.98,bottom=0.1)
#  font = FontProperties(fname=r"c:\windows\fonts\msjh.ttc", size=14) 
  font = FontProperties(size=10)
  font2 = FontProperties(size=14)
  print ("Sleep_time: ",sleep_time)      
#  print('x4',x4)
  yy2=np.array([0,1])
  yy3=np.array([0,1,2])
  fig2.add_subplot(3,1,2)
  ytick=[u"Sleep",u"Wake"]
  ax=plt.gca()
  for label in ax.get_yticklabels():
      label.set_fontproperties(font)
  plt.ylabel(u"Sleep-Wake Pattern",fontproperties=font).set_fontsize(10)
  plt.ylim(-0.1,1.1)
  plt.yticks(yy2, ytick)
  plt.plot(x4,y2,'r')

  x=md.DateFormatter('%H:%M:%S')  
  ax.xaxis.set_major_formatter(x)

  fig2.add_subplot(3,1,1)
  plt.plot(x4,y4,'g')
  plt.ylabel(u"PA (mG)",fontproperties=font).set_fontsize(10)
  plt.yscale('log')
  ax=plt.gca()
  x=md.DateFormatter('%H:%M:%S')  
  ax.xaxis.set_major_formatter(x)

  fig2.add_subplot(3,1,3)
  ytick2=[u"Low",u"Medium",u"High"]
  ax2=plt.gca()
  
  title="Date  "+ Date[0] + "  "+tib_start+" ~ "+"Date  "+ Date[count_tib_index+count_tib-1] +"  "+tib_end
#  print("Date",day_temp)
  for label in ax2.get_yticklabels():
      label.set_fontproperties(font)
  plt.ylabel(u"Actiprofile",fontproperties=font).set_fontsize(10)
  plt.ylim(-0.1,2.1)  
  plt.yticks(yy3, ytick2)
  plt.plot(x4,y5,'b')
  plt.xlabel(title).set_fontsize(14)
#  plt.xlim(x4[0],x4[len(x4)-1])
  x=md.DateFormatter('%H:%M:%S')  
  ax2.xaxis.set_major_formatter(x)
  
  print("Time taken: ", elapsed, "seconds.")
  
#  plt.show()
  fig2.savefig(doc_name+".jpg",dpi=300)
  fig3 = plt.figure(figsize=(7.5,5))
  fig3.subplots_adjust( hspace=0.24,right=0.97,left=0.09,top=0.93,bottom=0.11)
  plt.plot(x5,y6,'r')
#  plt.stem(x5,y6, markerfmt=" ")
  plt.ylabel(u"PA ( mG )",fontproperties=font2).set_fontsize(14)
  plt.yscale('log')
#  plt.xlim(x5[0]-0.1,x5[len(x5)-1]+0.1)
  ax=plt.gca()
  
  x=md.DateFormatter('%H:%M:%S')  
  xlocator = md.HourLocator(interval = 4)
  ax.xaxis.set_major_locator(xlocator)
  ax.xaxis.set_major_formatter(x)
#  print("max(x5)",max(x5))
  ax.fill_between(x5[start_index2:end_index2], 0,max(y6)+1000, alpha=0.5, color='grey' )
  plt.xlabel("Date  "+ syday.replace('-','/') +" 12:00:00 ~ Date "+ Date[count_tib_index+count_tib-1] +" 12:00:00").set_fontsize(14)
  plt.title("Daily Activity").set_fontsize(18)
  grey_patch = mpatches.Patch(color='grey', label='TIB', alpha=0.5)
  plt.legend(handles=[grey_patch])

  fig3.savefig(directory0+"/"+doc_name+'allday'+".jpg",dpi=300) 
#  print('syday',syday)
#
def main(script,filepath,tib_start,tib_end,input_thre,wake_thre,sleep_thre):
  if len(sys.argv)>6:
    L5M10_draw(script,filepath,tib_start,tib_end,input_thre,wake_thre,sleep_thre)       
  else:
    sys.argv[0]=script  
    sys.argv[1]=input('enter argument: ')
    
if __name__ == '__main__':
  main(sys.argv[0],sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4],sys.argv[5],sys.argv[6])
#L5M10_draw('s',r'D:\xds\web\02250007\02250007_20190511.txt', '00:00:00', '06:00:00', '139', '1', '18')



