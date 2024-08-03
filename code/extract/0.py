

import pickle
import numpy as np
from fun_h import generate_prompt, ask_LLM, regular, count_repeating_letters,find_similay_keyaspect_type,\
    judge_include, count_repeated_words, re_verfy, CWE_Score_LLM, retrieve_wiki_records, \
        NET_Score_LLM
import time

with open('all.data','rb') as f:
    data_all = pickle.load(f)
data_all = dict(sorted(data_all.items(), key=lambda d: d[0], reverse=True))

def extract(text, lang):
   

    ext_pro = generate_prompt(text, lang)
    ext_res = ask_LLM(ext_pro)
    ext_dir = regular(ext_res)[-1]
    ext_dir = find_similay_keyaspect_type(ext_dir)
    res = []
    for i in ext_dir:
        if ext_dir[i] != [] and i != 'attected product':
            res.append([i, judge_include(text, ext_dir[i])])
        else:
            res.append([i, True])
    
    res_list = [i[1] for i in res]
    if False in res_list:
        for attempt in range(5): 
            ext_pro1 = generate_prompt(text, lang)
            ext_res1 = ask_LLM(ext_pro1)
            ext_dir1 = regular(ext_res1)[-1]
            ext_dir1 = find_similay_keyaspect_type(ext_dir1)
            
            indices_of_false = [index for index, value in enumerate(res_list) if not value]
            
            for index in indices_of_false:
                key = res[index][0]
                if ext_dir1[key] != [] and judge_include(text, ext_dir1[key]):
                    ext_dir[key] = ext_dir1[key]
                    res[index][1] = True  
                else:
                    ext_dir[key] = []
            
            res_list = [i[1] for i in res]
            if not False in res_list:
                break  
    
    return ext_dir

def split_dict_into_five_parts(data,n):
    keys = list(data.keys())
    total_keys = len(keys)
    chunk_size = total_keys // n
    remainder = total_keys % n
    
    chunks = []
    start = 0
    
    for i in range(n):
        end = start + chunk_size + (1 if i < remainder else 0)
        chunk = {key: data[key] for key in keys[start:end]}
        chunks.append(chunk)
        start = end
    
    return chunks

n = 36
sub_dicts = split_dict_into_five_parts(data_all, n)
data_all = sub_dicts[0]




data_2023_keyaspect = {}
s= 0
keys = list(data_all.keys())
while s < len(data_all):
    s += 1
    # try:
    i = keys[s]

    if '-' in i:
        print(s)
        temp=[]
        for j in data_all[i]:
            if j[0] == '':
                temp.append([j[0],j[1],''])
            else:

                keyaspect = extract(j[0],j[1])
                temp.append([j[0],j[1],keyaspect])
        data_2023_keyaspect[i] = temp
        if s%10==1:
            print('：', s)
            with open('data0.data','wb') as f:
                pickle.dump(data_2023_keyaspect,f)   

































