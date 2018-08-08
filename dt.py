# -*- coding: utf-8 -*-
from sklearn import tree
from sklearn import metrics
import pandas as pd
import numpy as np
import glob
import os

# input files
path_train = 'C:\\Users\sri01\Downloads\DS 6999\HAPT Train\*.csv'
path_test = 'C:\\Users\sri01\Downloads\DS 6999\HAPT Test\*.csv'
files_train = glob.glob(path_train)
files_test = glob.glob(path_test)

# output file directory
os.chdir('C:\\Users\sri01\Downloads\DS 6999\DT')

def dt_clf():
    # Iterate through every pair of files
    # Initialize final dataframe
    df_out = pd.DataFrame(columns=['Hz','s','Accuracy','Avg_Precision','Avg_F_Measure','Avg_Recall',
                                   'Precision','F_Measure','Recall'])
    # Counter
    ct=0
    for i in range(0, len(files_train), 2):
        ct+=1
        print(i)
        print(files_train[i])
        print(files_train[i+1])
        print(files_test[i])
        print(files_test[i+1])
        
        # Read in the data
        X = pd.read_table(files_train[i], sep='\s', engine='python')
        Y = pd.read_table(files_train[i+1], sep='\s', header=None, engine='python')
        X_t = pd.read_table(files_test[i], sep='\s', engine='python')
        Y_t = pd.read_table(files_test[i+1], sep='\s', header=None, engine='python')
    
        # Set the name
        name = files_train[i]
        
        # Determine frequency and seconds
        if '50hz' in name:
            hz = 50
        elif '25hz' in name:
            hz = 25
        elif '10hz' in name:
            hz = 10
        else:
            hz = 5
        if '10s' in name:
            seconds = 10
        elif '5s' in name:
            seconds = 5
        elif '3s' in name:
            seconds = 3
        elif '2s' in name:
            seconds = 2
        else:
            seconds = 1
        print('hz',hz,'seconds',seconds)
    
        # Create decision tree classifier
        dt_clf = tree.DecisionTreeClassifier(splitter='best', criterion='gini') # multiclass multioutputs
            
        # Model and fit
        dt_clf.fit(X, Y.values.ravel())
        predictions = dt_clf.predict(X_t)
        
        # Accuracy
        accuracy = metrics.accuracy_score(Y_t[0],predictions)
        # Precision (by label)
        precision = metrics.precision_score(Y_t[0],predictions,average=None)
        precision_mean = metrics.precision_score(Y_t[0],predictions,average='weighted')
        # F Measure (by label)
        f1 = metrics.f1_score(Y_t[0],predictions,average=None)
        f1_mean = metrics.f1_score(Y_t[0],predictions,average='weighted')
        # Recall
        recall = metrics.recall_score(Y_t[0],predictions,average=None)
        recall_mean = metrics.recall_score(Y_t[0],predictions,average='weighted')
        
        # Add onto dataframe
        df_out.loc[ct] = [hz, seconds, accuracy, precision_mean, f1_mean, recall_mean,
                  precision, f1, recall]

    return(df_out.sort_values(by=['Hz','s']).reset_index(drop=True))

if __name__ == '__main__':
    out=dt_clf()