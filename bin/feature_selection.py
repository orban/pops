#!/usr/bin/env python
import os, sys, time, re, json, pdb, random, datetime, subprocess
# -----------------------------------
import numpy as np
import pandas as pd
from scipy import stats

def top_features(data_X, data_y, feature_list, num_feature = 5):
    # check data integrity
    if len(feature_list) != data_X.shape[1]:
        print 'feautre list has length:', len(feature_list)
        print 'data_X has shape:', data_X.shape
        raise

    # pearson ranks
    n_features = data_X.shape[1]
    df = pd.DataFrame(columns=['features', 'p_value'])
    for i in range(n_features):
        x = data_X[:,i]
        p_value = stats.pearsonr(x,data_y)[1]
        _row = pd.Series([i, p_value], index=['features', 'p_value'])
        _row.name = i
        df = df.append(_row)
    df = df.sort('p_value', ascending=1)
    df['rank'] = np.arange(n_features) + 1
    df = df.sort('features', ascending=1)
    ranks = df['rank'].values

    dict_feature_to_rank_pearson = {f:r for f,r in zip(feature_list, ranks)}
    dict_rank_to_feature_pearson = {r:f for f,r in zip(feature_list, ranks)}

    top_features = list({dict_rank_to_feature_pearson[i]
                         for i in np.arange(num_feature)+1})

    return top_features

# # by SVM
# from sklearn.feature_selection import SelectKBest
# from sklearn import svm
# from sklearn.cross_validation import StratifiedKFold
# from sklearn.feature_selection import RFECV
# from scipy import stats

# svc = svm.SVC(C=1, kernel='linear')
# rfecv = RFECV(estimator=svc, step=1) #cv=StratifiedKFold(y, 2), scoring='accuracy')
# rfecv.fit(data_X, data_y)

# dict_feature_to_rank_svm = {f:r for f,r in zip(feature_names, rfecv.ranking_)}
# dict_rank_to_feature_svm = {r:f for f,r in zip(feature_names, rfecv.ranking_)}

# print '---------------'
# print 'feature selection results using SVM'
# print dict_rank_to_feature
# print '---------------'


if __name__ == '__main__':
    pass
