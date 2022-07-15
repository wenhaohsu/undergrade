# -*- coding: utf-8 -*-
"""
Created on Wed Sep 18 12:04:12 2019

@author: william
"""

import numpy as np
from csv import reader
from pandas.core.frame import DataFrame
import pandas as pd
from itertools import chain
import torch
import torch.utils.data as Data
import torch.nn as nn
from torch.autograd import Variable

class data_prepare:
  def data_loading(w,x,y,z):
    '''
    w : 放入training data 的csv檔案
    x : 放入training target 的npy檔案
    y : 放入testing data 的csv檔案
    z : 放入testing target 的npy檔案
    '''
    train_d = pd.read_csv(w)
    train_d = train_d.set_index('index_label')
    train_t = np.load(x)
    test_d = pd.read_csv(y)
    test_d = test_d.set_index('index_label')
    test_t = np.load(z)
    return train_d,train_t,test_d,test_t
#%%
  def data_package(w,x,y,z):
    '''
    w : 放入training data 
    x : 放入training target
    y : 放入testing data
    z : 放入testing target
    產出兩個dataloader
    '''
    traintarget = torch.from_numpy(x.reshape(len(x))).type(torch.LongTensor)
    #Ｘ是只要輸入的資料
    testtarget = torch.from_numpy(z.reshape(len(z))).type(torch.LongTensor)
    #Ｚ是我們要輸出的資料，testtarget換成validtarget
    inputdata = torch.from_numpy(w.values.astype(float).reshape(len(w),1,700)).type(torch.FloatTensor)
    #換成要輸入的資料，700是點作為切割，這裡要想想是不是30點
    testdata = torch.from_numpy(y.values.astype(float).reshape(len(y),1,700)).type(torch.FloatTensor)
    #換成要輸出的資料，700是點作為切割，這裡要想想是不是30點
    '''
    這裡可以用transform.Compose
    '''
    train_data = Data.TensorDataset(inputdata,traintarget)
    test_data = Data.TensorDataset(testdata,testtarget)
    train_loader = Data.DataLoader(dataset=train_data, batch_size=256, shuffle=True)
    #batch size約50以上(至少為2的倍數)
    test_loader = Data.DataLoader(dataset=test_data, batch_size=256, shuffle=True)
    #batch size約50以上(至少為2的倍數)
    return train_loader,test_loader,inputdata,testdata
#%% 這裡為LeＮet 可以用transform learning(EfficientNet)
class CNN(nn.Module):
    def __init__(self):
      super(CNN, self).__init__()
      self.conv1 = nn.Sequential(
        nn.Conv1d(
          in_channels=1,
          out_channels=100,
          kernel_size= 5),
        nn.ReLU()
        )
      self.conv2 = nn.Sequential(
        nn.Conv1d(100,100,10),
        nn.ReLU(),
        nn.MaxPool1d(3)
        )
      self.conv3 = nn.Sequential(
        nn.Conv1d(100,100,10),
        nn.ReLU()
        )
      self.conv4 = nn.Sequential(
        nn.Conv1d(100,160,10),
        nn.ReLU(),
        nn.AvgPool1d(10),
        nn.Dropout(0.5)#資料量如果過大是必要dropout，如果沒有可以把drop變小
        )
      self.fc1 = nn.Linear(480, 100)
      self.activation1 = nn.ReLU()
      self.fc2 = nn.Linear(100, 2)
      
      
    def forward(self, x):
      out = self.conv1(x)
      out = self.conv2(out)
      out = self.conv3(out)
      out = self.conv4(out)
      out = out.view(out.size(0), -1)
#      print(len(out)) 得知fc1 的第一個變數該填多少
      out = self.fc1(out)
      out = self.activation1(out)
      out = self.fc2(out)
      return out

#%%
#train_d,train_t,test_d,test_t = data_prepare.data_loading('train_ecg.csv','train_label_ecg.npy','test_ecg.csv','test_label_ecg.npy')
#train_loader,test_loader = data_prepare.data_package(train_d,train_t,test_d,test_t)
torch.manual_seed(1)
cnn = CNN()
def parameter_use(x,lr = 0.01):
  use_cuda = True
  if use_cuda and torch.cuda.is_available():
    cnn.cuda()
  cnn.load_state_dict(torch.load(x))
  optimizer = torch.optim.Adam(cnn.parameters(), lr = lr)   # optimize all cnn parameters(控制模型學習率的變化)
  loss_func = nn.CrossEntropyLoss() # 已經內涵softmax所以不需要另外加
  return optimizer,loss_func
#%%
def train_testing(w,x,y,z):
  '''
  w : train_loader
  x : loss_func
  y : optimizer
  z : test_loader
  '''
  acc = []
  losses = []
  acces = []
  eval_losses = []
  eval_acces = []
  ys_cnn = []
  yl_cnn = []
  pre = []
  lab = []
#def adjust_learning_rate(optimizer, lr):
#    for param_group in optimizer.param_groups:
#        param_group['lr'] = lr
#    adjust_learning_rate(optimizer, epoch)
  for e in range(1):
    train_loss = 0
    train_acc = 0
#    cnn.train()
#    for im, label in w:
#        if e > 30:
#          lr = 0.00001
#          adjust_learning_rate(optimizer, lr)
#        print(optimizer)
#        if use_cuda and torch.cuda.is_available():
#          im = Variable(im).cuda()
#          label = Variable(label).cuda()
#        # 前向传播
#        out = cnn(im)
#        loss = x(out, label)
#        # 反向传播
#        y.zero_grad()
#        loss.backward()
#        y.step()
        # 记录误差
#        train_loss += loss.item()
        # 计算分类的准确率
#        _, pred = out.max(1)
#        num_correct = (pred == label).sum().item()
#        acc = num_correct / im.shape[0]
#        train_acc += acc
        
    losses.append(train_loss / len(w))
    acces.append(train_acc / len(w))
#    # 在测试集上检验效果
    eval_loss = 0
    eval_acc = 0
    cnn.eval() # 将模型改为预测模式
    for im, label in z:
        if use_cuda and torch.cuda.is_available():
          im = Variable(im).cuda()
          label = Variable(label).cuda()
        out = cnn(im)
#        loss = x(out, label)
        # 记录误差
#        eval_loss += loss.item()
        # 记录准确率
        _, pred = out.max(1)
        num_correct = (pred == label).sum().item()
        acc = num_correct / im.shape[0]
        eval_acc += acc
        ys_cnn.append(out.data.numpy())
        yl_cnn.append(label.cpu().numpy())
        pre.append(pred)
        lab.append(label)
    eval_losses.append(eval_loss / len(z))
    eval_acces.append(eval_acc / len(z))
    print('epoch: {}, Train Loss: {:.6f}, Train Acc: {:.6f}, Eval Loss: {:.6f}, Eval Acc: {:.6f}'
          .format(e, train_loss / len(x), train_acc / len(x), 
                     eval_loss / len(z), eval_acc / len(z)))
#    torch.save(cnn.state_dict(), 'params_cnn_2019_06_22_1_3.pkl')
        
def testing(x,y):
  '''
  x : testdata
  y : model use
  '''
  pred_as = []
  test_output = y(x)
  _, pred = test_output.max(1)
#num_correct = (pred == training_target_).sum().item()
#acc = num_correct / training_use.shape[0]
  pred = pred.numpy()
  pred = torch.max(test_output, 1)[1].data.numpy().squeeze()
#  print(sum(pred==test_t)/len(pred))
  predss = pd.DataFrame(pred)
  pred_as.append(pred)
  return pred