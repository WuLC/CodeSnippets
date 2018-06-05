# -*- coding: utf-8 -*-
# Created on Tue May 22 2018 14:35:23
# Author: WuLC
# EMail: liangchaowu5@gmail.com

import gc
import random
import visdom
import fire
import pandas as pd
import numpy as np
from sklearn import preprocessing
from sklearn.feature_extraction import FeatureHasher

DATA_DIR = '/mnt/e/dataset/criteo/'

def pos_neg_count():
    train_file = DATA_DIR + 'train.txt'
    train_samples = 1200000 # 4500000  # 3000000 # 150000
    val_samples = 160000    # 600000     # 400000  # 20000
    pos_count, neg_count = 0, 0
    with open(train_file, mode='r', encoding='utf8') as rf:
        for line in rf:
            label = int(line.split('\t')[0])
            if label == 1:
                pos_count += 1
            elif label == 0:
                neg_count += 1
            else:
                print('unknown label')
            if pos_count + neg_count > train_samples+val_samples:
                break

    print(pos_count, neg_count, pos_count/(pos_count+neg_count)) 
    # ALL       11745438 34095179 0.2562233837297609
    # 10000000  2512069  7487932  0.25120687487931254
    # 1000000   254949 745052     0.2549487450512549


def hash_size_of_cate_feature(train_file, val_file, max_hash_size = 1000000):
    cate_set = [set() for _ in range(26)]
    with open(train_file, mode='r', encoding='utf8') as rf:
        for line in rf:
            blocks = line.rstrip('\n').split(',') # line.strip().split('\t) will cause error
            for i in range(14, 40):
                cate_set[i-14].add(blocks[i])

    with open(val_file, mode='r', encoding='utf8') as rf:
        for line in rf:
            blocks = line.rstrip('\n').split(',') # line.strip().split('\t) will cause error
            for i in range(14, 40):
                cate_set[i-14].add(blocks[i])
    unique_count = [len(s) for s in cate_set]
    hash_size = []
    for i in range(len(unique_count)):
        hs = 10
        while hs < unique_count[i] and hs < max_hash_size:
            hs <<= 1
        hash_size.append(hs)
    return hash_size
    """
    unique_count = [1460, 583, 10131227, 2202608, 305, 24, 12517, 633, 3, 93145, 5683, 8351593, 3194, 27, 
    14992, 5461306, 10, 5652, 2173, 4, 7046547, 18, 15, 286181, 105, 142572]
    """


def generate_smaller_training_file(normalize_continous_value = True):
    train_samples = 1200000 # 4500000  # 3000000 # 150000
    val_samples = 160000    # 600000     # 400000  # 20000
    count = 0
    train_file = DATA_DIR + 'train.txt'
    sub_train_file = DATA_DIR + 'sub_train_{0}.txt'.format(train_samples)
    sub_val_file = DATA_DIR + 'sub_val_{0}.txt'.format(val_samples)
    
    # min_max normalization for continous value
    if normalize_continous_value:
        continous_value = []
        count = 0
        with open(train_file, mode='r', encoding='utf8') as rf:
            for line in rf:
                count += 1
                if count > train_samples + val_samples:
                    break
                blocks = line.rstrip('\n').split('\t')
                tmp = []
                for i in range(1, 14):
                    if len(blocks[i]) > 0:
                        tmp.append(float(blocks[i]))
                    else:
                        tmp.append(0)
                continous_value.append(tmp)
        min_max_scaler = preprocessing.MinMaxScaler()
        continous_scaled = min_max_scaler.fit_transform(np.array(continous_value))
        print('===========finish min-max scaling=============')

    count = 0
    with open(train_file, encoding='utf8', mode='r') as rf:
        with open(sub_train_file, encoding='utf8', mode='w') as twf:
            with open(sub_val_file, encoding='utf8', mode='w') as vwf:
                for line in rf:
                    count += 1
                    if count > train_samples + val_samples:
                        break
                    blocks = line.rstrip('\n').split('\t')
                    if normalize_continous_value:
                        content = ','.join(blocks[:1]+ 
                                           list(map(lambda x:str(x), continous_scaled[count-1]))+
                                           blocks[14:])+'\n'
                    else:
                        content = ','.join(blocks)+'\n'
                    if count <= train_samples:
                        twf.write(content)
                    elif count <= train_samples + val_samples:
                        vwf.write(content)


def remove_label(src_file, target_file):
    with open(target_file, mode='w', encoding='utf8') as wf:
        with open(src_file, mode='r', encoding='utf8') as rf:
            for line in rf:
                blocks = line.split(' ')
                wf.write(' '.join(blocks[1:]))


def generate_data_for_fm():
    train_samples = 1200000 # 4500000  # 3000000 # 150000
    val_samples = 160000    # 600000     # 400000  # 20000
    sub_train_file = DATA_DIR + 'fm_sub_train_{0}.txt'.format(train_samples)
    sub_val_file = DATA_DIR + 'fm_sub_val_{0}.txt'.format(val_samples)
    no_label_sub_train_file = DATA_DIR + 'fm_sub_train_{0}_no_label.txt'.format(train_samples)
    train_file = DATA_DIR + 'sub_train_{0}.txt'.format(train_samples)
    val_file = DATA_DIR + 'sub_val_{0}.txt'.format(val_samples)
    hash_size = hash_size_of_cate_feature(train_file, val_file, max_hash_size = 1000000)
    print('total hash size {0}'.format(sum(hash_size)))
    def transform(src_file, des_file):
        continous_value = []
        with open(src_file, mode='r', encoding='utf8') as rf:
            for line in rf:
                blocks = line.split(',')
                tmp = []
                for i in range(1, 14):
                    if len(blocks[i]) > 0:
                        tmp.append(float(blocks[i]))
                    else:
                        tmp.append(0)
                continous_value.append(tmp)
        
        # min_max scale for continous value
        min_max_scaler = preprocessing.MinMaxScaler()
        continous_scaled = min_max_scaler.fit_transform(np.array(continous_value))
        print('===========finish min-max scaling=============')

        # one-hot for categorical value
        feature_size = [1 for _ in range(13)] + hash_size
        accu_size = []
        curr = 0
        for i in range(len(feature_size)):
            curr += feature_size[i]
            accu_size.append(curr)

        count = 0
        missed_value = 'missed'
        with open(des_file, mode='w', encoding='utf8') as wf:
            with open(src_file, mode='r', encoding='utf8') as rf:
                for line in rf:
                    blocks = line.rstrip('\n').split(',')
                    # construct data for ffm
                    tmp = [blocks[0]] # label
                    tmp.extend(['{0}:{1}'.format(accu_size[j], continous_scaled[count][j]) for j in range(13) if continous_scaled[count][j] != 0]) # continous  feature
                    # ont-hot feature
                    for i in range(14, 40):
                        value = missed_value if len(blocks[i]) == 0 else blocks[i]
                        idx = hash(value)%hash_size[i-14]
                        tmp.append('{0}:{1}'.format(accu_size[i-2]+idx, 1))
                    wf.write(' '.join(tmp) + '\n')
                    count += 1
    transform(val_file, sub_val_file)
    gc.collect()
    transform(train_file, sub_train_file)
    remove_label(sub_train_file, no_label_sub_train_file)


def generate_data_for_ffm():
    train_samples = 4500000   #3000000 #150000
    val_samples = 600000 #400000 # 20000   
    sub_train_file = DATA_DIR + 'ffm_sub_train_{0}.txt'.format(train_samples)
    sub_val_file = DATA_DIR + 'ffm_sub_val_{0}.txt'.format(val_samples)
    no_label_sub_train_file = DATA_DIR + 'ffm_sub_train_{0}_no_label.txt'.format(train_samples)
    train_file = DATA_DIR + 'sub_train_{0}.txt'.format(train_samples)
    val_file = DATA_DIR + 'sub_val_{0}.txt'.format(val_samples)
    hash_size = hash_size_of_cate_feature(train_file, val_file)

    def transform(src_file, des_file):
        continous_value = []
        with open(src_file, mode='r', encoding='utf8') as rf:
            for line in rf:
                blocks = line.split(',')
                tmp = []
                for i in range(1, 14):
                    if len(blocks[i]) > 0:
                        tmp.append(float(blocks[i]))
                    else:
                        tmp.append(0)
                continous_value.append(tmp)
        
        # min_max scale for continous value
        min_max_scaler = preprocessing.MinMaxScaler()
        continous_scaled = min_max_scaler.fit_transform(np.array(continous_value))
        print('===========finish min-max scaling=============')

        # one-hot for categorical value
        count = 0
        missed_value = 'missed'
        with open(des_file, mode='w', encoding='utf8') as wf:
            with open(src_file, mode='r', encoding='utf8') as rf:
                for line in rf:
                    blocks = line.rstrip('\n').split(',')
                    # construct data for ffm
                    tmp = [blocks[0]] # label
                    tmp.extend(['{}:{}:{}'.format(j+1, 0, continous_scaled[count][j]) for j in range(13)]) # continous  feature
                    # ont-hot feature
                    for i in range(14, 40):
                        value = missed_value if len(blocks[i]) == 0 else blocks[i]
                        idx = hash(value)%hash_size[i-14]
                        tmp.append('{0}:{1}:{2}'.format(i, idx, 1))
                    wf.write(' '.join(tmp) + '\n')
                    count += 1
    transform(val_file, sub_val_file)
    gc.collect()
    transform(train_file, sub_train_file)
    remove_label(sub_train_file, no_label_sub_train_file)


def test_visdom():
    vis = visdom.Visdom(env='test')
    title = 'testing'
    n = 10
    train_auc = [random.randint(1, 10)*0.01 for _ in range(n)]
    val_auc = [random.randint(1, 10)*0.01 for _ in range(n)]
    x_epoch = list(range(n+1))
    t_auc = dict(x=x_epoch, y=train_auc, type='custom', name='train_auc')
    v_auc = dict(x=x_epoch, y=val_auc, type='custom', name='val_auc')
    layout=dict(title=title, xaxis={'title':'epochs'}, yaxis={'title':'auc&loss'})
    data = [t_auc, v_auc]
    vis._send({'data':data, 'layout':layout, 'win':title})

if __name__ == '__main__':
    fire.Fire()