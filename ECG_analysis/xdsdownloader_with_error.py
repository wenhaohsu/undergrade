# -*- coding: utf-8 -*-
"""
Created on Fri Mar  8 10:50:30 2019

@author: kylab
"""

import requests
import math
import pandas as pd



serverdns="xds.ym.edu.tw"
print("Your will download data from sever:" + serverdns)
XID=input("Please enter Xenon ID: ").upper()
date=input("Please enter date (format: yyyymmdd eq. 20190912): ")

urlstart="http://"+serverdns+"/"+XID+"/"+XID+"_"+date+".txt"
print("URL: "+ urlstart)


r = requests.get(urlstart)
rawtxt=r.text

if ("404 Not Found" in rawtxt):
    print ("No data")
else:
    format = '%Y-%m-%d %H:%M:%S'
    rawtxt=rawtxt.replace("/","-")
    rawlist=rawtxt.split("\r\n")
    PID=XID[4:8]
    data_dic={}
    data2_dic={}
    temp2list=[]
    filetype=''
    for  i in range(len(rawlist)):
        templist=rawlist[i].split(",")
        if PID=="0007" :
            #print ("XA")
            filetype='ACT'
            if templist[0]==";PA":
                templist.remove(";PA")
                datetime=templist[0].split(" ")
                data_dic[datetime[1]]={'ACT':float(templist[1]),'angle':float(templist[2]),'spin':float(templist[3])}
        elif PID=="0040":
            #print ("O2")        
            filetype='SPO2'
            if templist[0]==";O2" and int(templist[2])>0 and int(templist[2])<100:
                templist.remove(";O2")
                datetime=templist[0].split(" ")
                data_dic[datetime[1]]={'O2':int(templist[1]),'HR':int(templist[2]),'ACT':int(templist[3])/2}
        elif PID=="005A" or PID=="005B" or PID=="005C":
           # print ("Patch")
            filetype='HRV'
            
            if templist[0]==";PA":
                templist.remove(";PA")
                datetime=templist[0].split(" ")
                if len(templist)==6:
                    data_dic[datetime[1]]={'ACT':float(templist[1]),'angle':float(templist[2]),
                                       'spin':float(templist[3]),'HR':float(templist[4]),'VAR':int(templist[5])}
                elif (len(templist)==10) and ('XYZ' in rawlist[i]):
                    data_dic[datetime[1]]={'ACT':float(templist[1]),'angle':float(templist[2]),
                                        'spin':float(templist[3]),'X':float(templist[5]),'Y':float(templist[6]),
                                        'Z':float(templist[7]),'HR':float(templist[8]),'VAR':int(templist[9])}
                else:
                    data_dic[datetime[1]]={'ACT':float(templist[1]),'angle':float(templist[2]),
                                       'spin':float(templist[3]),'HR':float('nan'),'VAR':float('nan')}
            elif templist[0]==";HV":
                templist.remove(";HV")
                datetime=templist[0].split(" ")
                templistlog=[]
                for j in range(4):
                    if int(templist[13+j]) >0:
                        templistlog.append(math.log(int(templist[13+j])))
                    else:
                        templistlog.append(0)
                
                data2_dic[datetime[1]]={'RR':int(templist[11]),'SD':float(templist[12]),'TP':int(templist[13]),
                                        'VL':int(templist[14]),'LF':int(templist[15]),'HF':int(templist[16]),
                                        'Ln(HF)':templistlog[3],'Ln(LF)':templistlog[2],
                                        'Ln(VL)':templistlog[1],'Ln(TP)':templistlog[0],
                                        'LF/HF':int(templist[15])/int(templist[16]),'LF%':int(templist[15])/(int(templist[13])-int(templist[14]))*100}
        
        
        
    try:
        writer = pd.ExcelWriter(XID+'_'+date+'('+filetype+').xlsx')
#writer = pd.ExcelWriter(Year+'_'+Month+'_'+userID+'_output.xlsx')
        pd.DataFrame(data_dic).T.to_excel(writer,'data')
        if bool(data2_dic):
            pd.DataFrame(data2_dic).T.to_excel(writer,'data2')
        writer.save()

        print("Done")
        print("Your file name is "+ XID+'_'+date+'('+filetype+').xlsx')
        
    except PermissionError:
        print("You don't have the permission to write the file, check whether your file is already open.")

#呼吸鬥性心律不整是什麼
#找人測試，這支程式還有使用上的哪些問題想要處理的？
#另存出只有睡眠時間的資料，在另一個一個sheet做出睡眠統計，並對每小時的HR做出mean+-STD
