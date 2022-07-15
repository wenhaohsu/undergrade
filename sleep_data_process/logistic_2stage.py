#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 22 23:35:10 2020

@author: hao
"""

import pandas as pd
import os
import matplotlib.pyplot as plt
import numpy as np
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()
import itertools
from sklearn.metrics import roc_curve,roc_auc_score
from sklearn.metrics import confusion_matrix,accuracy_score,cohen_kappa_score
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection  import train_test_split
from sklearn.feature_selection import f_regression
from sklearn.linear_model import LogisticRegression
#%%
def sleep_wake_score(score):
    conscious=[]
    for i in range(len(score)):
        if score[i] == 5:
            conscious.append(1)
        else:
            conscious.append(0)
    return conscious

def state(post):
    get_state=[]
    for i in range(len(post)):
        if post[i] == 5:
            get_state.append(2)
        else:
            get_state.append(1)
    return get_state

def plot_confusion_matrix(cm, classes,normalize=True,
                          title='Confusion matrix',
                          cmap=plt.cm.Blues,
                          fontname="Arial",
                          xlabel=False,ylabel=False):
    if normalize:
        cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
    plt.imshow(cm, interpolation='nearest', cmap=cmap)
    plt.title(title,fontname='Arial',fontsize=18)
    tick_marks = np.arange(len(classes))
    plt.xticks(tick_marks, classes,fontsize=14)
    plt.yticks(tick_marks, classes,fontsize=14)
    fmt = '.2f' if normalize else 'd'
    thresh = cm.max() / 2.
    for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
        plt.text(j, i, format(cm[i, j], fmt),fontsize=14,
                 horizontalalignment="center",
                 color="white" if cm[i, j] > thresh else "black")
    plt.xlim(-0.5,len(classes)-0.5)
    plt.ylim(len(classes)-0.5,-0.5)
    plt.tick_params(axis='both',which='both',bottom=False,top=False,length = 0)
    if ylabel:
        plt.ylabel('Scored by TD1',fontname="Arial",fontsize=16)
    if xlabel:
        plt.xlabel('Scored by algorithm',fontname="Arial",fontsize=16)
#%%
path='/Users/hao/Desktop/python/sleep_data_process/2_stage/health'
lista = os.listdir(path)
Score_list=[]
Score_len=[]
act_list=[]
act_len=[]
HR_list=[]
HR_len=[]
Time_list=[]
Post_list=[]
Post_len=[]
lie_list=[]
stand_list=[]
multi_layer_list=[]
for i in range(len(lista)):
    if('.xls' in lista[i]):
#        xls=pd.ExcelFile(path+'/'+lista[i])
#        sheet=xls.parse('whole data')
        sheet=pd.read_excel(path+'/'+lista[i],sheet_name='whole data')
        sheet=sheet.dropna(axis=0, how='any')
        Score=list(map(int,sheet['Score']))
        act=np.array(sheet['act']).tolist()
        HR=np.array(sheet['HR']).tolist()
        Time=sheet['Time'].tolist()
        Pre_post=sheet['post'].tolist()
        Post=state(Pre_post)
        TD1=sleep_wake_score(Score)
        Score_list.append(TD1)
        Score_len+=TD1
        Post_len+=Post
        Post_list.append(Post)
        act_len+=act
        act_list.append(act)
        HR_len+=HR
        HR_list.append(HR)
        Time_list.append(Time)
act_len=np.array(act_len)
Score_len=np.array(Score_len)
Post_len=np.array(Post_len)
HR_len=np.array(HR_len)
#%%
#x=np.vstack([act_len,HR_len])
#act_train,act_test,Score_train,Score_test=train_test_split(x.T,Score_len,test_size=0.2,random_state=0) #random_state 種子值
act_train,act_test,Score_train,Score_test=train_test_split(act_len,Score_len,test_size=0.2,random_state=0)
#%%
act_train=act_train.reshape(-1, 1)
act_test=act_test.reshape(-1, 1)
score_train=Score_train.T.ravel()
score_test=Score_test.T.ravel()
sc=StandardScaler()
sc.fit(act_train)
act_train_nor=sc.transform(act_train)
act_test_nor=sc.transform(act_test)
#%%LogisticRegression


lr=LogisticRegression(solver='liblinear') #solver:消除警告的方法
#lr=lr.fit(act_train_nor,score_train)      #ravel:不規範模式  
lr=lr.fit(act_train,score_train)
#print(lr.coef_)# 印出係數
#print(lr.intercept_ )# 印出截距
#print(f_regression(act_train_nor,score_train)[1])# 印出p_value

predictions = lr.predict(act_test)
accuracy = lr.score(act_test_nor,Score_test)

my_yticks1 = ["Sleep","Wake"]
plot_confusion_matrix(confusion_matrix(score_test,predictions),classes=my_yticks1,
                      title='Unfiltered activity',ylabel=True)
#%%
from matplotlib.colors import ListedColormap
def plot_decision_regions(X, y, classifier, test_idx=None, resolution=0.02):

    # setup marker generator and color map
    markers = ('s', 'x', 'o', '^', 'v')
    colors = ('red', 'blue', 'lightgreen', 'gray', 'cyan')
    cmap = ListedColormap(colors[:len(np.unique(y))])

    # plot the decision surface
    x1_min, x1_max = X[:, 0].min() - 1, X[:, 0].max() + 1
    x2_min, x2_max = X[:, 1].min() - 1, X[:, 1].max() + 1
    xx1, xx2 = np.meshgrid(np.arange(x1_min, x1_max, resolution),
                           np.arange(x2_min, x2_max, resolution))
    Z = classifier.predict(np.array([xx1.ravel(), xx2.ravel()]).T)
    Z = Z.reshape(xx1.shape)
    plt.contourf(xx1, xx2, Z, alpha=0.4, cmap=cmap)
    plt.xlim(xx1.min(), xx1.max())
    plt.ylim(xx2.min(), xx2.max())

    for idx, cl in enumerate(np.unique(y)):
        plt.scatter(x=X[y == cl, 0], 
                    y=X[y == cl, 1],
                    alpha=0.6, 
                    c=cmap(idx),
                    edgecolor='black',
                    marker=markers[idx], 
                    label=cl)

    # highlight test samples
    if test_idx:
        # plot all samples
        X_test, y_test = X[test_idx, :], y[test_idx]

        plt.scatter(X_test[:, 0],
                    X_test[:, 1],
                    c='',
                    alpha=1.0,
                    edgecolor='black',
                    linewidths=1,
                    marker='o',
                    s=55, label='test set')
fig1=plt.figure(figsize=(20,20))
#plot_decision_regions(act_test,score_test, classifier=lr)
#plt.legend(loc='upper left')
#plt.tight_layout()
#plt.show()
#%%
fig2=plt.figure(figsize=(20,20))
lr_roc_auc = roc_auc_score(score_test, lr.predict(act_test))
fpr, tpr, thresholds = roc_curve(score_test, lr.predict_proba(act_test)[:,1])
plt.plot(fpr, tpr, label='Logistic Regression (area = %0.2f)' % lr_roc_auc)
plt.plot([0, 1], [0, 1],'r--')
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.0])
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('Receiver operating characteristic')
plt.legend(loc="lower right")
plt.show()
#%%
