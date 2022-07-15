# -*- coding: utf-8 -*-
"""
Created on Tue May  7 15:42:07 2019

@author: kylab
"""
import matplotlib.pyplot as plt
from datetime import datetime
from datetime import timedelta
import matplotlib.dates as mdates
import os
import pandas as pd
import math

def get_date(inputdate,dateFormat="%d-%m-%Y", addDays=0):

    anotherTime = datetime.strptime(inputdate,dateFormat) + timedelta(days=addDays)
    return anotherTime.strftime(dateFormat)

def getSleepScore(Sleepstage):
    if ('REM' in Sleepstage) or ('R' in Sleepstage):
        score=3
    elif ('S0' in Sleepstage) or ('Wake' in Sleepstage) or ('W' in Sleepstage): # wake
        score=4
    elif ('S1' in Sleepstage) or ('N1' in Sleepstage): 
        score=2
    elif ('S2' in Sleepstage) or ('N2' in Sleepstage):
        score=2
    elif ('S3' in Sleepstage) or ('S4' in Sleepstage) or ('N3' in Sleepstage): #sleep stage3
        score=1
    else:
        score=0
    return score

def getHypnogram(filename,isfigoutput=False):

    if '.txt' in filename:
        filename=filename.replace('.txt','')
    timeformat='%Y/%m/%d %p %I:%M:%S'
    f=open(filename+'.txt','r');

    rawtxt=f.read();
    f.close
    rawtxt=rawtxt.replace("上午","AM")
    rawtxt=rawtxt.replace("下午","PM")
    rawlist=rawtxt.split("\n")
    

    for i in range(len(rawlist)):
        if 'Recording Date' in rawlist[i]:
            recordingdate=rawlist[i].split('\t')[1]
        if 'Duration[s]' in rawlist[i]:
            break
    
    sleepstage=[]
    sleeptime=[]
    tempmeridiem=''
    isnextday=False
    idx=0
    dic={}
    for j in range(i+1,len(rawlist)):
        templist=rawlist[j].split("\t")
        if len(templist)<2:
            break
        elif len(templist)==5:
            idx=1
        
        if ('PM' in tempmeridiem):
            if 'AM' in templist[1+idx]:
                isnextday=True
        tempmeridiem=templist[1+idx]
    
        if isnextday:
            timeformat='%Y/%m/%d'
            recordingdate=get_date(recordingdate,timeformat,1)
            isnextday=False
        templist[1+idx]=recordingdate+' '+templist[1+idx]
        if ('AM' in templist[1+idx]) or ('PM' in templist[1+idx]):
            timeformat='%Y/%m/%d %p %I:%M:%S'
        else:
            timeformat='%Y/%m/%d %H:%M:%S'
        timetemp=datetime.strptime(templist[1+idx],timeformat)
        if len(sleepstage)==0:
            if not getSleepScore(templist[2+idx])==0:
                sleepstage.append(getSleepScore(templist[2+idx]))
                sleeptime.append(timetemp)
                dic[timetemp]={'score':getSleepScore(templist[2+idx])}
        elif sleeptime[len(sleepstage)-1]==timetemp:
            a=''
        else:
            if not getSleepScore(templist[2+idx])==0:
                sleepstage.append(getSleepScore(templist[2+idx]))
                sleeptime.append(timetemp)
                dic[timetemp]={'score':getSleepScore(templist[2+idx])}
#    dic={'time':sleeptime,'stage':sleepstage}
    
    if isfigoutput:
        fig_dpi=300
        line_width=0.5
        plt.plot(sleeptime,sleepstage,'k',linewidth=line_width)
        ax = plt.gca()
        ax.xaxis.set_major_locator(mdates.HourLocator(interval=4))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        ax.set_yticks([1,2,3,4,5], minor=False)
        plt.savefig(filename+'.png',bbox_inches='tight',dpi =fig_dpi)
        plt.close('all')
    return dic
    
#getHypnogram('1125-24hr')
#lista=os.listdir(os.getcwd())
#for i in range(5):
#    if '.txt' in lista[i]:
#        dica=getHypnogram(lista[i].replace('.txt',''))
timeformat='%Y-%m-%d %H:%M:%S'
path='/unprocess' #\\data
listcwd=os.listdir(os.getcwd()+path)

for k in range(len(listcwd)):#len(listcwd)
    listdata=os.listdir(os.getcwd()+path+'/'+listcwd[k])


    rawtxt=''
    hrtxt=''
    for i in range(len(listdata)):
        if ('-event' in listdata[i]) or ('-Events' in listdata[i]):
            dica=getHypnogram(os.getcwd()+path+'\\'+listcwd[k]+'\\'+listdata[i])
        if '(ACT)' in listdata[i]:
            f=open(os.getcwd()+path+'\\'+listcwd[k]+'\\'+listdata[i],'r');
            rawtxt=rawtxt+f.read()
            f.close
        if '(HRV)' in listdata[i]:
            f=open(os.getcwd()+path+'\\'+listcwd[k]+'\\'+listdata[i],'r')
            hrtxt=hrtxt+f.read()
            f.close


#    posture_xls = pd.ExcelFile(os.getcwd()+'\\vedio_sleep_posture\\'+listcwd[k]+'.xlsx')
#    posture_df= posture_xls.parse(posture_xls.sheet_names[0])
#    posture_df = [posture_df.set_index('Unnamed: 0')]
#    posture_dic=posture_df[0].to_dict()
    
    
    rawlist=rawtxt.split("\n")
    hrlist=hrtxt.split('\n')

    data_dic={}
    for  i in range(len(rawlist)):
        if not 'Date Time' in rawlist[i]:
            templist=rawlist[i].split(";")
            if not len(templist)<2:
                if float(templist[1])>0:
                    data_dic[datetime.strptime(templist[0],timeformat)]={'ACT':math.log(float(templist[1]))}#,'angle':float(templist[2]),'spin':float(templist[3])}
                else:
                    data_dic[datetime.strptime(templist[0],timeformat)]={'ACT':float(templist[1])}#,'angle':float(templist[2]),'spin':float(templist[3])}
    for  i in range(len(hrlist)):
        if not 'Date Time' in hrlist[i]:
            templist=hrlist[i].split(";")
            if not len(templist)<2:
                data_dic[datetime.strptime(templist[0],timeformat)].update({'HR':float(templist[1]),'var':float(templist[2])})

    data_dic_list=sorted(data_dic.items(), key=lambda d: d[0])
    
    data_dic={}
    for i in range(len(data_dic_list)):
        data_dic[data_dic_list[i][0]]=data_dic_list[i][1]

    data_keystore=list(data_dic.keys())
    dica_keystore=list(dica.keys())
#    data_keystore.sort()
#    dica_keystore.sort()
    j=0
    posture_loss=0
    for i in range(len(data_keystore)):
#        try:
#            data_dic[data_keystore[i]].update({'posture':posture_dic['posture'][data_keystore[i]]})
#        except:
#            posture_loss=posture_loss+1
        for j in range(j,len(dica_keystore)):
            if (data_keystore[i]<dica_keystore[j]):
                if (abs(data_keystore[i]-dica_keystore[j]).seconds<60):
                    data_dic[data_keystore[i]].update(dica[dica_keystore[j-1]])
                break
        
        
    writer = pd.ExcelWriter(listcwd[k]+'.xlsx')
    #writer = pd.ExcelWriter(Year+'_'+Month+'_'+userID+'_output.xlsx')
    pd.DataFrame(data_dic).T.to_excel(writer,'data')
    writer.save()
    print (str(k+1)+'/'+str(len(listcwd))+' complete '+datetime.now().strftime(timeformat)+' with posture point: '+str(i-posture_loss)+' filename: '+listcwd[k]+'.xlsx')