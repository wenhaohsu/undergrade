# -*- coding: utf-8 -*-
"""
Created on Wed Aug  5 16:29:29 2020

@author: kylab
"""

import pandas as pd
import numpy as np
from datetime import datetime


class SA_report():
    def __init__(self):
        self.Total_Record_time=0
        self.Record_start=''
        self.Record_end=''
        self.baseline=0
        self.meanSPO2=0
        self.LowestSPO2=0
        self.ratio_under90=0
        self.ODE = 0
        self.ODE4 = 0
        self.ODE_new = 0
        self.AHI = 0
        self.AHI_new =0
        self.osa_level=''
        
    def get_mode(self,arr):
        mode = []
        arr_appear = dict((a, arr.count(a)) for a in arr)
        if max(arr_appear.values()) == 1:  # 如果最大的出現為1
            return  # 則沒有眾數
        else:
            for k, v in arr_appear.items():  # 否則，出現次數最大的數字，就是眾數
                if v == max(arr_appear.values()):
                    mode.append(k)
        return mode

    def f_getSAReport(self,**kwargs):
        Threshold=3
        Activity_Threshold=2
        Duration_Time=75
        
        
        if '.xls' in kwargs['filename']:
            xls = pd.ExcelFile(kwargs['filename'])
            sheetname='SPO2'#input("Please enter sheetname: ")
            sheetX = xls.parse(sheetname)
            sheetkeys=sheetX.keys()
            sheetX=sheetX.set_index(sheetkeys[0])
            data_df=sheetX
            
        elif '.txt' in kwargs['filename']:
            with open(kwargs['filename'], 'r') as f:
                text = []
                data_dic={}
                for line in f:
                    text.append(line)
                for  i in range(len(text)):
                    text[i]=text[i].replace("\n","")
                    templist=text[i].split(",")
                    try:
                        timeformat='%Y-%m-%d %H:%M:%S'
                        datetime.strptime(templist[0],timeformat)
                        data_dic[templist[0]]={'O2':int(templist[1]),'HR':int(templist[2]),'ACT':float(templist[3])}
                    except:
                        continue
                data_df=pd.DataFrame.from_dict(data_dic).T
        elif kwargs['rawtxt']!='':
            rawtxt=kwargs['rawtxt'].replace("/","-")
            rawlist=rawtxt.split("\r\n")
            for  i in range(len(rawlist)):
                templist=rawlist[i].split(",")
                if templist[0]==";O2" and int(templist[2])>0 and int(templist[2])<100:
                    templist.remove(";O2")
                    data_dic[templist[0]]={'O2':int(templist[1]),'HR':int(templist[2]),'ACT':int(templist[3])/2}
        
            data_df=pd.DataFrame.from_dict(data_dic).T
        
        
        listdatakey=data_df.index
        TimeInBed = len(listdatakey)
        
        SPO2_denoise=[]
        SPO2_under90=[]
        SPO2_origin_loc=[]
        for i in range(TimeInBed):
            if data_df['O2'][listdatakey[i]]==0 or data_df['O2'][listdatakey[i]]==-1 or data_df['O2'][listdatakey[i]]>100 or data_df['O2'][listdatakey[i]]<70 or data_df['ACT'][listdatakey[i]]>Activity_Threshold:
                TimeInBed-=1
                continue
            SPO2_denoise.append(data_df['O2'][listdatakey[i]])
            SPO2_origin_loc.append(i)
            if data_df['O2'][listdatakey[i]]<90:
                SPO2_under90.append(data_df['O2'][listdatakey[i]])
        
        diffSPO2=np.diff(np.array(SPO2_denoise))#ISPO2 in Charlie thesis
        NPSPO2=[]
        RealIdx=[]
        
        for i in range(len(diffSPO2)):
            if diffSPO2[i]!=0:
                NPSPO2.append(SPO2_denoise[i+1])
                RealIdx.append(i+1)
                
        NPNPSPO2=np.diff(np.array(NPSPO2))
        IndMin=[]
        IndMax=[]
        SPO2_mark_location =[np.nan] * TimeInBed
        
#        for i in range(len(NPNPSPO2)-1):
#            if NPNPSPO2[i+1]*NPNPSPO2[i]>0:
#                IndMin.append(i+1)   #trough 
#            else:
#                IndMax.append(i+1)   #peak
        
        for i in range(len(NPNPSPO2)-1):
            if np.sign(NPNPSPO2[i+1]) - np.sign(NPNPSPO2[i])>0:
                IndMin.append(i+1)   #trough 
            elif np.sign(NPNPSPO2[i+1]) - np.sign(NPNPSPO2[i])<0:
                IndMax.append(i+1)   #peak
                
        peak_values=[]
        peak_values_idx=[]
        trough_values=[]
        trough_values_idx=[]
        
        for i in range(len(IndMax)):
            peak_values.append(NPSPO2[IndMax[i]])
            peak_values_idx.append(RealIdx[IndMax[i]])
            SPO2_mark_location[RealIdx[IndMax[i]]] = 'peak,' +str(SPO2_origin_loc[RealIdx[IndMax[i]]]) + ',' + str(NPSPO2[IndMax[i]])
            
        for i in range(len(IndMin)):
            trough_values.append(NPSPO2[IndMin[i]])
            trough_values_idx.append(RealIdx[IndMin[i]])
            SPO2_mark_location[RealIdx[IndMin[i]]] = 'trough,' + str(SPO2_origin_loc[RealIdx[IndMin[i]]]) + ',' + str(NPSPO2[IndMin[i]])
            
            
        peak_count=len(peak_values)
        trough_count=len(trough_values)
        count_diff=abs(peak_count-trough_count)
        
        SPO2_mark_location = [x for x in SPO2_mark_location if str(x) != 'nan']
        
        if NPNPSPO2[0]>0:
            if count_diff ==1:
                peak_values.pop()
                peak_values_idx.pop()
                SPO2_mark_location.pop();
        else:
            if count_diff == 1:
                trough_values.pop(0)
                trough_values_idx.pop(0)
                SPO2_mark_location.pop(0)
            else:
                peak_values.pop()
                peak_values_idx.pop()
                trough_values.pop(0)
                trough_values_idx.pop(0)
                SPO2_mark_location.pop();
                SPO2_mark_location.pop(0);
                
        amp=[]
        O2_delta=[]
        O2_delta_4=[]
        
        for i in range(len(peak_values)):
            if abs(peak_values_idx[i]-trough_values_idx[i]) <=Duration_Time:
                amp.append(peak_values[i]-trough_values[i])
                if peak_values[i]-trough_values[i]>=Threshold:
                    O2_delta.append(peak_values[i]-trough_values[i])
                if peak_values[i]-trough_values[i]>=4:
                    O2_delta_4.append(peak_values[i]-trough_values[i])
                    
                    
        
        
        self.ODE = len(O2_delta);
        self.ODE4 = len(O2_delta_4);
        self.ODE_new = (self.ODE+self.ODE4)/2
        
        self.AHI = round(self.ODE/TimeInBed*3600,2)
        self.AHI_new = round(self.ODE_new/TimeInBed*3600,2)
        

        
        if self.AHI_new>=30:
            self.osa_level='Severe'
        elif self.AHI_new>=15 and self.AHI_new<30:
            self.osa_level='Moderate'
        elif self.AHI_new>=5 and self.AHI_new<=15:
            self.osa_level='Mild'
        elif self.AHI_new<5:
            self.osa_level='Normal'
            
        self.Total_Record_time=round(TimeInBed/3600,2)
        self.Record_start=listdatakey[0]
        self.Record_end=listdatakey[-1]
        self.baseline=self.get_mode(SPO2_denoise)
        self.meanSPO2=round(np.mean(SPO2_denoise),2)
        self.LowestSPO2=min(SPO2_denoise)
        self.ratio_under90=round(len(SPO2_under90)/len(SPO2_denoise)*100,2)