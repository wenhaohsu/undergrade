#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Hao

水仙花
a*100+b*10+c = a**d + b**d + c**d
print:1-1000的水仙花
"""
limit = 10001
def narcissus():
#	print('输出所有水仙花数：' )
	for i in range(0,limit):
		       temp=i
		       sum=0
		       a=len(str(i))
		       while temp:
			       sum+=(temp%10)**a
			       temp//=10
			       if sum==i:
				       print(i,end='  ')

narcissus()
