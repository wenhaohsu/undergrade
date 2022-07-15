#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct  7 01:27:10 2019

@author: chenghan
"""

import requests
import pandas as pd
import matplotlib.pyplot as plt

import numpy as np

import math
import torch
import json
from datetime import datetime
import threading
#self define class
import ecg_cuda_competition as ec
from dataDecode import dataDecode
from Line_function import Line_function 

def medfilt (x, k):
    """Apply a length-k median filter to a 1D array x.
    Boundaries are extended by repeating endpoints.
    """
    assert k % 2 == 1, "Median filter length must be odd."
    assert x.ndim == 1, "Input must be one-dimensional."
    k2 = (k - 1) // 2
    y = np.zeros ((len (x), k), dtype=x.dtype)
    y[:,k2] = x
    for i in range (k2):
        j = k2 - i
        y[j:,i] = x[:-j]
        y[:j,i] = x[0]
        y[:-j,-(i+1)] = x[j:]
        y[-j:,-(i+1)] = x[-1]
    return np.median (y, axis=1)

#def ECGscanning():
userprofile_list=[]
format = '%Y/%m/%d %H:%M:%S'
r=requests.get("https://script.google.com/macros/s/AKfycbxkiEZ3GUj0kwsr4d_EGnoTxzb5UdW1LQRpiOBT0_ATubm6-h0/exec?GETID=all")
jsontemp=json.loads(r.text)
for i in range(len(jsontemp)):
    if '0060' in jsontemp[i]['XID']:
        userprofile_list.append(jsontemp[i])
        
for j in range(len(userprofile_list)):        
    
    
    XID=userprofile_list[j]['XID']
    if len(XID)==9:
        XID=XID[1:len(XID)]
    user_lineID=userprofile_list[j]['USERID']
    username=userprofile_list[j]['LOC']
    
    
    severdns="xds.ym.edu.tw:81"
    urlstart="http://"+severdns+"/"+XID+"/latest.txt"
    
    r = requests.get(urlstart)
    latest_filename=r.text.split("\r\n")[0]
 
    if r.status_code==404:
        continue
 
    urlstart="http://"+severdns+"/"+XID
    r = requests.get(urlstart)
    rawtxt=r.text  
    
    XIDfolder_list=rawtxt.split('/r/n')
    isoffline=False

    for i in range(len(XIDfolder_list)):
        if latest_filename in XIDfolder_list[i]:
            datetimelist= XIDfolder_list[i].split("<a")[0].split(' ')
            datetime_diff=datetime.now()-datetime.strptime(datetimelist[0]+' '+datetimelist[1], format)
            print(datetime_diff.total_seconds)
            if datetime_diff.total_seconds()>25:
                isoffline=True
                break
            elif datetime_diff.total_seconds()>15:
                isoffline=True
                
                Line_function.pushRequest_xenonhelper(XID+' 設備離線',user_lineID)
                
                break
    if isoffline:
        continue
    
    urlstart="http://"+severdns+"/"+XID+"/"+latest_filename
    r = requests.get(urlstart)
    rawtxt=r.text
    

    

    
    #print(rawtxt)
    Data,sampling_rate=dataDecode.rawdataDecode(rawtxt)
    
    duration=10
    Data_len=int(sampling_rate)*duration
    Data_from=len(Data[0])-Data_len
    
    
    vector=Data[0][Data_from:Data_from+Data_len]#-medfilt(np.array(Data[0][Data_from:Data_from+Data_len]),125)
    plt.plot(vector)
#   plt.plot(medfilt(np.array(Data[0][Data_from:Data_from+Data_len]),125))
    col = {"HR" : vector}
    data = pd.DataFrame(col)
    
    
        
    xs = [i for i in np.linspace(Data_len)]
    x1 = np.linspace(0, duration, len(xs))  #這地方應該改成linspace,
    x_time=[]
    for x in x1:
        x_time.append(x)
    
    
    
    hrw = 0.75 #One-sided window size, as proportion of the sampling frequency
    fs = 250 #The example dataset was recorded at 100Hz
    mov_avg = data['HR'].rolling(int(hrw*fs)).mean() #Calculate moving average
    #Impute where moving average function returns NaN, which is the beginning of the signal where x hrw
    
    avg_hr = (np.mean(data.HR))
    mov_avg = [avg_hr if math.isnan(x) else x for x in mov_avg]
    mov_avg = [x*1.04 for x in mov_avg] #For now we raise the average by 20% to prevent the secondary heart contraction from interfering, in part 2 we will do this dynamically
    data['HR_rollingmean'] = mov_avg #Append the moving average to the dataframe
    #Mark regions of interest
    window = []
    peaklist = []
    listpos = 0 #We use a counter to move over the different data columns
    for datapoint in data.HR:
        rollingmean = data.HR_rollingmean[listpos] #Get local mean
        if (datapoint < rollingmean) and (len(window) < 1): #If no detectable R-complex activity -> do nothing
            listpos += 1
        elif (datapoint > rollingmean): #If signal comes above local mean, mark ROI
            window.append(datapoint)
            listpos += 1
        else: #If signal drops below local mean -> determine highest point
            #maximum = max(window)
            beatposition = listpos - len(window) + (window.index(max(window))) #Notate the position of the point on the X-axis
            peaklist.append(beatposition) #Add detected peak to list
            window = [] #Clear marked ROI
            listpos += 1
    ybeat = [data.HR[x] for x in peaklist] #Get the y-value of all peaks for plotting purposes
    
#    print(len(peaklist))
    pred_list = []
    
    for index in peaklist:
    
        #cut R peak，計算切割區間(以R peak為中心的300ms)
        epoch_len=175
        cut1 = index-math.floor(epoch_len/2)#(x_time[index] - (350/1000))*250    
        cut2 = index+round(epoch_len/2)#(x_time[index] + (350/1000))*250
    #    print(cut1)
    
        if len(vector[int(cut1):int(cut2)])<epoch_len:
            break
        plt.plot(vector[int(cut1):int(cut2)])
        
        testData=pd.DataFrame(vector[int(cut1):int(cut2)]) 
        cnn = ec.CNN()
        #%%
        #optimizer,loss_func = ec.parameter_use('params_cnn_2019_9_13.pkl',lr = 0.01)
        test = testData
        testdata = torch.from_numpy(test.values.astype(float).reshape(1,1,epoch_len)).type(torch.FloatTensor)
        pred_as = []
        cnn.load_state_dict(torch.load('params_cnn_175_2019_10_18.pkl',map_location=torch.device('cpu')))
        test_output = cnn(testdata[0:epoch_len])
        _, pred = test_output.max(1)
        pred = pred.data.numpy() 
        pred_list.append(pred[0])
        
        
    if len(peaklist)==0:
            message=username+'\n此設備沒有偵測到ECG' 
            Line_function.pushRequest_xenonhelper(message,user_lineID)
            continue
        
    isabnormal=False     
    for i in range(len(pred_list)):
        if pred_list[i]==1:
            isabnormal=True
            message=username+'\n偵測到異常\n查看:http://kylab.ap-northeast-1.elasticbeanstalk.com/ecgmonitor/?XID='+XID+'&LEN='+str(Data_from)+"&LATEST="+latest_filename
            Line_function.pushRequest_xenonhelper(message,user_lineID)
            break       
    if isabnormal:
        continue
    print('normal')
                
'''   
                  var CHANNEL_ACCESS_TOKEN = 'Nzyyv6xValODf0H+n6Bt5JZcWo2Bj2Q9FFSWMbbDUhri/XnZ5Q71MIPapidjawRkByiAPB7c3D+DPnbXVVfXaCpWA0h2jQ4xvFuPT3eOmnxH7ZVh1BUqTTgki3WqB/+mIL1C4sP5SLe58eoyfAe2xgdB04t89/1O/w1cDnyilFU=';
          var ;
          UrlFetchApp.fetch(url, {
            'headers': {
              'Content-Type': 'application/json; charset=UTF-8',
              'Authorization': 'Bearer ' + CHANNEL_ACCESS_TOKEN,
            },
            'method': 'post',
            'payload': JSON.stringify({
              'to': to,
              'messages': [{
                'type': 'text',
                'text': e,
              }],
            }),
          }); 
        }
        
'''       
        
#threading.Timer(10, ECGscanning).start()     







#plt.subplot(2,1,1)
#plt.plot(Data[0][(len(Data[0])-500):len(Data[0])], 'k')
#plt.xlabel('Point(CH1)')
#plt.ylabel('Volts')
#plt.subplot(2,1,2)
#plt.plot(Data[1][(len(Data[1])-500):len(Data[1])], 'k')
#plt.xlabel('Point(CH2)')
#plt.ylabel('Volts')
##Datelist=[]
##
##if ("404 Not Found" in rawtxt):
##    print ("No data")
##else:
##    rawlist=rawtxt.split("<br>")
##    for i in range(len(rawlist)):
##        if XID in rawlist[i] and "txt" in rawlist[i]: 
##            DateXID=rawlist[i].split(">")[1]
##            DateXID=DateXID.replace(".txt</a","")
##            templist=DateXID.split("_")
##            if len(templist)==3:
##                Datelist.append(templist[1]+"_"+templist[2])
##            else:   Datelist.append(templist[1])
##    
