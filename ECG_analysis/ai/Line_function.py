#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 25 11:17:35 2019

@author: chenghan
"""
import requests
import json

class Line_function:
    
    
    def pushRequest_xenonhelper(message,userID):
        PUSHURL = 'https://api.line.me/v2/bot/message/push'

        CHANNEL_ACCESS_TOKEN = 'Nzyyv6xValODf0H+n6Bt5JZcWo2Bj2Q9FFSWMbbDUhri/XnZ5Q71MIPapidjawRkByiAPB7c3D+DPnbXVVfXaCpWA0h2jQ4xvFuPT3eOmnxH7ZVh1BUqTTgki3WqB/+mIL1C4sP5SLe58eoyfAe2xgdB04t89/1O/w1cDnyilFU='    
        headers={      'Content-Type': 'application/json; charset=UTF-8',
                         'Authorization': 'Bearer ' + CHANNEL_ACCESS_TOKEN
                }
        payload={
                'to': userID,                           #user Line ID in this chatbot
                'messages': [{
                                'type': 'text',
                                'text': message        #message
                            }]
                }
                            
        r=requests.post(PUSHURL,data=json.dumps(payload),headers=headers)
        
        return r