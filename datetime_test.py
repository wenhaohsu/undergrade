#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 10 09:43:44 2020

@author: hao
"""
import re
from datetime import datetime, timedelta
#二級函數，從投訴內容中，過濾出用戶反應問題發生的時間，通過re正則表達式實現
def searchwhen(content):
     #問號代表的是非貪婪模式,.*?連在一起是取盡量少的任意字符
     # m = re.search(u"從((([0-9]{2,4}年)|([0-9]{1,2}月)|([0-9]{1 ,2}日))(.*?))開始", content)
     # (?: re)類似(...),但是不表示一個組
     #第一重保護，通過正則表達式，限制年月日的數字範圍
    m = re.search(u"从(((([0-9]{2,4})年)?(([0-9]{1,2})月)?(([0-9]{1,2})日)?)(?:.*?)"
                  u"(([1-2]?[0-9])[:：点时]([0-5][0-9])?(?:[:：分]([0-5][0-9]))?)?)开始", content)
    # m.groups()的结果：('2017年12月27日15：00:42', '2017年12月27日', '2017年', '2017', '12月',
    #  '12', '27日', '27', '15：00:42', '15', '00', '42')
    when = None
    dt = None
    if m:
        datetuple = m.groups()
        syear = datetuple[3]
        smonth = datetuple[5]
        sdate = datetuple[7]
        shour = datetuple[9]
        sminute = datetuple[10]
        ssecond = datetuple[11]
        if syear or smonth or sdate:
            y = 2018
            mo = 1
            d = 1
             #如果有值，就轉為整數
            if sdate:
                #使用三目運算，做第二重保護，還有第三重保護validatedate
                d = int(sdate) if int(sdate) < 32 else 31
            if smonth:
                mo = int(smonth) if int(smonth) < 13 else 12
            if syear:
                y = whichyear(syear)
                #當年份數值不是None，則確定年份，不管月日有沒有，有則已經賦值，沒有則使用默認時間，
                #均滿足生成時間datetime的三個參數(年，月，日)
                if y:
                    dt = validatedate(y, mo, d)
            else:
                # 如果存在月份，但没有年份
                if smonth:
                    #先把年設為今年
                    y = datetime.now().year
                    dt = validatedate(y, mo, d)
                    #如果設為今年後，日期比當前時間大，說明年份應設為去年
                    if dt > datetime.now():
                        #年不像月，有1-12月限制，年不會減到0，可以用y-1表示去年
                        dt = validatedate(y - 1, mo, d)
                # 如果年份月份都没有
                else:
                     #月先設為當月，年先設為當年
                    mo = datetime.now().month
                    y = datetime.now().year
                    dt = validatedate(y, mo, d)
                    #如果添加年月後的日期比當前日期還往後，說明年月填錯了，需要改為上月。
                    if dt > datetime.now():
                        dt = todayoflastmonth(dt)
        if dt:
             #如果小時不為空，則設置為dt的小時，分別設置時分秒，因為，datetime創建時，默認的時間時00：00：00
            if shour:
                dt = dt.replace(hour=int(shour) if int(shour) < 24 else 23)
            #如果分鐘不為空，則設置為dt的分鐘
            if sminute:
                dt = dt.replace(minute=int(sminute) if int(sminute) < 60 else 59)
            #如果秒不為空，則設置為dt的秒
            if ssecond:
                dt = dt.replace(second=int(ssecond) if int(ssecond) < 60 else 59)
    else:
        print( "沒有時間" )
    return dt


'''
         when = m.group(1)
         print(when)
         m1 = re.search(u"([0-9]{2,4})年", when)
         m2 = re.search(u"(1 [0-2]|[1-9])月", when)
         m3 = re.search(u"([0-9]{1,2})日", when)
         #默認年份為當前時間的當年
         y = None
         mo = None
         d = None
         if m1:
             yearstr = m1.group(1)
             #如果年份不足4位，則通過最長公共子序列，對比近10年中哪個年份與這個不完整的字符串最匹配。
            if len(yearstr) != 4:
                 thisyear = datetime.now().year
                 #從今年開始，向前找匹配的年份，一旦找到，則停止循環。
                for n in range(0, 10):
                     if yearstr == find_lcseque(str(thisyear-n), yearstr):
                        y = thisyear-n
                         break
             else:
                 y = int(yearstr)
         #判斷日存在不存在，並進行相應賦值
         if m3:
             d = int(m3.group(1))
         else:
             #如果不存在日期，直接設為1號，因為經過u"從((([0-9]{2,4}年)|([0-9]{1,2}月)|([0-9]{1,2}日))(.*?))開始"過濾，
             #一定會存在年月日中的一項。不存在日說明，存在年或月。
            d = 1
         #判斷月份存在不存在，並賦值
         if m2:
             mo = int(m2.group(1))
         else:
             #月份為空，看是否有年，如果有年，則設為1月，
             #沒有年只有日，則月設為當前時間的月份，年設為當前年份
             #或者日大於當前日，則設為上月，年設為上月的年份
             if y:
                mo = 1
                 dt = datetime(y, mo, d)
             else:
                 #沒有年，月先設為當月，年先設為當年
                 mo = datetime.now().month
                 y = datetime.now().year
                 dt = datetime(y, mo, d)
                 #如果添加年月後的日期比當前日期還往後，說明年月填錯了，需要改為上月。
                if dt > datetime.now():
                     dt = todayoflastmonth(dt)
         #查找時分秒
         m4 = re.search(u"([1-2]?[0-9][:：點時]([0-5 ][0-9])?([:：分]([0-5][0-9]))?)", when)
         h = None
         m = None
         s = None
         if m4:
             #根據m4搜索結果m4.group(1)的15：00，再次分組搜索時分秒


            m5 = re.search(u"([1-2]?[0-9])[:：點時]([0-5][0-9])?([:：分]([0- 5][0-9]))?", m4.group(1))
             if m5:
                 hhmmss = m5.groups()
                 # match.groups()函數的返回值是組元，包括每個小括號的結果。('15', '00', None, None)
                 if hhmmss[0]:
                     h = int(hhmmss[0])
                 if hhmmss[1]:
                     m = int(hhmmss[1])
                 if hhmmss[3]:
                     s = int(hhmmss[3])
         if y is None:
             y = datetime.now().year
             dt = datetime(y, mo, d)
             #如果設為今年後，日期比當前時間大，說明年份應設為去年
             if dt > datetime.now():
                #年不像月，有1-12月限制，年不會減到0，可以用y-1表示去年
                 dt = datetime(y-1, mo, d)
         #如果dt為空，說明年月日都有，則直接通過年月日生成dt
         if dt is None:
             dt = datetime(y, mo, d)
         #如果h不為空，則設置dt的小時為h
         if h:
             dt = dt.replace(hour= h)
         #如果m不為空，則設置dt的分鐘為m
         if m:
             dt = dt.replace(minute=m)
         #如果s不為空，則設置dt的秒為s
         if s:
             dt = dt. replace(second=m)
'''

#求上一個月的今天,輸入輸出格式datetime.datetime(2018, 3, 19, 0, 0)
def todayoflastmonth(dt):
    # 本月第一天
    firstday = datetime(dt.year, dt.month, 1)
    #上月最後一天
    premonthlastday = firstday - timedelta(days=1)
    # 返回上月的今天
    return datetime(premonthlastday.year, premonthlastday.month, dt.day)


#最長公共子序列(The Longest Common Subsequence)子串要求字符必須是連續的，但是子序列就不是連續的。
def find_lcseque(s1, s2):
    # 生成字符串长度加1的0矩阵，m用来保存对应位置匹配的结果
    m = [[0 for x in range(len(s2) + 1)] for y in range(len(s1) + 1)]
    # d用来记录转移方向
    d = [[None for x in range(len(s2) + 1)] for y in range(len(s1) + 1)]

    for p1 in range(len(s1)):
        for p2 in range(len(s2)):
            if s1[p1] == s2[p2]:  # 字符匹配成功，则该位置的值为左上方的值加1
                m[p1 + 1][p2 + 1] = m[p1][p2] + 1
                d[p1 + 1][p2 + 1] = 'ok'
            elif m[p1 + 1][p2] > m[p1][p2 + 1]:  # 左值大于上值，则该位置的值为左值，并标记回溯时的方向
                m[p1 + 1][p2 + 1] = m[p1 + 1][p2]
                d[p1 + 1][p2 + 1] = 'left'
            else:  # 上值大于左值，则该位置的值为上值，并标记方向up
                m[p1 + 1][p2 + 1] = m[p1][p2 + 1]
                d[p1 + 1][p2 + 1] = 'up'
    (p1, p2) = (len(s1), len(s2))
    s = []
    while m[p1][p2]:  # 不为None时
        c = d[p1][p2]
        if c == 'ok':  # 匹配成功，插入该字符，并向左上角找下一个
            s.append(s1[p1 - 1])
            p1 -= 1
            p2 -= 1
        if c == 'left':  # 根据标记，向左找下一个
            p2 -= 1
        if c == 'up':  # 根据标记，向上找下一个
            p1 -= 1
    s.reverse()
    return ''.join(s)


# 将年份数字字符串str，转换为整形int，如果年份不是四位数，通过最长公共子序列对比近几年的年份，找到匹配度最高的最近的年份
def whichyear(yearstr):
    # 如果年份不足4位，则通过最长公共子序列，对比近10年中哪个年份与这个不完整的字符串最匹配。
    y = None
    thisyear = datetime.now().year
    strlength = len(yearstr)
    if strlength != 4:
        # 从今年开始，向前找匹配的年份，一旦找到，则停止循环。
        # 如果输入的年份字符串大于4个字符，如20166，则与2016对比结果的长度为4，如果小于4个字符，如206，则对比结果长度为3
        # 三目运算
        min = strlength if strlength < 4 else 4
        for n in range(0, 9):
            # 原来的条件yearstr == find_lcseque(str(thisyear - n), yearstr)，但不满足输入字符串201666超过4个字符的情况
            if min == len(find_lcseque(str(thisyear - n), yearstr)):
                y = thisyear - n
                break
    else:
        # 如果日期是4位的，可能写错位，比如2018写成2108
        # 最长匹配长度
        longestlen = 0
        # 最接近的年份
        proximateyear = thisyear
        # 向前找近10年的年份，哪个年份与输入年份匹配度最高
        for n in range(0, 9):
            lcsstr = find_lcseque(str(thisyear - n), yearstr)
            if longestlen < len(lcsstr):
                longestlen = len(lcsstr)
                proximateyear = thisyear - n
        y = proximateyear
    return y


# 判断生成日期的年月日是否符合相应的范围，比如月的范围是1-12，日的范围根据月不同而不同，自己调用自己，递归调用
def validatedate(y, mo, d):
    dt = None
    try:
        dt = datetime(y, mo, d)
    except ValueError as e:
        print(str(y) + str(mo) + str(d))
        print(e.args)
        # 从datetime的错误提示中，过滤关键字，注意是句首的关键字,有尖号^
        # year 20166 is out of range
        # month must be in 1..12
        # day is out of range for month
        ma = re.search(u"^(year)|(month)|(day)", str(e))
        ymd = ma.groups()
        # print(ymd)
        if ymd[0]:
            dt = validatedate(whichyear(str(y)), mo, d)
        if ymd[1]:
            recoveredmonth = 1
            if mo > 12:
                recoveredmonth = 12
            dt = validatedate(y, recoveredmonth, d)
        if ymd[2]:
            dt = validatedate(y, mo, 1)
    finally:
        return dt
