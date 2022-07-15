#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 13 01:04:24 2020

@author: hao
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import scipy.stats as stats
#%%
def U_test(group1, group2):
    mean1 = np.median(group1)
    mean2 = np.median(group2)
    std1 = np.std(group1)
    std2 = np.std(group2)
    nobs1 = len(group1)
    nobs2 = len(group2)  
    modified_std1 = np.sqrt(np.float32(nobs1)/
                    np.float32(nobs1-1)) * std1
    modified_std2 = np.sqrt(np.float32(nobs2)/
                    np.float32(nobs2-1)) * std2
    (statistic, pvalue) = stats.ttest_ind_from_stats( 
               mean1=mean1, std1=modified_std1, nobs1=nobs1,   
               mean2=mean2, std2=modified_std2, nobs2=nobs2 )
    return statistic, pvalue

#def SE(sample):
#
#    std=np.std(sample,ddof=0)
#
#    standard_error=std/np.sqrt(len(sample))
#
#    return standard_error
#%%
#df.loc["Goldfinger"]
df = pd.read_excel('posagroup.xlsx')
bar_width = 0.35
posa_median = df.groupby(['group','Posture']).median()
HRV_se = df.groupby(['group','Posture']).std()
posture = ['supine','right']#,'left','prone']
indx = np.arange(len(posture))
#score_label = np.arange(0, max(df.RR), max(df.RR)/5)
posa_medians = list(posa_median.T[1].loc["RR"])
nonposa_medians = list(posa_median.T[0].loc["RR"])
posa_se = list(HRV_se.T[1].loc["RR"])
nonposa_se = list(HRV_se.T[0].loc["RR"])
#%%
fig, ax = plt.subplots()
barMale = ax.bar(indx - bar_width/2,posa_medians,bar_width,yerr=posa_se/(np.sqrt(len(df[df['group']==1]))),label='Male means',color='white')
barFemale = ax.bar(indx + bar_width/2,nonposa_medians,bar_width,yerr=nonposa_se/(np.sqrt(len(df[df['group']==0]))),label='Female means',color='k')
#

# inserting x axis label
ax.set_xticks(indx)
ax.set_xticklabels(posture)

# inserting y axis label
#ax.set_yticks(score_label)
#ax.set_yticklabels(score_label)

# inserting legend
ax.legend()

def insert_data_labels(bars):
	for bar in bars:
		bar_height = bar.get_height()
		ax.annotate('{0:.0f}'.format(bar.get_height()),
			xy=(bar.get_x() + bar.get_width() / 2, bar_height),
			xytext=(0, 3),
			textcoords='offset points',
			ha='center',
			va='bottom'
            
		)

insert_data_labels(barMale)
insert_data_labels(barFemale)

plt.show()