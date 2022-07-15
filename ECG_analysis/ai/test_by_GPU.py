#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 21 11:25:24 2019

@author: hao
"""

import torch
import ecg_cuda_competition as ec
import pandas as pd
test = pd.read_csv('file') #這是把心電訊號轉成的CSV檔匯入
testdata = torch.from_numpy(test.values.astype(float).reshape(lens/sampling,1,sampling)).type(torch.cuda.FloatTensor)
#len:資料長度，sampling:採樣頻率
cnn = ec.CNN()
use_cuda = True
if use_cuda and torch.cuda.is_available():
  cnn.cuda()
pred_as = []
cnn.load_state_dict(torch.load('path'))#path是訓練好的模型的位子與檔名，檔案類型是pkl檔
for i in range(0,len(testdata),255):
   test_output = cnn(testdata[i:i+255].cuda())
   _, pred = test_output.max(1)
   pred = pred.cpu().data.numpy()
   pred_as.append(pred)
#num_correct = (pred == training_target_).sum().item()
#acc = num_correct / training_use.shape[0]
print(pred_as)