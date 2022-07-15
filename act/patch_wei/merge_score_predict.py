# -*- coding: utf-8 -*-
"""
Created on Mon May 20 10:41:42 2019

@author: kylab
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import os

listcwd=os.listdir(os.getcwd()+'/validatedata_output')

filename=os.getcwd()+'/validatedata_output/'+listcwd[2]
xls = pd.ExcelFile(filename)
sheetX = xls.parse('data')

xls_output = pd.ExcelFile(filename.replace('.xlsx','_output.xlsx'))
sheetX_output = xls_output.parse('predict_output')

#a=pd.merge([xls,xls_output])

a=pd.merge(sheetX,sheetX_output)#sheetX.merge(sheetX_output,left_on='lkey',right_on='rkey')

