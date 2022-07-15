# -*- coding: utf-8 -*-
"""
Created on Mon May 13 11:06:00 2019

@author: william
"""

from Wei_datainput import process as pro
from Wei_datainput import Net as ne
from itertools import chain
import torch.nn as nn
import torch
import pandas as pd
data = []
data_chain = []

num_input=3
num_output=2

site = ['13','14','17','18']#少1020
for i in range(len(site)):
  data.append(pro.search('C:\\Users\\kylab\\Desktop\\patch_wei\\validatedata'+str(num_input)+'input'+str(num_output)+'output',site[i]))
data_chain = list(chain(*data))
excel_data = pro.excel_input(data_chain)
excel_data_proce = excel_data
use_data = pro.drop_na(excel_data_proce)
#跟家緯不一樣
use_data = use_data[0].rename(index = str,columns={'Unnamed: 0':'index'})
use_data = [use_data.set_index('index')]
out_data = use_data[0].drop(['score'],axis = 1)


use_data = pro.normal_min_max_scalar(use_data,'score')



targets = use_data['score'].as_matrix()
input_datas = use_data.drop(['score'],axis = 1)
#%%
input_data = torch.from_numpy(input_datas.values.astype(float)).type(torch.FloatTensor)
target = torch.from_numpy(targets.reshape(len(targets))).type(torch.LongTensor)
net = ne()
net.load_state_dict(torch.load('params_dnn_2019_06_04_input'+str(num_input)+'_output'+str(num_output)+'_hiddenlayer7_1000_epoch.pkl'))
criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(net.parameters(), lr = 0.0001)
#%%
pred_as = []
sacces = []
test_output = net(input_data)
_, pred = test_output.max(1)
#num_correct = (pred == training_target_).sum().item()
#acc = num_correct / training_use.shape[0]
pred = pred.numpy()
pred = torch.max(test_output, 1)[1].data.numpy().squeeze()
print(sum(pred==targets)/len(pred))
predss = pd.DataFrame(pred,columns = ['predict'])
index = use_data.index
predss['index'] = index
predss = predss.set_index('index')
pred_as.append(pred)
output_excel = pd.concat([out_data,predss],axis = 1)
output_excel.to_excel("output.xlsx",sheet_name='predict_output')

