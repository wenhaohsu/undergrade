#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb  5 11:38:11 2020

@author: hao
"""
import pandas as pd
import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt
#def U_test(group1, group2):
#    mean1 = np.median(group1)
#    mean2 = np.median(group2)
#    std1 = np.std(group1)
#    std2 = np.std(group2)
#    nobs1 = len(group1)
#    nobs2 = len(group2)  
#    modified_std1 = np.sqrt(np.float32(nobs1)/
#                    np.float32(nobs1-1)) * std1
#    modified_std2 = np.sqrt(np.float32(nobs2)/
#                    np.float32(nobs2-1)) * std2
#    (statistic, pvalue) = stats.ttest_ind_from_stats( 
#               mean1=mean1, std1=modified_std1, nobs1=nobs1,   
#               mean2=mean2, std2=modified_std2, nobs2=nobs2 )
#    return statistic, pvalue
def get_post(data,post):
    right=[]
    left=[]
    supine=[]
    prone=[]
    for i in range(len(data)):
        if post[i] == 4:
            prone.append(data[i])
        elif post[i] == 3:
            left.append(data[i])
        elif post[i] == 2:
            supine.append(data[i])
        else:
            right.append(data[i])
    return right,supine,left,prone
def plot_error(x,y,error):
    
    plot2,cap1,bar1=plt.errorbar(
       x,y, yerr=error,lolims=True, capsize = 0, ls='None', color='k')
    cap1[0].set_marker('_')
    cap1[0].set_markersize(10)
#    return bar[0]
#    return caplines2[0]
#%%
def tick_post(x,y):
    plt.tick_params( axis='x',which='both',bottom=False, top=False, labelbottom=True)
    plt.yticks(fontsize=14)
    plt.xticks(x,y,fontname='arial',fontsize=16)
def label_diff(i,j,text,X,Y):
#    x = (X[i]+X[j])/2
    y = 1.1*max(Y[i], Y[j])
    dx = abs(X[i]-X[j])

#    props = {'connectionstyle':'bar','arrowstyle':'-',\
#                 'shrinkA':20,'shrinkB':20,'linewidth':2}
    plt.annotate(text, xy=(X[i],y+(0.2*y)), zorder=10)
#    plt.annotate('', xy=(X[i],y), xytext=(X[j],y), arrowprops=props)
#    label_diff(0,1,'p=0.0370',ind,menMeans)
#%%
base_hrv=pd.read_excel('/Users/hao/Desktop/posture hrv.xlsx',sheet_name='base hrv')
filt_hrv=pd.read_excel('/Users/hao/Desktop/posture hrv.xlsx',sheet_name='sleep hrv')
#posture_base=(base_hrv['Posture']
posture_filt=filt_hrv['Posture']
result=filt_hrv.groupby('Posture').mean()
std=filt_hrv.groupby('Posture').std()
xticks = ["Right","Supine","Left","Prone"]
std_zero=(0,0,0,0)
color_list=['white','silver','gray','k']
xarray=np.array([1,2,3,4])
#%%
fig1 = plt.figure(figsize=(25,20))
fig1.add_subplot(3,2,1)
result_RR=np.array(result['RR'])
std_RR=np.array(std['RR'])
plt.bar(xarray,result_RR,yerr=std_RR,capsize=5)
tick_post(xarray,xticks)
#plt.xticks(xarray,xticks,fontname='arial',fontsize=16)
#plt.tick_params( axis='x',which='both',bottom=False, top=False, labelbottom=True)
plt.ylabel("RR interval")
label_diff(xarray[0],xarray[1],'*',result_RR,std_RR)
fig1.add_subplot(3,2,2)
result_SD=np.array(result['SD'])
std_SD=np.array(std['SD'])
#plt.bar(xarray,result_SD,capsize=5,color=['black', 'red', 'green', 'blue'])
plt.bar(xarray,result_SD,capsize=5,color=color_list,edgecolor='k')
plot_error(xarray,result_SD,std_SD)
#plt.xlabel('Posture')
plt.xticks(xarray,xticks)
plt.ylabel("Standard deviation")
fig1.add_subplot(3,2,3)
result_TP=np.array(result['TP'])
std_TP=np.array(std['TP'])
plt.bar(xarray,result_TP,yerr=std_TP,capsize=5)
#plt.xlabel('Posture')
plt.xticks(xarray,xticks)
plt.ylabel("Total power")
fig1.add_subplot(3,2,4)
result_HF=np.array(result['HF'])
std_HF=np.array(std['HF'])
plt.bar(xarray,result_HF,yerr=std_HF,capsize=5)
#plt.xlabel('Posture')
plt.xticks(xarray,xticks)
plt.ylabel("High frequency")
fig1.add_subplot(3,2,5)
result_LF=np.array(result['LF'])
std_LF=np.array(std['LF'])
plt.bar(xarray,result_LF,yerr=std_HF,capsize=5)
#plt.errorbar(xarray,result_LF, yerr=std_LF, xuplims=True, capsize = 0, ls='None', color='k')
plt.xlabel('Posture')
plt.xticks(xarray,xticks)
plt.ylabel("Low frequency")
fig1.add_subplot(3,2,6)
result_VL=np.array(result['VL'])
std_VL=np.array(std['VL'])
plt.bar(xarray,result_VL,yerr=std_VL,capsize=5)
plt.xlabel('Posture')
plt.xticks(xarray,xticks)
plt.ylabel("Very low\nfrequency")
#%%
fig2 = plt.figure(figsize=(25,20))
fig2.add_subplot(3,2,1)
result_logTP=np.array(result['Ln(TP)'])
std_logTP=np.array(std['Ln(TP)'])
plt.bar(xarray,result_logTP,yerr=std_logTP,capsize=5)
#plt.xlabel('Posture')
plt.xticks(xarray,xticks)
plt.ylabel("Nature\nlog TP")
fig2.add_subplot(3,2,2)
result_logHF=np.array(result['Ln(HF)'])
std_logHF=np.array(std['Ln(HF)'])
plt.bar(xarray,result_logHF,yerr=std_logHF,capsize=5)
#plt.xlabel('Posture')
plt.xticks(xarray,xticks)
plt.ylabel("Nature\nlog HF")
fig2.add_subplot(3,2,3)
result_logLF=np.array(result['Ln(LF)'])
std_logLF=np.array(std['Ln(LF)'])
plt.bar(xarray,result_logLF,yerr=std_logLF,capsize=5)
#plt.xlabel('Posture')
plt.xticks(xarray,xticks)
plt.ylabel("Nature\nlog LF")
fig2.add_subplot(3,2,4)
result_logVL=np.array(result['Ln(VL)'])
std_logVL=np.array(std['Ln(VL)'])
plt.bar(xarray,result_logVL,yerr=std_logVL,capsize=5)
#plt.xlabel('Posture')
plt.xticks(xarray,xticks)
plt.ylabel("Nature\nlog VL")
fig2.add_subplot(3,2,5)
result_LH=np.array(result['LF/HF'])
std_LH=np.array(std['LF/HF'])
plt.bar(xarray,result_LH,yerr=std_LH,capsize=5)
plt.xlabel('Posture')
plt.xticks(xarray,xticks)
plt.ylabel("Low high\nratio")
#%%
fig2.add_subplot(3,2,6)
result_LFprc=np.array(result['LF%'])
std_LFprc=np.array(std['LF%'])
plt.bar(xarray,result_LFprc,yerr=std_LFprc,capsize=5)
plt.xlabel('Posture')
plt.xticks(xarray,xticks)
plt.ylabel("LF percentage")
#%%
right,supine,left,prone=get_post(filt_hrv['LF%'],posture_filt)
result_RS,pvalue_RS=stats.mannwhitneyu(right,supine)
result_RL,pvalue_RL=stats.mannwhitneyu(right,left)
result_RP,pvalue_RP=stats.mannwhitneyu(right,prone)
result_SL,pvalue_SL=stats.mannwhitneyu(supine,left)
result_SP,pvalue_SP=stats.mannwhitneyu(supine,prone)
result_LP,pvalue_LP=stats.mannwhitneyu(left,prone)
print(pvalue_RS)
print(pvalue_RL)
print(pvalue_RP)
print(pvalue_SL)
print(pvalue_SP)
print(pvalue_LP)