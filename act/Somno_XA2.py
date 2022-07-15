# -*- coding: utf-8 -*-
"""
Created on Tue Sep 25 16:50:53 2018

@author: Albert
"""
from tkinter import filedialog  
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats as st

def select_file():
  fname = filedialog.askopenfilename(title = u'選擇文件', initialdir = "C:/Users/User/Desktop",filetypes = [("all files", "*.xlsx"), ("allfiles", "*")])
  return fname
def parseinsecond(hh,mm,ss):
  return (hh*3600+mm*60+ss)
  



fname=select_file()
name_somno=['Day','Duration','TST','WD','#Wake','SE','SL','WASO','TA','From_To','NO']
name_xa2=['Day','Duration','TST','WD','#Wake','SE','SL','WASO','TA','From_To','NO','DeviceID']
xlsx = pd.ExcelFile(fname)
for sheet in xlsx.sheet_names:
  
  if sheet=='XA2':
    print(sheet)
    XA2_data=xlsx.parse(sheetname=sheet,skiprows=range(0, 2),keep_default_na=False,names=name_xa2)
  if sheet=='Somno':
    print(sheet)
    Somno_data=xlsx.parse(sheetname=sheet,skiprows=range(0, 2),keep_default_na=False,names=name_somno)

patient_filter=XA2_data['NO']!=''
patient_start_index=XA2_data['NO'][patient_filter].index

#lm = LinearRegression()
#lm.fit(np.reshape(XA2_data['SE'], (len(XA2_data['SE']), 1)), np.reshape(Somno_data['SE'], (len(Somno_data['SE']), 1)))
#model = lm.fit(XA2_data['SE'],Somno_data['SE'])
#plt.plot(model)

for i in range(len(XA2_data)):
  h,m,s=map(int,map(float,(str(XA2_data['WASO'][i]).split(":"))))
  XA2_data['WASO'][i]=int(parseinsecond(h,m,s))
  h,m,s=map(int,map(float,(str(Somno_data['WASO'][i]).split(":"))))
  Somno_data['WASO'][i]=int(parseinsecond(h,m,s))
  
  h,m,s=map(int,map(float,(str(XA2_data['SL'][i]).split(":"))))
  XA2_data['SL'][i]=int(parseinsecond(h,m,s))
  h,m,s=map(int,map(float,(str(Somno_data['SL'][i]).split(":"))))
  Somno_data['SL'][i]=int(parseinsecond(h,m,s))
  
  h,m,s=map(int,map(float,(str(XA2_data['TST'][i]).split(":"))))
  XA2_data['TST'][i]=int(parseinsecond(h,m,s))
  h,m,s=map(int,map(float,(str(Somno_data['TST'][i]).split(":"))))
  Somno_data['TST'][i]=int(parseinsecond(h,m,s))
  
  h,m,s=map(int,map(float,(str(XA2_data['WD'][i]).split(":"))))
  XA2_data['WD'][i]=int(parseinsecond(h,m,s))
  h,m,s=map(int,map(float,(str(Somno_data['WD'][i]).split(":"))))
  Somno_data['WD'][i]=int(parseinsecond(h,m,s))
  
  
Somno_data['WASO']=Somno_data['WASO'].convert_objects(convert_numeric=True)
XA2_data['WASO']=XA2_data['WASO'].convert_objects(convert_numeric=True)
Somno_data['SL']=Somno_data['SL'].convert_objects(convert_numeric=True)
XA2_data['SL']=XA2_data['SL'].convert_objects(convert_numeric=True)
Somno_data['TST']=Somno_data['TST'].convert_objects(convert_numeric=True)
XA2_data['TST']=XA2_data['TST'].convert_objects(convert_numeric=True)
Somno_data['WD']=Somno_data['WD'].convert_objects(convert_numeric=True)
XA2_data['WD']=XA2_data['WD'].convert_objects(convert_numeric=True)

Somno_data['mean']=Somno_data['TA']/Somno_data['TST']
XA2_data['mean']=XA2_data['TA']/XA2_data['TST']



for i in range(len(patient_start_index)):

  fig=plt.figure(figsize=(15,10))
  fig.subplots_adjust( hspace=0.3,wspace=0.20,right=0.98,left=0.06,top=0.96,bottom=0.11)
  patient=XA2_data['NO'][patient_start_index[i]]
  Device=XA2_data['DeviceID'][patient_start_index[i]]
  fig.canvas.set_window_title(patient)
  if i!=len(patient_start_index)-1:
    start=patient_start_index[i]
    end=patient_start_index[i+1]
  else:
    start=patient_start_index[i]
    end=len(XA2_data)


  fig.add_subplot(2,2,1)
  slope, intercept, r_value, p_value, std_err=st.linregress(Somno_data['SE'][start:end],XA2_data['SE'][start:end])
  print(patient+" "+Device + " r-squared:", r_value**2)
  plt.plot(Somno_data['SE'][start:end], XA2_data['SE'][start:end], 'o', label='original data')
  plt.plot(Somno_data['SE'][start:end], intercept + slope*Somno_data['SE'][start:end], 'r', label='fitted line'+r'$\ R^2$'+": "+"{0:2.3f}".format(r_value**2))
  plt.title(patient+' SE')
  plt.xlabel('Somno ')
  plt.ylabel('XA2 '+Device)
  plt.legend()
  fig.add_subplot(2,2,2)
  slope, intercept, r_value, p_value, std_err=st.linregress(Somno_data['TA'][start:end],XA2_data['TA'][start:end])
  print(patient+" "+Device + " r-squared:", r_value**2)
  plt.plot(Somno_data['TA'][start:end], XA2_data['TA'][start:end], 'o', label='original data')
  plt.plot(Somno_data['TA'][start:end], intercept + slope*Somno_data['TA'][start:end], 'r', label='fitted line'+r'$\ R^2$'+": "+"{0:2.3f}".format(r_value**2))
  plt.title(patient+' TA')
  plt.xlabel('Somno ')
  plt.ylabel('XA2 '+Device)
  plt.legend()
  
  fig.add_subplot(2,2,3)
  slope, intercept, r_value, p_value, std_err=st.linregress(Somno_data['WASO'][start:end],XA2_data['WASO'][start:end])
  print(patient+" "+Device + " r-squared:", r_value**2)
  plt.plot(Somno_data['WASO'][start:end], XA2_data['WASO'][start:end], 'o', label='original data')
  plt.plot(Somno_data['WASO'][start:end], intercept + slope*Somno_data['WASO'][start:end], 'r', label='fitted line'+r'$\ R^2$'+": "+"{0:2.3f}".format(r_value**2))
  plt.title(patient+' WASO')
  plt.xlabel('Somno ')
  plt.ylabel('XA2 '+Device)
  plt.legend()

  fig.add_subplot(2,2,4)
  slope, intercept, r_value, p_value, std_err=st.linregress(Somno_data['SL'][start:end],XA2_data['SL'][start:end])
  print(patient+" "+Device + " r-squared:", r_value**2)
  plt.plot(Somno_data['SL'][start:end], XA2_data['SL'][start:end], 'o', label='original data')
  plt.plot(Somno_data['SL'][start:end], intercept + slope*Somno_data['SL'][start:end], 'r', label='fitted line'+r'$\ R^2$'+": "+"{0:2.3f}".format(r_value**2))
  plt.title(patient+' SL')
  plt.xlabel('Somno ')
  plt.ylabel('XA2 '+Device)
  plt.legend()
  
  fig=plt.figure(figsize=(15,10))
  fig.subplots_adjust( hspace=0.3,wspace=0.20,right=0.96,left=0.07,top=0.93,bottom=0.11)
  fig.canvas.set_window_title(patient+'_2')
  fig.add_subplot(1,2,1)
  slope, intercept, r_value, p_value, std_err=st.linregress(Somno_data['WD'][start:end],XA2_data['WD'][start:end])
  plt.plot(Somno_data['WD'][start:end], XA2_data['WD'][start:end], 'o', label='original data')
  plt.plot(Somno_data['WD'][start:end], intercept + slope*Somno_data['WD'][start:end], 'r', label='fitted line'+r'$\ R^2$'+": "+"{0:2.3f}".format(r_value**2))
  plt.title(patient+' WD')
  plt.xlabel('Somno ')
  plt.ylabel('XA2 '+Device)
  plt.legend()
  
  fig.add_subplot(1,2,2)
  slope, intercept, r_value, p_value, std_err=st.linregress(Somno_data['TST'][start:end],XA2_data['TST'][start:end])
  plt.plot(Somno_data['TST'][start:end], XA2_data['TST'][start:end], 'o', label='original data')
  plt.plot(Somno_data['TST'][start:end], intercept + slope*Somno_data['TST'][start:end], 'r', label='fitted line'+r'$\ R^2$'+": "+"{0:2.3f}".format(r_value**2))
  plt.title(patient+' TST')
  plt.xlabel('Somno ')
  plt.ylabel('XA2 '+Device)
  plt.legend()


fig=plt.figure(figsize=(15,10))
#fig.subplots_adjust( hspace=0.3,wspace=0.20,right=0.98,left=0.06,top=0.96,bottom=0.11)
fig.subplots_adjust( hspace=0.3,wspace=0.20,right=0.96,left=0.07,top=0.93,bottom=0.11)
fig.canvas.set_window_title("All")

#print("All r-squared:", r_value**2)
fig.add_subplot(1,2,1)
slope, intercept, r_value, p_value, std_err=st.linregress(Somno_data['SE'],XA2_data['SE'])
print("p_value: ", p_value)
#if p_value<0.001 and p_value>0.0001:
#  p_value=0.001
#  p_label="{0:2.3f}".format(p_value)
if p_value<0.001:
  p_value=0.001
  p_label="{0:2.3f}".format(p_value)
else:
  p_label="{0:2.3f}".format(p_value)

plt.plot(Somno_data['SE'], XA2_data['SE'], 'o', label='original data')
plt.plot(Somno_data['SE'], intercept + slope*Somno_data['SE'], 'r', label='fitted line'+r'$\ R^2$'+": "+"{0:2.3f}".format(r_value**2)+"\np < "+p_label)

plt.title('SE (n='+str(len(XA2_data))+')')
#plt.xlim(50,95)
#plt.ylim(50,95)
plt.xlabel('Somno ')
plt.ylabel('XA2 (%)')
plt.legend()
fig.add_subplot(1,2,2)
slope, intercept, r_value, p_value, std_err=st.linregress(Somno_data['TA'],XA2_data['TA'])
print("p_value: ", p_value)
#if p_value<0.001 and p_value>0.0001:
#  p_value=0.001
#  p_label="{0:2.3f}".format(p_value)
if p_value<0.001:
  p_value=0.001
  p_label="{0:2.3f}".format(p_value)
else:
  p_label="{0:2.3f}".format(p_value)
plt.plot(Somno_data['TA'], XA2_data['TA'], 'o', label='original data')
plt.plot(Somno_data['TA'], intercept + slope*Somno_data['TA'], 'r', label='fitted line'+r'$\ R^2$'+": "+"{0:2.3f}".format(r_value**2)+"\np < "+p_label)
plt.title('TA (n='+str(len(XA2_data))+')')
#plt.xlim(0,45000)
#plt.ylim(0,45000)
plt.xlabel('Somno ')
plt.ylabel('XA2 (mG)')
plt.legend()
fig=plt.figure(figsize=(15,10))
fig.subplots_adjust( hspace=0.3,wspace=0.20,right=0.96,left=0.07,top=0.93,bottom=0.11)
fig.add_subplot(1,2,1)
slope, intercept, r_value, p_value, std_err=st.linregress(Somno_data['WASO'],XA2_data['WASO'])
print("p_value: ", p_value)
#if p_value<0.001 and p_value>0.0001:
#  p_value=0.001
#  p_label="{0:2.3f}".format(p_value)
if p_value<0.001:
  p_value=0.001
  p_label="{0:2.3f}".format(p_value)
else:
  p_label="{0:2.3f}".format(p_value)
plt.plot(Somno_data['WASO'], XA2_data['WASO'], 'o', label='original data')
plt.plot(Somno_data['WASO'], intercept + slope*Somno_data['WASO'], 'r', label='fitted line'+r'$\ R^2$'+": "+"{0:2.3f}".format(r_value**2)+"\np < "+p_label)
plt.title('WASO (n='+str(len(XA2_data))+')')
plt.xlabel('Somno ')
plt.ylabel('XA2 (Sec)')
#plt.xlim(0,15000)
#plt.ylim(0,15000)
plt.legend()
fig.add_subplot(1,2,2)
slope, intercept, r_value, p_value, std_err=st.linregress(Somno_data['SL'],XA2_data['SL'])
print("p_value: ", p_value)
#if p_value<0.001 and p_value>0.0001:
#  p_value=0.001
#  p_label="{0:2.3f}".format(p_value)
if p_value<0.001:
  p_value=0.001
  p_label="{0:2.3f}".format(p_value)
else:
  p_label="{0:2.3f}".format(p_value)
plt.plot(Somno_data['SL'], XA2_data['SL'], 'o', label='original data')
plt.plot(Somno_data['SL'], intercept + slope*Somno_data['SL'], 'r', label='fitted line'+r'$\ R^2$'+": "+"{0:2.3f}".format(r_value**2)+"\np < "+p_label)
plt.title('SL (n='+str(len(XA2_data))+')')
#plt.xlim(-200,3500)
#plt.ylim(-200,3500)
plt.xlabel('Somno ')
plt.ylabel('XA2 (Sec)')
plt.legend()

fig=plt.figure(figsize=(15,10))
fig.subplots_adjust( hspace=0.3,wspace=0.20,right=0.96,left=0.07,top=0.93,bottom=0.11)
fig.canvas.set_window_title('All_2')
fig.add_subplot(1,2,1)
slope, intercept, r_value, p_value, std_err=st.linregress(Somno_data['WD'],XA2_data['WD'])
print("p_value: ", p_value)
#if p_value<0.001 and p_value>0.0001:
#  p_value=0.001
#  p_label="{0:2.3f}".format(p_value)
if p_value<0.001:
  p_value=0.001
  p_label="{0:2.3f}".format(p_value)
else:
  p_label="{0:2.3f}".format(p_value)
plt.plot(Somno_data['WD'], XA2_data['WD'], 'o', label='original data')
plt.plot(Somno_data['WD'], intercept + slope*Somno_data['WD'], 'r', label='fitted line'+r'$\ R^2$'+": "+"{0:2.3f}".format(r_value**2)+"\np < "+p_label)
plt.title('WD (n='+str(len(XA2_data))+')')
#plt.xlim(2000,15000)
#plt.ylim(2000,15000)
plt.xlabel('Somno ')
plt.ylabel('XA2 (Sec)')
plt.legend()

fig.add_subplot(1,2,2)
slope, intercept, r_value, p_value, std_err=st.linregress(Somno_data['TST'],XA2_data['TST'])
print("p_value: ", p_value)
#if p_value<0.001 and p_value>0.0001:
#  p_value=0.001
#  p_label="{0:2.3f}".format(p_value)
if p_value<0.001:
  p_value=0.001
  p_label="{0:2.3f}".format(p_value)
else:
  p_label="{0:2.3f}".format(p_value)
plt.plot(Somno_data['TST'], XA2_data['TST'], 'o', label='original data')
plt.plot(Somno_data['TST'], intercept + slope*Somno_data['TST'], 'r', label='fitted line'+r'$\ R^2$'+": "+"{0:2.3f}".format(r_value**2)+"\np < "+p_label)
plt.title('TST (n='+str(len(XA2_data))+')')
#plt.xlim(15000,33000)
#plt.ylim(15000,33000)
plt.xlabel('Somno ')
plt.ylabel('XA2 (Sec)')
plt.legend()

fig=plt.figure(figsize=(15,10))

fig.canvas.set_window_title('Mean Activity')

slope, intercept, r_value, p_value, std_err=st.linregress(Somno_data['mean'],XA2_data['mean'])
print("p_value: ", p_value)
#if p_value<0.001 and p_value>0.0001:
#  p_value=0.001
#  p_label="{0:2.4f}".format(p_value)
if p_value<0.001:
  p_value=0.001
  p_label="{0:2.3f}".format(p_value)
else:
  p_label="{0:2.3f}".format(p_value)
plt.plot(Somno_data['mean'], XA2_data['mean'], 'o', label='original data')
plt.plot(Somno_data['mean'], intercept + slope*Somno_data['mean'], 'r', label='fitted line'+r'$\ R^2$'+": "+"{0:2.3f}".format(r_value**2)+"\np < "+p_label)
plt.title('Mean Activity in Sleep (n='+str(len(XA2_data))+')')
plt.xlabel('Somno ')
plt.ylabel('XA2 ')
plt.legend()

plt.show()

#plt.plot(temperatures, lm.predict(np.reshape(temperatures, (len(temperatures), 1))), color='blue', linewidth=0.5)