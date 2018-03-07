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
        with open('./data/zhuanxiangjijin2006.csv', 'rb') as f:
            for line in f:
                if len(line.decode('utf-8').split(',')) != 11:
                    bad.write(line)
                else:
                    good.write(line)

tmp = pd.read_csv('./good.csv', header=None, quoting=csv.QUOTE_ALL)
tmp.index = tmp[3]
tmp.columns = ['year','grant','sub','num','id','subject','title','author','school','money','duration']
tmp.sort_index().to_csv('./data/zhuanxiangjijin2006.csv', index=False, encoding='utf-8')

data = []
for x in os.listdir():
    print(x)
    d = pd.read_csv(x, sep=',', header=0)
    data.append(d)

all = pd.concat(data)
all['start'] = all['duration'].str.split('至').map(lambda x: x[0])
all['end'] = all['duration'].str.split('至').map(lambda x: x[1])
del all['duration']
del all['sub']
all.reset_index(drop=True, inplace=True)
all.to_csv('../isisn.csv', index=False, encoding='utf-8')