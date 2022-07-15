# -*- coding: utf-8 -*-
"""
Created on Thu May  9 10:45:54 2019

@author: william
"""

#from Wei_datainput import process as pro
#from Wei_datainput import Net as ne
from Wei_datainput_hao import process as pro
from Wei_datainput_hao import CNN
from itertools import chain
import torch.nn as nn
import torch
from torch.autograd import Variable
import matplotlib.pyplot as plt
import random
import datetime
import os

num_epoch=1000
num_output=2
num_input=3
num_hiddenlayer=7

data = []
data_chain = []
site = ['13','14']#少1020

starttime=datetime.datetime.now().strftime("%Y_%m_%d %H:%M:%S")

for i in range(len(site)):
#  data.append(pro.search('C:\\Users\\kylab\\Desktop\\patch_wei\\processeddata'+str(num_input)+'input'+str(num_output)+'output_log\\',site[i]))
    data.append(pro.search('/Users/hao/Desktop/python/act/patch_wei/processeddata'+str(num_input)+'input'+str(num_output)+'output_log/',site[i]))
data_chain = list(chain(*data))
excel_data = pro.excel_input(data_chain)
excel_data_proce = excel_data
use_data = pro.drop_na(excel_data_proce)
#跟家緯不一樣
use_data = use_data[0].rename(index = str,columns={'Unnamed: 0':'index'})
use_data = [use_data.set_index('index')]


#%%
use_data = pro.normal_min_max_scalar(use_data,'score')

#%% do label balance 
sleep_idx=use_data.index[use_data['score'] == 0].tolist()
wake_idx=use_data.index[use_data['score'] == 1].tolist()


if len(sleep_idx)>len(wake_idx):
    randomlist = random.sample(sleep_idx, len(sleep_idx)-len(wake_idx)) 
    use_data=use_data.drop(randomlist)
else:
    randomlist = random.sample(wake_idx, len(wake_idx)-len(sleep_idx)) 
    use_data=use_data.drop(randomlist)
    
sleep_idx=use_data.index[use_data['score'] == 0].tolist()
wake_idx=use_data.index[use_data['score'] == 1].tolist()

training_use,training_target,test_use,testing_target = pro.random_sampling(use_data,'score')
#%%
train_loader,test_loader = pro.tensor_torch(training_use,training_target,test_use,testing_target,100)
#net = ne()
net = CNN()
#net.load_state_dict(torch.load('params_dnn_2019_5_11_output2_5000epoch.pkl'))
criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(net.parameters(), lr = 0.0001) # 使用随机梯度下降，学习率 0.1
#%%
losses = []
acces = []
eval_losses = []
eval_acces = []
ys_dnn = []
yl_dnn = []
pre = []
lab = []
for e in range(num_epoch):
    train_loss = 0
    train_acc = 0
    net.train()
    for im, label in train_loader:
        im, label = im,label
        im = Variable(im)
        label = Variable(label)
        # 前向传播
        out = net(im)
        loss = criterion(out, label)
        # 反向传播
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        # 记录误差
        train_loss += loss.item()
        # 计算分类的准确率
        _, pred = out.max(1)
        num_correct = (pred == label).sum().item()
        acc = num_correct / im.shape[0]
        train_acc += acc
        
    losses.append(train_loss / len(train_loader))
    acces.append(train_acc / len(train_loader))
    # 在测试集上检验效果
    eval_loss = 0
    eval_acc = 0
    net.eval() # 将模型改为预测模式
    for im, label in test_loader:
        im, label = im,label
        im = Variable(im)
        label = Variable(label)
        out = net(im)
        loss = criterion(out, label)
        # 记录误差
        eval_loss += loss.item()
        # 记录准确率
        _, pred = out.max(1)
#        plt.plot(label.numpy(),'.')
#        plt.plot(pred.numpy(),'.')
        num_correct = (pred == label).sum().item()
        acc = num_correct / im.shape[0]
        eval_acc += acc
        ys_dnn.append(out.data.cpu().numpy())
        yl_dnn.append(label.cpu().numpy())
        pre.append(pred)
        lab.append(label)
    eval_losses.append(eval_loss / len(test_loader))
    eval_acces.append(eval_acc / len(test_loader))
    print('epoch: {}, Train Loss: {:.6f}, Train Acc: {:.6f}, Eval Loss: {:.6f}, Eval Acc: {:.6f}'
          .format(e, train_loss / len(train_loader), train_acc / len(train_loader), 
                     eval_loss / len(test_loader), eval_acc / len(test_loader)))
    
    
filename='params_dnn_'+datetime.datetime.now().strftime("%Y_%m_%d")+'_input'+str(num_input)+'_output'+str(num_output)+'_hiddenlayer'+str(num_hiddenlayer)+'_'+str(num_epoch)+'_epoch.pkl'
listcwd=os.listdir(os.getcwd())
if filename in listcwd:
    filename=filename.replace(".pkl","a.pkl")
 
endtime=datetime.datetime.now().strftime("%Y_%m_%d %H:%M:%S") 
    
torch.save(net.state_dict(), filename)


fig_width=5.75
fig_height=2.5
fig_dpi=300
font_size=8
marker_size=3
line_width=0.5
board_color='#222222'
board_width=1
tick_color='#222222'
line_color='#444444'


#plt.subplot(2,1,1)
plt.plot(losses)
#plt.subplot(2,1,2)
#plt.plot(eval_acces)

ax = plt.gca()
#ax.xaxis.grid(which='both') # vertical lines
#plt.ylim((0.1,0.7))
#ax.set_yticks([0.1,0.3,0.5,0.7], minor=False)
ax.spines['top'].set_linewidth(board_width)
ax.spines['top'].set_color(board_color)
ax.spines['bottom'].set_linewidth(board_width)
ax.spines['bottom'].set_color(board_color)
ax.spines['left'].set_linewidth(board_width)
ax.spines['left'].set_color(board_color)
ax.spines['right'].set_linewidth(board_width)
ax.spines['right'].set_color(board_color)


filename='loss_'+datetime.datetime.now().strftime("%Y_%m_%d")+'_input'+str(num_input)+'_output'+str(num_output)+'_'+str(num_epoch)+'_epoch.png'
if filename in listcwd:
    filename=filename.replace(".png","a.png")
plt.savefig(filename,bbox_inches='tight',dpi =fig_dpi)
plt.close('all')
