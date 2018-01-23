# -*- coding: utf-8 -*-
"""
Created on Mon Jan 22 09:23:59 2018

@author: lib
"""
import pandas as pd

with open('good.csv', 'wb') as good:
    with open('bad.csv', 'wb') as bad:
        with open('ms2011.csv', 'rb') as f:
            for line in f:
                if len(line.decode('utf-8').split(',')) > 11:
                    bad.write(line)
                else:
                    good.write(line)
                    
                    
tmp = pd.read_csv('./good.csv', header=None)

tmp.index= tmp[3]
tmp.columns = ['year','grant','sub','num','id','subject','title','author','school','money','dueration']
tmp.sort_index().to_csv('./data/mianshang2011.csv', index=False, encoding='utf-8')



