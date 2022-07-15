#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 14 11:17:15 2020

@author: hao
"""

from datetime import datetime
#print(datetime.now())
from dateutil import parser
date=parser.parse("2020/2/14 00:00:00") #字串轉換成日期(y-m-d h:m:s)
#print(date.strftime('%A'))#這天是星期幾
import numpy as np
date2=np.array('2020-02-14').astype('datetime64') 
date3=date2+np.arange(12)#日期可以透過numpy做運算，前提是要做成datetime64的格式
ymd=np.datetime64('2020-01-01')
ymdhm=np.datetime64('2020-01-01 12:00')
ymdhms=np.datetime64('2020-01-01 12:00:00')
ymdhmsms=np.datetime64('2020-01-01 12:00:00.05','ms')
#datetime64的格式可以做年月日時分秒，甚至毫秒以上的小單位
import pandas as pd
date4=pd.to_datetime([datetime.now(),'1st of Jan, 2020',
                      '2020-Jan-1','01-01-2020','20200101'])
#以上格式都能轉成:年-月-日，的格式
date5=pd.to_datetime(datetime.now())+pd.to_timedelta(np.arange(12),'s')
#timedelta可以做時間的運算
dates=pd.date_range('2020/1/1',datetime.now())#把今年到今天的天數列入
dates_2=dates.to_period('H')
dates_3=dates_2-dates_2[0]
#print(daterange)
#pd.date_range('2020/1/1',period=)
a=pd.to_datetime(['00:01:00','00:02:00'])
#for i in range(0,100,10)
delta=date+pd.to_timedelta(np.arange(1,100,10),unit='s')
print(delta)
