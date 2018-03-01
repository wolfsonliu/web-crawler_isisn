# -*- coding: utf-8 -*-
"""
Created on Mon Jan 22 09:23:59 2018

@author: lib
"""
import pandas as pd
import csv

with open('good.csv', 'wb') as good:
    with open('bad.csv', 'wb') as bad:
        with open('dqkxjj2017.csv', 'rb') as f:
            for line in f:
                if len(line.decode('utf-8').split(',')) != 11:
                    bad.write(line)
                else:
                    good.write(line)

tmp = pd.read_csv('./good.csv', header=None, quoting=csv.QUOTE_ALL)
tmp.index = tmp[3]
tmp.columns = ['year','grant','sub','num','id','subject','title','author','school','money','dueration']
tmp.sort_index().to_csv('./data/diqukexuejijin2017.csv', index=False, encoding='utf-8')



with open('good.csv', 'wb') as good:
    with open('bad.csv', 'wb') as bad:
        with open('qnkxjj2017.csv', 'rb') as f:
            for line in f:
                if len(line.decode('utf-8').split(',')) != 11:
                    bad.write(line)
                else:
                    good.write(line)

tmp = pd.read_csv('./good.csv', header=None, quoting=csv.QUOTE_ALL)
tmp.index = tmp[3]
tmp.columns = ['year','grant','sub','num','id','subject','title','author','school','money','dueration']
tmp.sort_index().to_csv('./data/qingniankexuejijinxiangmu2017.csv', index=False, encoding='utf-8')

