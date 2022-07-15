# -*- coding: utf-8 -*-
"""
Created on Mon Apr 29 11:21:55 2019

@author: Albert
"""
from matplotlib.font_manager import FontProperties
from tkinter import filedialog  
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import datetime
import xlsxwriter
from scipy import stats as st
from pylab import *
import os

def select_file():
  fname = filedialog.askopenfilename(title = u'選擇文件', initialdir = "C:/Users/User/Desktop",filetypes = [("all files", "*.xlsx"), ("allfiles", "*")])
  return fname


def rounds(x,n):
  z=''
  for i in range(n):
    z=z+'0'
  n=int('1'+z)
  a=round(x*n)/n
  return a 


def read_scale(fname,pat,patience_name):
    sheet_name=[]
    name=['Item','FD','Gd','TD']
    xlsx = pd.ExcelFile(fname)
    MoCA_dif=pd.DataFrame()
    MoCA_item=pd.DataFrame()
    pname=pd.DataFrame({'Name':[patience_name]})
    pname.index+=1
    for sheet in xlsx.sheet_names:
      exec('{} = xlsx.parse(sheetname=sheet,skiprows=0,keep_default_na=False,names=name)'.format(sheet))
      sheet_name.append(sheet)
#    exec('MoCA_dif["Name"] = pd.Series(["{}"])'.format(patience_name))
    exec('MoCA_item["Item"] = {}["Item"]'.format(sheet_name[0]))
    exec('MoCA_item["FD"] = {}["FD"]'.format(sheet_name[0]))
    exec('MoCA_dif["Gd"] = {}["Gd"]-{}["Gd"]'.format(sheet_name[1],sheet_name[0]))

#    exec('name=pd.DataFrame({"Name":"{}"})'.format(patience_name))
    pname=pd.concat([pname,MoCA_dif],axis=1)

    return MoCA_item,pname

def read_bp(fname_BP,pat,patience_name):
    name_BP=['mor_sys','aft_sys','all_sys','mor_dia','aft_dia','all_dia','mor_hr','aft_hr','all_hr','sys_dif','dia_dif','hr_dif','mor_pre_dif','aft_pre_dif','all_pre_dif']
    xlsx = pd.ExcelFile(fname_BP)
#    BP_data=pd.DataFrame()
    
    
    for sheet in xlsx.sheet_names:
      BP_data= xlsx.parse(sheetname=sheet,skiprows=0,keep_default_na=False,names=name_BP)
    BP_data['Name']=patience_name

#    BP_data=BP_data[cols]
    return BP_data

def plot_subplot(row,cloumn,xtitle,ytitle,x,y,full_grade,item):
  axes[row][cloumn].plot(x,y,'b.',markersize=2)
#  axes[row][cloumn].set_title(patience_scale["Item"][item] +' vs '+ytitle ,fontproperties=font)
  axes[row][cloumn].set_xlim([-(full_grade+0.5),full_grade+0.5])
  axes[row][cloumn].set_ylim([min(y)+min(y)*0.2,max(y)+max(y)*0.2])
  slope, intercept, r_value, p_value, std_err=st.linregress(x,y.T)
#  axes[row][cloumn].grid('on', linestyle='--')
  r=rounds(r_value,2)
  posy=(max(y)-min(y))/2+min(y) #文字位置 position y
  posx=-full_grade-full_grade/4 #文字位置 position x
  if p_value<0.05:
    p=rounds(p_value,3)
    sub_text='r='+str(r)+'\n'+'p='+str(p)
    axes[row][cloumn].text(posx, posy,sub_text, ha='left',color='red',fontsize=5)

    for axis in ['top','bottom','left','right']:
      axes[row][cloumn].spines[axis].set_linewidth(3)
      axes[row][cloumn].spines[axis].set_color('green')
  else:
    p=rounds(p_value,2)
    sub_text='r=' +str(r)+'\n'+'p='+str(p)
    axes[row][cloumn].text(posx, posy,sub_text, ha='left',fontsize=5)
  
  if row==14:
    axes[row][cloumn].set_xlabel(patience_scale["Item"][item] ,fontproperties=font).set_fontsize(9)
    

  if cloumn==0:
    axes[row][cloumn].set_ylabel(ytitle ,fontproperties=font).set_fontsize(9)
    axes[row][cloumn].get_yaxis().set_label_coords(-0.65,0.5)
    axes[row][cloumn].tick_params(axis="y", labelsize=8)
  if row!=14:
    axes[row][cloumn].tick_params(
    axis='x',          # changes apply to the x-axis
    bottom=False,      # ticks along the bottom edge are off
    top=False,         # ticks along the top edge are off
    labelbottom=False) # labels along the bottom edge are off
  if cloumn!=0:
    axes[row][cloumn].tick_params(
    axis='y',          # changes apply to the x-axis
    left=False,      # ticks along the bottom edge are off
    top=False,
    labelleft=False) # labels along the bottom edge are off
    


  if full_grade>60:
    axes[row][cloumn].xaxis.set_ticks(np.arange(-(full_grade),full_grade+7, full_grade))
    axes[row][cloumn].set_xlim([-full_grade-28,full_grade+28])
  elif full_grade>10 and full_grade<60:
    axes[row][cloumn].xaxis.set_ticks(np.arange(-(full_grade),full_grade+5, full_grade))
    axes[row][cloumn].set_xlim([-full_grade-15,full_grade+15])
  elif full_grade==1 :
    axes[row][cloumn].xaxis.set_ticks(np.arange(-(full_grade),full_grade+0.5, full_grade))
    axes[row][cloumn].set_xlim([-full_grade-0.5,full_grade+0.5])
  elif full_grade==2:
    axes[row][cloumn].xaxis.set_ticks(np.arange(-(full_grade),full_grade+1, full_grade))
    axes[row][cloumn].set_xlim([-full_grade-1,full_grade+1])
  elif full_grade==6:
    axes[row][cloumn].xaxis.set_ticks(np.arange(-(full_grade),full_grade+2, full_grade))
    axes[row][cloumn].set_xlim([-full_grade-3,full_grade+3])
  else:    
    axes[row][cloumn].xaxis.set_ticks(np.arange(-(full_grade),full_grade+1, full_grade))
    axes[row][cloumn].set_xlim([-full_grade-2,full_grade+2])

font = FontProperties(fname=r"c:\windows\fonts\msjh.ttc", size=10)

#得到資料位置
path='../'+u"雙和中風"+"/"+u"血壓與量表"
folder=os.listdir(path)
info=[]
patience_scale=pd.DataFrame()
patience_BP=pd.DataFrame()
scale_temp=pd.DataFrame()
item_temp=pd.DataFrame()
BP_temp=pd.DataFrame()
for i in range(len(folder)):
  exec('temp=u"{}"'.format(folder[i])) #
  file_excel=os.listdir(path+"/"+temp)
  
  for j in range(len(file_excel)):
    domain=path+"/"+temp
#    print(domain+"/"+file_excel[i])
    if file_excel[j].find('血壓')>0:
      BP_temp=read_bp(os.path.join(domain,file_excel[j]),i,temp)
      patience_BP=pd.concat([patience_BP,BP_temp])
    else:
      item_temp,scale_temp =read_scale(os.path.join(domain,file_excel[j]),i,temp)
      if i==0 :
        patience_scale=item_temp
      patience_scale=pd.concat([patience_scale,scale_temp],axis=1)
#    info.append( os.path.join(domain,file_excel[i]))
cols = patience_BP.columns.tolist()
cols = cols[-1:] + cols[:-1]
patience_BP=patience_BP[cols]

print(info)




title_ytext1=[u'上午\n收縮', u'下午\n收縮', u'整體\n收縮', u'上午\n舒張', u'下午\n舒張',
u'整體\n舒張',u'上午\n心率', u'下午\n心率', u'整體\n心率', u'早晚\n收縮\n差值', u'早晚\n舒張\n差值',
u'早晚\n心率\n差值',u'上午\n脈壓\n差值',u'下午\n脈壓\n差值',u'整體\n脈壓\n差值']

title_ytext2=[u'變異量',u'斜率']



#畫圖
fig_row=15
fig_col=17
BP_xindex=patience_BP.axes[1]
BP_xindex=BP_xindex.delete(0)
BP_yindex=patience_BP.axes[0]


for l in range(len(title_ytext2)): # ['VAR','SLOP']
  x_count=0
  fig,axes= plt.subplots(nrows=fig_row, ncols= fig_col, gridspec_kw = {'wspace':0, 'hspace':0})
#  fig.text(10,10,'123')
#  plt.gcf().text(0.02, 14, '123', fontsize=8)
  fig.subplots_adjust(right=0.99,left=0.07,top=0.99,bottom=0.1)
  fig.canvas.set_window_title(u'量表'+' vs '+ u'血壓'+title_ytext2[l])
  for ii, ax in enumerate(fig.axes):# 讓子圖相連
#    print('ii',ii)
    if ii % fig_col==0 or ii >(fig_row-1)*(fig_col-1)-fig_col:
      continue
    
    ax.set_xticklabels([])
    ax.set_yticklabels([])
#  plt.grid(True)
  for k in range(1,len(patience_scale["Item"])+1):# 量表項目長度
    for m in range(len(BP_xindex)):
      j=x_count//15
      i=x_count%15
#      plot_subplot(i,j,patience_scale["Item"][k],title_ytext1[m]+title_ytext2[l],patience_scale["Gd"][k-1:k].T,patience_BP[BP_xindex[m]][BP_yindex[l]],patience_scale["FD"][k],k)
      plot_subplot(i,j,patience_scale["Item"][k],title_ytext1[m],patience_scale["Gd"][k-1:k].T[k].tolist(),patience_BP[BP_xindex[m]][BP_yindex[l]],patience_scale["FD"][k],k)
      x_count+=1
plt.show()


