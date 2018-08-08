import glob
import numpy as np
import os
import pandas as pd
from sklearn import linear_model
from sklearn import metrics
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import classification_report

# This is where the raw data files are
path_test = 'F://DS 6999//project//test//*.csv'
path_train = 'F://DS 6999//project//train//*.csv'
files_test = glob.glob(path_test)
files_train = glob.glob(path_train)

os.chdir('F:\DS 6999\project\log_reg')

def param():
    ct=0
    # Just test the first 5 pairs of files
    for i in range(0, 39, 2):
        ct+=1
        print(i)
        print(files_train[i])
        print(files_train[i+1])
        print(files_test[i])
        print(files_test[i+1])
        X = pd.read_table(files_train[i], sep='\s', engine='python')
        Y = pd.read_table(files_train[i+1], sep='\s', header=None, engine='python')
        X_t = pd.read_table(files_test[i], sep='\s', engine='python')
        Y_t = pd.read_table(files_test[i+1], sep='\s', header=None, engine='python')
        
        param = {'C': [0.1, 1, 10, 100, 1000] }
        logreg = linear_model.LogisticRegression(multi_class='ovr')
        clf = GridSearchCV(logreg, param, scoring='accuracy')
        clf.fit(X, Y.values.ravel())
        print(clf.best_params_)
        print()
        y_true, y_pred = Y_t, clf.predict(X_t)
        print(classification_report(y_true, y_pred))
# Results
# for 1s, C=100
# for 5s, C=1
# all other C=10
# for other hz values, it's mostly 10-100


def log_reg():
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
    
        # Create the logistic regression model
        logreg = linear_model.LogisticRegression(C=10, multi_class='ovr')
            
        # Model and fit
        logreg.fit(X, Y.values.ravel())
        predictions = logreg.predict(X_t)
        
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
        
    df_out.to_csv('logistic_regression.csv',sep='\t',index=False)
    return(df_out.sort_values(by=['Hz','s']).reset_index(drop=True))

        
if __name__ == '__main__':
    out=log_reg()