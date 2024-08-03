# -*- coding: utf-8 -*-
"""
Created on Wed Jul 10 15:38:50 2024

@author: hanly2
"""

import pickle
import numpy as np
from fun_h import merge_s, extract_special_voc1, similay_BERT
with open(r'D:\ICSE_2025\邢老师新故事\合并句子\分布式\keyaspect_All.data','rb') as f:
    data_all = pickle.load(f)

#汇总结果
data = {}
s=0
for i in data_all:
    print(s)
    s += 1
    temp = []
    for j in data_all[i]:
        temp.append(j[2])
    res = {}
    if temp != ['']:
        for k in temp:
            for g in k:
                if g in res:
                    if k[g] == []:
                        res[g].append('')
                    else:
                        res[g].append(k[g])
                else:
                    if k[g] == []:
                        res[g] = ['']
                    else:
                        res[g] = [k[g]]
    for j in res:
        res[j] = list(set(res[j]))
        if len(res[j]) > 1 and '' in res[j]:
            res[j].remove('')
                        
        data[i] = res

#打分
#完整度
integrity = {}
for i in data:
    print(i)
    item = data[i]
    s = 0
    for j in item:
        if item[j] != ['']:
            s += 1
    integrity[i] = s/len(item)

#离散程度
dispersion = {}
for i in data:
    print(i)
    item = data[i]
    score = []
    for j in item:
        if len(item[j]) == 1:
            score.append(1)
        else:
            temp = []
            for k in item[j]:
                temp.append(extract_special_voc1(k))
            score.append(similay_BERT(temp))
    dispersion[i] = sum(score)/len(score)
            
                
socre = {}
for i in integrity:
    temp1 = integrity[i]
    if i in dispersion:
        temp2 = dispersion[i]
        score[i] = [temp1,temp2]


with open('score.data','wb') as f:
    pickle.dump([integrity,dispersion],f) 
    
    
    
    
    
    
    
    
    
    
    
    
    
            

