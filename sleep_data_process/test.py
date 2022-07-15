#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May  4 00:47:51 2020

@author: hao
"""
import random
a=[0,1,0,1,0]

d=[]
for i in range(len(a)):
    b=random.uniform(5, 20)
    c=random.uniform(1, 5)
    if a[i]==1:
        d.append(b)
    else:
        d.append(c)
print(d)