import glob
import numpy as np
import os
import pandas as pd
from sklearn import svm
from sklearn import metrics

# This is where the raw data files are
path_test = 'F://DS 6999//project//test//*.csv'
path_train = 'F://DS 6999//project//train//*.csv'
files_test = glob.glob(path_test)
files_train = glob.glob(path_train)

os.chdir('F:\DS 6999\project\log_reg')

def supp():
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
    
        # Create the linear regression model
        supp = svm.SVC()
            
        # Model and fit
        supp.fit(X, Y.values.ravel())
        predictions = supp.predict(X_t)
        
        # Accuracy
        accuracy = metrics.accuracy_score(Y_t[0],predictions)
        # Precision (by label)
        precision = metrics.precision_score(Y_t[0],predictions,average=None)
        precision_mean = np.mean(precision[precision!=0])
        # F Measure (by label)
        f1 = metrics.f1_score(Y_t[0],predictions,average=None)
        f1_mean = np.mean(f1[f1!=0])
        # Recall
        recall = metrics.recall_score(Y_t[0],predictions,average=None)
        recall_mean = np.mean(recall[recall!=0])
        
        # Add onto dataframe
        df_out.loc[ct] = [hz, seconds, accuracy, precision_mean, f1_mean, recall_mean,
                  precision, f1, recall]

    return(df_out.sort_values(by=['Hz','s']).reset_index(drop=True))

        
if __name__ == '__main__':
    out=supp()