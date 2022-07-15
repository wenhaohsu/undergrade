#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 25 23:21:22 2020

@author: hao
"""

import pandas as pd
import os
import matplotlib.pyplot as plt
import numpy as np
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()
import itertools
from sklearn.metrics import roc_curve,roc_auc_score,confusion_matrix,accuracy_score,cohen_kappa_score,precision_score
#%%

def sleep_wake_act2(posture,activity):
    state=[]
    lie_act=[]       
    conscious=[]
    for i in range(len(posture)):
        if posture[i]==5:
            state.append(2)
        else:
            state.append(1)
            lie_act.append(activity[i])
    threshold=np.median(lie_act)+0.2*np.std(lie_act)
    for i in range(len(activity)):
        if activity[i]>= threshold:
            conscious.append(1)
        else:
            conscious.append(0)
    return conscious

def sleep_wake_act3(posture,activity):
    state=[]
    lie_act=[]       
    conscious=[]
    for i in range(len(posture)):
        if posture[i]==5:
            state.append(2)
        else:
            state.append(1)
            lie_act.append(activity[i])
    #threshold=np.median(lie_act)+0.2*np.std(lie_act)
    threshold=np.median(lie_act)+0.2*np.std(lie_act)
    for i in range(len(activity)):
        if activity[i]>= threshold:
            conscious.append(1)
        else:
            conscious.append(0)
    return threshold

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

def getstate_filter(state,window_size):#window_size決定你的過濾窗格大小，使用奇數
    window=[]
    state_len=window_size+1
    window_epoch=window_size//2
    for i in range(len(state)):
        if i < window_size or i > len(state)-state_len:
            window.append(1)
        else:
            state_sum=sum(state[i-window_epoch:i+window_epoch]) 
            if state_sum>=window_epoch:
                window.append(1)
            else:
                window.append(0)
    return window 

def multi_filter(post,act):
    layer1=3
    window=2
    layer2=layer1+window  
    layer3=layer2+window
    layer4=layer3+window
    layer5=layer4+window
    unfilter=sleep_wake_act2(post,act)
    first_layer=getstate_filter(unfilter,layer1)
    second_layer=getstate_filter(first_layer,layer2)
    third_layer=getstate_filter(second_layer,layer3)
    fourth_layer=getstate_filter(third_layer,layer4)
    fifth_layer=getstate_filter(fourth_layer,layer5)
    return unfilter,first_layer,second_layer,third_layer,fourth_layer,fifth_layer

def plot_confusion_matrix(cm, classes,normalize=True,
                          title='Confusion matrix',
                          cmap=plt.cm.binary,
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

def filter_wake_sleep(x,y,threshold):
    output=[]
    for i in range(len(x)):
        if x[i]>threshold and y[i]==0:
            output.append(threshold - 0.1)
        elif x[i]<threshold and y[i]==1:
            output.append(threshold +0.1)
        else:
            output.append(x[i])
    return output
#%%
path='/Users/hao/Desktop/python/sleep_data_process/2_stage/health_2'
lista = os.listdir(path)
Score_list=[]
Score_len=[]
act_list=[]
act_len=[]
Time_list=[]
Post_list=[]
Post_len=[]
lie_list=[]
stand_list=[]
multi_layer_list=[]
for i in range(len(lista)):
    if('.xls' in lista[i]):
        sheet=pd.read_excel(path+'/'+lista[i],sheet_name='whole data')
        sheet=sheet.dropna(axis=0, how='any')
        Score=list(map(int,sheet['Score']))
        act=sheet['act'].tolist()
        Time=sheet['Time'].tolist()
        Pre_post=sheet['post'].tolist()
        Post=state(Pre_post)
        TD1=sleep_wake_score(Score)
        multi_layer=multi_filter(sheet['post'],sheet['act'])
        Score_list.append(TD1)
        Score_len+=TD1
        Post_len+=Post
        Post_list.append(Post)
        act_len+=act
        act_list.append(act)
        Time_list.append(Time)
        multi_layer_list.append(multi_layer)

multi_layer_len=multi_filter(Post_len,act_len)

'''confusion matrix'''
my_yticks1 = ["Sleep","Wake"]
fig2=plt.figure(figsize=(20,20))
fig2.add_subplot(2,3,1)
plot_confusion_matrix(confusion_matrix(Score_len,multi_layer_len[0]),classes=my_yticks1,
                      title='Unfiltered activity',ylabel=True)
fig2.add_subplot(2,3,2)
plot_confusion_matrix(confusion_matrix(Score_len,multi_layer_len[1]),classes=my_yticks1,
                      title='The 1st layer')
fig2.add_subplot(2,3,3)
plot_confusion_matrix(confusion_matrix(Score_len,multi_layer_len[2]), classes=my_yticks1,
                      title="The 2nd layer")
fig2.add_subplot(2,3,4)
plot_confusion_matrix(confusion_matrix(Score_len,multi_layer_len[3]),classes=my_yticks1,
                      title="The 3rd layer",ylabel=True,xlabel=True)
fig2.add_subplot(2,3,5)
plot_confusion_matrix(confusion_matrix(Score_len,multi_layer_len[4]),classes=my_yticks1,
                      title="The 4th layer",xlabel=True)
fig2.add_subplot(2,3,6)
plot_confusion_matrix(confusion_matrix(Score_len,multi_layer_len[5]),classes=my_yticks1,
                      title="The 5th layer",xlabel=True)
plt.suptitle('Title')
plt.tight_layout()

get_accuracy=[accuracy_score(Score_len,multi_layer_len[i]) for i in range(len(multi_layer_len))]
get_kappa=[cohen_kappa_score(Score_len,multi_layer_len[i]) for i in range(len(multi_layer_len))]

'''AUROC curve'''
threshold_wake=sleep_wake_act3(Post_len,act_len)
convert=[filter_wake_sleep(act_len,multi_layer_len[i],threshold_wake) for i in range(len(multi_layer_len))]
tpr_list=[]
fpr_list=[]
for i in range(len(multi_layer_len)):
    fpr,tpr,_=roc_curve(Score_len,convert[i])
    tpr_list.append(tpr)
    fpr_list.append(fpr)
roc_auc=[roc_auc_score(Score_len,multi_layer_len[i],average='weighted') for i in range(len(multi_layer_len))]
''' plot auc for multilayer'''
fig3=plt.figure(figsize=(20,20))
plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
plt.plot(fpr_list[0], tpr_list[0],label='Unfilter activity (AUC = %0.2f)' % roc_auc[0],color='k')
plt.plot(fpr_list[1], tpr_list[1],label='1st layer (AUC = %0.2f)' % roc_auc[1],color='k',linestyle='--')
plt.plot(fpr_list[2], tpr_list[2],label='2nd layer (AUC = %0.2f)' % roc_auc[2],color='k',linestyle='-.')
plt.plot(fpr_list[3], tpr_list[3],label='3rd layer (AUC = %0.2f)' % roc_auc[3],color='k',linestyle=':')
plt.plot(fpr_list[4], tpr_list[4],'.',label='4th layer (AUC = %0.2f)' % roc_auc[4],color='k',linestyle='--')
plt.plot(fpr_list[5], tpr_list[5],'*',label='5th layer (AUC = %0.2f)' % roc_auc[5],color='k',linestyle='--')
plt.legend(loc="lower right",fontsize=12)
plt.xlim(0,1)
plt.xlabel('False Positive Rate',fontname="Arial",fontsize=20)
plt.xticks(fontname="Arial",fontsize=16)
plt.ylim(0,1)
plt.ylabel('True Positive Rate',fontname="Arial",fontsize=20)

plt.yticks(fontname="Arial",fontsize=16)
plt.show()
#%% machine laerning
from sklearn.model_selection  import train_test_split
#act_train,act_test,Score_train,Score_test=train_test_split(np.array(act_len),np.array(Score_len),test_size=0.2,random_state=0)
act_train,_,Score_train,_=train_test_split(np.array(act_len),np.array(Score_len),test_size=0.2,random_state=0)
test=pd.read_excel(path+'/'+lista[16],sheet_name='whole data')
test.dropna(inplace=True)
act_train=act_train.reshape(-1, 1)
#act_test=act_test.reshape(-1, 1)
score_train=Score_train.T.ravel()
#score_test=Score_test.T.ravel()
act_test=np.array(test['act']).reshape(-1, 1)
score_test=np.array(test['Score']).T.ravel()

#%% logistic regression

from sklearn.linear_model import LogisticRegression
lr=LogisticRegression(solver='liblinear')
lr=lr.fit(act_train,score_train)
lr_predictions = lr.predict(act_test)
lr_accuracy = lr.score(act_test,score_test)
#lr_roc_auc = roc_auc_score(score_test, lr_predictions,average='weighted')#損失的預測值
#lr_score = lr.decision_function(act_test.reshape(-1, 1))
#fpr_lr, tpr_lr,_ = roc_curve(score_test, lr.predict_proba(act_test)[:,1])
#fpr_lr, tpr_lr,_ = roc_curve(score_test.ravel(),lr_score.ravel())
#%% Decision tree 跟SVM的結果一樣，但跑速較快
from sklearn.tree import DecisionTreeClassifier
tr = DecisionTreeClassifier()  # 決策樹模型
tr.fit(act_train,score_train)
tr_predictions = tr.predict(act_test)
#tr_accuracy = tr.score(act_test,score_test)
#tr_roc_auc = roc_auc_score(score_test, tr_predictions,average='weighted')
#fpr_tr, tpr_tr,_ = roc_curve(score_test, tr.predict_proba(act_test)[:,1])

#test['pre_lr']=lr_predictions
#test['pre_svm']=tr_predictions
#test.to_excel(str(test['Time'][0])[0:10]+"predict.xlsx",
#              sheet_name='whole data')
#%% ANN model
#path2='/Users/hao/Desktop/python/sleep_data_process/2_stage/'
#ann=pd.read_excel(path2+'/'+'05_26_1000_epoch_output.xlsx',sheet_name='predict_output')
#ann_act=np.array(ann['ACT'])
#ann_score=np.array(ann['score'])
#ann_predict=np.array(ann['predict'])
#ann_roc_auc = roc_auc_score(ann_score,ann_predict,average='weighted')
#fpr_ann, tpr_ann,_=roc_curve(ann_score,ann_act)


#%% confusion matrix for all method
#fig4=plt.figure(figsize=(20,20))
#fig4.add_subplot(2,2,1)
#plot_confusion_matrix(confusion_matrix(Score_len,multi_layer_len[5]),classes=my_yticks1,
#                      title="The proposed method",ylabel=True)
#fig4.add_subplot(2,2,2)
#plot_confusion_matrix(confusion_matrix(score_test,lr_predictions),classes=my_yticks1,
#                      title='Logistic regression')
#fig4.add_subplot(2,2,3)
#plot_confusion_matrix(confusion_matrix(score_test,tr_predictions),classes=my_yticks1,
#                      title='Support vector machine',xlabel=True,ylabel=True)
#fig4.add_subplot(2,2,4)
#plot_confusion_matrix(confusion_matrix(ann_score,ann_predict),classes=my_yticks1,
#                      title="Artificial neural network",xlabel=True)
##plt.tight_layout()
##%% ROC curve for all method
#fig5=plt.figure(figsize=(20,20))
#plt.plot(fpr_list[5], tpr_list[5],label='The proposed method (AUC = %0.2f)' % roc_auc[5],color='k')
#plt.plot(fpr_lr, tpr_lr, label='Logistic regression (AUC = %0.2f)' % lr_roc_auc,color='k',linestyle='--')
#plt.plot(fpr_tr, tpr_tr, label='Support vector machine (AUC = %0.2f)' % tr_roc_auc,color='k',linestyle='-.')
##plt.plot(fpr_tr,tpr_tr, label='Decision tree (area = %0.2f)' % tr_roc_auc)
#plt.plot(fpr_ann, tpr_ann, label='Artificial neural network (AUC = %0.2f)' % ann_roc_auc,color='k',linestyle=':')
#plt.plot([0, 1], [0, 1],'r--')
#plt.xlim([0.0, 1.0])
#plt.ylim([0.0, 1.0])
#plt.xlabel('False Positive Rate',fontname="Arial",fontsize=20)
#plt.xticks(fontname="Arial",fontsize=16)
#plt.ylabel('True Positive Rate',fontname="Arial",fontsize=20)
#plt.yticks(fontname="Arial",fontsize=16)
##plt.title('ROC curve',fontname="Arial",fontsize=24)
#plt.legend(loc="lower right",fontsize=12)
#plt.show()
#%% PR curve for our method
#from sklearn.metrics import precision_recall_curve
#from sklearn.metrics import f1_score
#
#precision_list=[]
#recall_list=[]
#for i in range(len(multi_layer_len)):
#    precision, recall, _ =precision_recall_curve(Score_len,convert[i])
#    precision_list.append(precision)
#    recall_list.append(recall)
#f1=[f1_score(Score_len,multi_layer_len[i],average='weighted') for i in range(len(multi_layer_len))]
#fig6=plt.figure(figsize=(20,20))
#plt.plot([0, 1], [1, 0], color='navy', lw=2, linestyle='--')
#plt.plot(precision_list[0], recall_list[0],label='Unfilter activity (F1-score = %0.2f)' % f1[0],color='k')
#plt.plot(precision_list[1], recall_list[1],label='1st layer (F1-score = %0.2f)' % f1[1],color='k',linestyle='--')
#plt.plot(precision_list[2], recall_list[2],label='2nd layer (F1-score = %0.2f)' % f1[2],color='k',linestyle='-.')
#plt.plot(precision_list[3], recall_list[3],label='3rd layer (F1-score = %0.2f)' % f1[3],color='k',linestyle=':')
#plt.plot(precision_list[4], recall_list[4],'.',label='4th layer (F1-score = %0.2f)' % f1[4],color='k',linestyle='--')
#plt.plot(precision_list[5], recall_list[5],'*',label='5th layer (F1-score = %0.2f)' % f1[5],color='k',linestyle='--')
##plt.plot([0,1], [1,0],'r--')
#plt.xlim([0.0, 1.0])
#plt.ylim([0.0, 1.0])
#plt.xticks(fontname="Arial",fontsize=16)
#plt.xlabel('Recall',fontname="Arial",fontsize=20)
#plt.yticks(fontname="Arial",fontsize=16)
#plt.ylabel('Precision',fontname="Arial",fontsize=20)
#plt.legend(loc="lower left",fontsize=12)
#plt.show()
#%% PR curve for all method

#precision, recall, _ = precision_recall_curve(Score_len,convert[5])
#precision_lr,recall_lr,_=precision_recall_curve(score_test,lr.predict_proba(act_test)[:,1])
#precision_tr,recall_tr,_=precision_recall_curve(score_test,tr.predict_proba(act_test)[:,1])
#precision_ann, recall_ann,_=precision_recall_curve(ann_score,ann_act)
##f1=f1_score(Score_len,multi_layer_len[i],average='weighted')
#f1_lr=f1_score(ann_score,ann_predict,average='weighted')
#f1_tr=f1_score(score_test, tr_predictions,average='weighted')
#f1_ann=f1_score(ann_score,ann_predict,average='weighted')
#fig7=plt.figure(figsize=(20,20))
#plt.plot(precision, recall,label='The proposed method (F1-score = %0.2f)' % f1[5],color='k')
#plt.plot(precision_lr,recall_lr,label='Logistic regression (F1-score = %0.2f)' % f1_lr,color='k',linestyle='--')
#plt.plot(precision_tr,recall_tr,label='Support vector machine (F1-score = %0.2f)' % f1_tr,color='k',linestyle='-.')
#plt.plot(precision_ann, recall_ann, label='Artificial neural network (F1-score = %0.2f)' % f1_ann,color='k',linestyle=':')
#plt.plot([0,1], [1,0],'r--')
#plt.xlim([0.0, 1.0])
#plt.ylim([0.0, 1.0])
#plt.xticks(fontname="Arial",fontsize=16)
#plt.xlabel('Recall',fontname="Arial",fontsize=20)
#plt.yticks(fontname="Arial",fontsize=16)
#plt.ylabel('Precision',fontname="Arial",fontsize=20)
#plt.legend(loc="lower left",fontsize=12)
#plt.show()

#%%
#precision_list=[precision_score(Score_len,multi_layer_len[i],average='weighted') for i in range(len(multi_layer_len))]
#print(precision_list)
#precision_LR=precision_score(score_test,lr_predictions,average='weighted')
#precision_SVM=precision_score(score_test,tr_predictions,average='weighted')
#precision_ANN=precision_score(ann_score,ann_predict,average='weighted')
#print(precision_LR)
#print(precision_SVM)
#print(precision_ANN)