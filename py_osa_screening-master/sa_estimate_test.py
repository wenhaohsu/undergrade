# -*- coding: utf-8 -*-
"""
Created on Wed Aug  5 17:14:53 2020

@author: kylab
"""

import os
from SA_estimate import SA_report
import pandas as pd

path='\\data' #\\data
listcwd=os.listdir(os.getcwd()+path)
SA_report_dic={}
for k in range(len(listcwd)):#len(listcwd)
    try:
        if '.txt' in listcwd[k]:
            sa=SA_report()
            sa.f_getSAReport(filename=os.getcwd()+path+'/'+listcwd[k])
        
            SA_report_dic[listcwd[k].replace('.txt','')]={'Baseline':sa.baseline,'Mean':sa.meanSPO2,'Lowest':sa.LowestSPO2,'ODI':sa.AHI_new,'ODE':sa.ODE_new,'Estimated_SA':sa.osa_level,'Total_record_time':sa.Total_Record_time,
                       'Record_time_start':sa.Record_start,'Record_time_end':sa.Record_end,'ratio_under_90':sa.ratio_under90}

        
            print(listcwd[k])
    except:
        continue
try:
    writer = pd.ExcelWriter('SPO2.xlsx')
    pd.DataFrame(SA_report_dic).T.to_excel(writer,'data')
    writer.save()
    print("Done")
        
except PermissionError:
        print("You don't have the permission to write the file, check whether your file is already open.")