# -*- coding: utf-8 -*-
"""
Created on Wed May  8 16:28:47 2019

@author: william
"""
from csv import reader
from itertools import chain
from pandas.core.frame import DataFrame
import os
import numpy as np
import pandas as pd
from sklearn import preprocessing
import torch
import torch.utils.data as Data
import torch.nn as nn

class process:
  def datainput_xenon(x,y = False):
    row_array = []
    row_chain = []
    for t in range(len(x)):
      with open (x[t],"r",encoding ="latin-1") as f:
        data = reader(f,delimiter=',')
        row_in = []
        for row in data:
          row_in.append(row)
        for i in range(len(row_in)):
          del row_in[i][0:5]
        row_array.append(row_in)
    row_chain = list(chain(*row_array))
    if y == True:
      return row_chain
    else:
      row_excel = DataFrame(row_chain)
      return row_excel
  def search(path, word):
    data = []
    for filename in os.listdir(path):
        fp = os.path.join(path, filename)
        if os.path.isfile(fp) and word in filename:
            data.append(fp)
        elif os.path.isdir(fp):
            search(fp, word)
    return data
  def padding(x,y):
    ap_bpm = []
    for i in range(len(y)):
      ap_ = []
      for j in range(0,len(x)):
        ts= x[j]
        if y[i] not in ts:
          ap_.append(-200)
        else:
          aps = ts.index(y[i])
          ap_.append(ts[aps+1])
      ap_bpm.append(ap_)
    return ap_bpm
  def target_process(x,y=1):
    traintarget = np.zeros([len(x),y],float)
    traintarget[0:1160,0] = 0
    traintarget[1160:2317,0] = 1
    traintarget[2317:3670,0] = 2
    traintarget[3670:4980,0] = 3
    traintarget[4980:5820,0] = 4
    traintarget[5820:7064,0] = 5
    traintarget[7064:7789,0] = 7
    traintarget[7789:8254,0] = 8
    traintarget[8254:9424,0] = 6
    return traintarget
  def data_excelceview(x,y):
    ap_signal = []
    data = []
    for i in range(len(y)):
      signal = pd.DataFrame(x[i],columns = [y[i]])
      ap_signal.append(signal)
    ap_bpmt = ap_signal[0]
    for j in range(1,len(ap_signal)):
      ap_bpmt = pd.concat([ap_bpmt,ap_signal[j]],axis = 1)
    data.append(ap_bpmt)
    return data
  def excel_input(x):
    data_excel = []
    for i in range(len(x)):
      data = pd.read_excel(x[i])
      data_excel.append(data)
    return data_excel
  def drop_na(x):
    list_data = []
    data = []
    for i in range(len(x)):
      list_use = x[i].dropna(axis=0, how='any')
      list_data.append(list_use)
    ap_bpmt = list_data[0]
    for j in range(1,len(list_data)):
      ap_bpmt = pd.concat([ap_bpmt,list_data[j]],axis = 0)
    data.append(ap_bpmt)
    return data
  def drop_na_one(x,y):
    list_data = []
    data = []
    for i in range(len(x)):
        list_dd = x[i]
        list_use = list_dd
        list_dd = list_dd.drop([y],axis = 1)
        list_use = list_use[y].dropna(axis=0, how='any')
        list_uses = pd.concat([list_dd,list_use],axis = 1,join = 'inner')
        list_data.append(list_uses)
    ap_bpmt = list_data[0]
    for j in range(1,len(list_data)):
      ap_bpmt = pd.concat([ap_bpmt,list_data[j]],axis = 0)
    data.append(ap_bpmt)
    return data
  def normal_min_max_scalar(x,y): #x ???input data, y???target???column?????? ?????????string????????? 'column??????'
    min_max_scaler = preprocessing.MinMaxScaler()#?????????
    target = x[0][y]-1
    use_data = x[0].drop([y],axis = 1)
    index = use_data.index
    column = list(use_data.columns.values)
    use_data = min_max_scaler.fit_transform(use_data)
    use_data = pd.DataFrame(use_data,columns = column)
    use_data['index'] = index
    use_data = use_data.set_index('index')
#norm-l2  ???????????????l2????????? ||X||p=(|x1|^p+|x2|^p+...+|xn|^p)^1/p (l2, ???p?????????2),???????????????????????????????????????????????????????????????????????????????????????
    use_data = pd.concat([use_data,target],axis = 1)
    return use_data
  def random_sampling(x,y):
    training_use = DataFrame.sample(x,n=None, frac=0.7, replace=False, weights=None, random_state=None, axis=None)
    indexs = list(training_use.index)
    training_target = training_use[y].as_matrix()
    training_use = training_use.drop([y],axis = 1)
    test_validation = x.drop(index=indexs, axis=1, inplace=False)
    testing_target = test_validation[y].as_matrix()
    test_validation = test_validation.drop([y],axis = 1)
    return training_use,training_target,test_validation,testing_target
  def tensor_torch(a,c,b,d,z):#a:training data, c: train target, b: test data, d: test target
    inputdata = torch.from_numpy(a.values.astype(float)).type(torch.FloatTensor)
    traintarget = torch.from_numpy(c.reshape(len(c))).type(torch.LongTensor)
    testdata = torch.from_numpy(b.values.astype(float)).type(torch.FloatTensor)
    testtarget = torch.from_numpy(d.reshape(len(d))).type(torch.LongTensor)
#validation = torch.from_numpy(validation.values.astype(float)).type(torch.FloatTensor)
    train_data = Data.TensorDataset(inputdata,traintarget)
    test_data = Data.TensorDataset(testdata,testtarget)
    train_loader = Data.DataLoader(dataset=train_data, batch_size=z, shuffle=True)
    test_loader = Data.DataLoader(dataset=test_data, batch_size=z, shuffle=True)
    return train_loader,test_loader

class Net(nn.Module):
    
    def __init__(self):
        super(Net, self).__init__()
        self.fc1 = nn.Linear(5, 50) 
        self.relu = nn.ReLU()
#        self.drop1 = nn.Dropout(0.25)
        self.fc2 = nn.Linear(50, 50)  
        self.relu = nn.ReLU()
#        self.drop2 = nn.Dropout(0.15)
        self.fc3 = nn.Linear(50, 50)  
        self.relu = nn.ReLU()
#        self.drop2 = nn.Dropout(0.15)
        self.fc4 = nn.Linear(50, 50)  
        self.relu = nn.ReLU()
#        self.drop3 = nn.Dropout(0.10)
        self.fc5 = nn.Linear(50, 50)  
        self.relu = nn.ReLU()
        
        self.fc6 = nn.Linear(50, 50)  
        self.relu = nn.ReLU()
#        self.drop2 = nn.Dropout(0.15)
        self.fc7 = nn.Linear(50, 50)  
        self.relu = nn.ReLU()
#        self.drop2 = nn.Dropout(0.15)
        self.fc8 = nn.Linear(50, 50)  
        self.relu = nn.ReLU()
#        self.drop3 = nn.Dropout(0.10)
        self.fc9 = nn.Linear(50, 50)  
        self.relu = nn.ReLU()
#        self.fc6 = nn.Linear(80, 15)  
        self.fc10 = nn.Linear(50, 2)  
    def forward(self, x):
        out = self.fc1(x)
        out = self.relu(out)
#        out = self.drop1(out)
        out = self.fc2(out)
        out = self.relu(out)
#        out = self.drop2(out)
        out = self.fc3(out)
        out = self.relu(out)
#        out = self.drop2(out)
        out = self.fc4(out)
        out = self.relu(out)
#        out = self.drop3(out)
        out = self.fc5(out)
        out = self.relu(out)
        
        out = self.fc6(out)
        out = self.relu(out)
#        out = self.drop2(out)
        out = self.fc7(out)
        out = self.relu(out)
#        out = self.drop2(out)
        out = self.fc8(out)
        out = self.relu(out)
#        out = self.drop3(out)
        out = self.fc9(out)
        out = self.relu(out)
        
        out = self.fc10(out)
        return out
