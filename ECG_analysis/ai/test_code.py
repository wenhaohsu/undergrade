# -*- coding: utf-8 -*-
"""
Created on Wed Sep 18 09:08:45 2019

@author: william
"""

import ecg_competition_CNN_model as ec
import torch
train_d,train_t,test_d,test_t = ec.data_prepare.data_loading('train_ecg.csv','train_label_ecg.npy','test_ecg.csv','test_label_ecg.npy')
train_loader,test_loader,inputdata,testdata = ec.data_prepare.data_package(train_d,train_t,test_d,test_t)
cnn = ec.CNN()
#%%
#optimizer,loss_func = ec.parameter_use('params_cnn_2019_9_13.pkl',lr = 0.01)
pred_as = []
cnn.load_state_dict(torch.load('D:/python/python/params_cnn_2019_9_13.pkl'))
test_output = cnn(testdata[0:1000])
_, pred = test_output.max(1)
#num_correct = (pred == training_target_).sum().item()
#acc = num_correct / training_use.shape[0]
pred = pred.data.numpy()
#pred = torch.max(test_output, 1)[1].data.numpy().squeeze()
#  print(sum(pred==test_t)/len(pred))
#predss = pd.DataFrame(pred)
pred_as.append(pred)

