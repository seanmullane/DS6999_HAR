import glob
import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn import preprocessing

def split_scale():
    
    # Change this line to where your feature data is located
    path = 'F:\\DS 6999\\project\\FeatureData\\*.csv'
    files = glob.glob(path)
    
    # Change this line to where the transformed and scaled data will be
    test = 'F:\\DS 6999\\project\\test'
    train = 'F:\\DS 6999\\project\\train'
    
    # Here's a scaler that automatically scales values between -1 and 1
    max_abs_scaler = preprocessing.MaxAbsScaler()
    
    for name in files:
        # Import data
        df=pd.DataFrame.from_csv(name, sep='\t')
        # Remove all entries where there is no activity id (Y value)
        df=df[df['activityID']!=0]
        # Drop all raw data columns. Leave all features.
        # Separate the features (X variables) from the Y variable
        df_X=df.drop(columns=['activityID','experimentID','index',
                         'tBodyAcc-X','tBodyAcc-Y','tBodyAcc-Z',
                         'tBodyGyro-X','tBodyGyro-Y','tBodyGyro-Z',
                         'tGravityAcc-X','tGravityAcc-Y','tGravityAcc-Z',
                         'userID',
                         'fBodyAcc-X','fBodyAcc-Y','fBodyAcc-Z',
                         
                         # Here are values which go into extremes/are bad
                         'tBodyAcc-ropy-1','tBodyAcc-ropy-2','tBodyAcc-ropy-3',
                         'tBodyAccJerk-ropy-1','tBodyAccJerk-ropy-2','tBodyAccJerk-ropy-3',
                         'tBodyGyro-ropy-1','tBodyGyro-ropy-2','tBodyGyro-ropy-3',
                         'tBodyGyroJerk-ropy-1','tBodyGyroJerk-ropy-2','tBodyGyroJerk-ropy-3',
                         'tBodyAccJerkMag-ropy-1','tBodyGyroJerkMag-ropy-1',
                         'tGravityAcc-ropy-1','tGravityAcc-ropy-2','tGravityAcc-ropy-3'
                         ])
        
        # Here's a diagnostic function that shows which values are invalid
        # diag=a.isin([np.nan,np.inf,-np.inf]).apply(lambda x: sum(x))
        
        df_Y = df['activityID']
        
        # Split the data into two sets at a 3:1 ratio.
        a, b, c, d = train_test_split(df_X, df_Y, test_size=0.25, random_state=4669)
        
        # Scale data
        a_scale = max_abs_scaler.fit_transform(a)
        a_scale = pd.DataFrame(a_scale)
        a_scale.columns = list(a)
        
        b_scale = max_abs_scaler.fit_transform(b)
        b_scale = pd.DataFrame(b_scale)
        b_scale.columns = list(b)
    
        # Set the value of hz and seconds    
        if "50hz" in name:
            hz = 50
        elif "25hz" in name:
            hz = 25
        elif "10hz" in name:
            hz = 10
        else:
            hz = 5
            
        if "10s" in name:
            seconds = 10
        elif "5s" in name:
            seconds = 5
        elif "3s" in name:
            seconds = 3
        elif "2s" in name:
            seconds = 2
        else:
            seconds = 1
    
        print("Printing "+str(hz)+"hz "+str(seconds)+" second(s)")
    
        # Print Training
        os.chdir(train)
        a_scale.to_csv(str(hz)+'hz'+str(seconds)+'s_train_X.csv',sep='\t')
        c.to_csv(str(hz)+'hz'+str(seconds)+'s_train_Y.csv',sep='\t')    
        
        # Print Testing
        os.chdir(test)
        b_scale.to_csv(str(hz)+'hz'+str(seconds)+'s_test_X.csv',sep='\t')
        d.to_csv(str(hz)+'hz'+str(seconds)+'s_test_X.csv',sep='\t')
    
if __name__ == '__main__':
    split_scale()