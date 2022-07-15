#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 10 16:57:13 2020

@author: hao
"""

import requests
import json
import pandas as pd
from datetime import datetime,timedelta

class biodata_m:
    biodata_type=''
    RFID=''
    xid=''
    bphr=0
    sys=0
    dia=0
    gu=0
    hr=0
    sd=0
    hf=0
    lf=0
    tp=0
    vl=0
    records=''
    recorde=''
    total_record_time=0
    baseline=0
    mean=0
    lowest=0
    sbo=0
    ode=0
    ahi=0
    ref=''
    datadate=''
    datatime=''
    status=''
    
    def biodata_init(self):
        self.biodata_type=''
        self.RFID=''
        self.xid=''
        self.bphr=0
        self.sys=0
        self.dia=0
        self.gu=0
        self.hr=0
        self.sd=0
        self. hf=0
        self. lf=0
        self.tp=0
        self.vl=0
        self.records=''
        self.recorde=''
        self.total_record_time=0
        self.baseline=0
        self.mean=0
        self.lowest=0
        self.sbo=0
        self.ode=0
        self.ahi=0
        self.ref=''
        self.datatime=''
        self.status=''
def getSAreport(xid,time,ptime):
    biodata=biodata_m()
    spo2dns='http://kylab.ap-northeast-1.elasticbeanstalk.com/spo2/?'
    r=requests.get(spo2dns+'XID='+xid+'&starttime='+time+'&stoptime='+ptime)
    jsontemp=json.loads(r.text)
    biodata.status=jsontemp['code']
    if jsontemp['code']=='S01':
        biodata.xid=jsontemp['ID']
        biodata.baseline=jsontemp['Report']['Baseline']
        biodata.mean=jsontemp['Report']['Mean']
        biodata.lowest=jsontemp['Report']['Lowest']
        biodata.ode=jsontemp['Report']['Oxygen_desaturation_event']
        biodata.ahi=jsontemp['Report']['Estimated_AHI']
        biodata.ref=jsontemp['Report']['Estimated_SA']
        biodata.total_record_time=jsontemp['Report']['Total_record_time']
        biodata.records=jsontemp['Report']['Record_time']['Start']
        biodata.recorde=jsontemp['Report']['Record_time']['End']
        biodata.biodata_type='SPO2'
    return biodata,biodata.ode
def get_post(tilt,roll,Y_axis,Z_axis):
    state = []
    posture=[]
    method1=45
    method2=135
    for i in range(len(tilt)):
        if abs(tilt[i]) >= method1:
            posture.append(5)
            state.append(2)
        else:
            if abs(roll[i])<(method1) or abs(roll[i])>(method2):
                if Y_axis[i]>= 0:
                    posture.append(2) #right
                    state.append(1)
                else:
                    posture.append(3) #left
                    state.append(1)
            else:
                if Z_axis[i]>= 0:
                    posture.append(1) #supine
                    state.append(1)
                else:
                    posture.append(4) #prone
                    state.append(1)
    return posture,state

xls = pd.ExcelFile('\\Users\\Jonathan Chen\\Desktop\\收案data\\介入\\氣功\\謝翠蘋\\第一週\\HRV\\0395005A_20191231(HRV).xlsx')
sheetX = xls.parse('HR&ACT')
sheetX=sheetX.rename(columns={'Unnamed: 0':'TIME'})
XID='01d60040'
spo2date='20191230'
posture2,state2=get_post(sheetX['tilt_derive'],sheetX['roll_derive'],sheetX['Y'],sheetX['Z'])
sheetX['Posture2']=posture2
Posture_dic={"1":[],"2":[],"3":[],"4":[],"5":[]}
#%%
latest_posture=0
latest_hour=-1
starttime=""
for i in range(len(sheetX['Posture2'])):
    if latest_hour==23 and int(sheetX['TIME'][i].split(':')[0])==0:
        spo2date=(datetime.strptime(spo2date, "%Y%m%d")+timedelta(days=1)).strftime("%Y%m%d")
        latest_hour=int(sheetX['TIME'][i].split(':')[0])
        print("hello")
    else:
        latest_hour=int(sheetX['TIME'][i].split(':')[0])
        
    if (latest_posture!=sheetX['Posture2'][i]) and (i!=0):
        Posture_dic[str(latest_posture)].append({"start":starttime,"end":spo2date+" "+sheetX['TIME'][i-1]})
        latest_posture=sheetX['Posture2'][i]
        starttime=spo2date+" "+sheetX['TIME'][i]
    elif i==0:
        latest_posture=sheetX['Posture2'][i]
        starttime=spo2date+" "+sheetX['TIME'][i]
    else:
        latest_posture=sheetX['Posture2'][i]
#%%        
Posture_keystore=list(Posture_dic.keys())
for i in range(len(Posture_keystore)):
    for j in range(len(Posture_dic[Posture_keystore[i]])):
        biotemp,ode=getSAreport(XID,Posture_dic[Posture_keystore[i]][j]['start'],Posture_dic[Posture_keystore[i]][j]['end'])
        print(Posture_keystore[i]+" "+str(biotemp.ode))
        
    