import glob
import os
import pandas as pd
import scipy

# This is the directory where your raw data files are located
path = 'F:\DS 6999\data\HAPT\RawData\*.txt'
files = glob.glob(path)

# This is the directory where you want to write the new csvs to
os.chdir('F:\DS 6999\project\hzData')

def get_data():
    """
    Input: Raw data files from HAPT data set.
    Output: Data files which have new columns experimentID, userID, and
    activityID associated with labels.txt
    """
    
    # This is just reading in labels.txt
    type_file = pd.read_table(files[-1], sep='\s', header=None, engine='python')
    type_file.columns = ['experimentID','userID','activityID','start','end']
    
    # Initialize the final output dataframes
    acc_hz_5 = pd.DataFrame(); acc_hz_10 = pd.DataFrame();
    acc_hz_25 = pd.DataFrame(); acc_hz_50 = pd.DataFrame();
    gyro_hz_5 = pd.DataFrame(); gyro_hz_10 = pd.DataFrame();
    gyro_hz_25 = pd.DataFrame(); gyro_hz_50 = pd.DataFrame();
    
    ct = 0
    
    # Iterate through all of the raw data files except for labels.txt
    for name in files[:-1]:
        ct += 1
        # Print the filename to keep track of which files are being processed.
        print(ct, "/", 122, name)

        # Read in the raw data
        df=pd.read_table(name, sep='\s', header=None, engine='python')
        
        # If accelerometer data, then set the variable filename to something
        # like 'acc_exp01_user01' and name the columns accordingly
        if 'acc' in name[-21:-4]:
            filename = name[-20:-4]
        # If gyroscopic data, use different headers
        else:
            filename = name[-21:-4]
            
        # Extract the experimentId and userID values from the filename
        df['experimentID'] = int(name[-13:-11])
        df['userID'] = int(name[-6:-4])
        
        # Create a temporary variable which observes a particular set of
        # experimentIDs and userIDs at a time. These will be iterated
        # through to associate the start and end indexes with activityID
        # as according to labels.txt
        type_files_temp = type_file[(type_file.experimentID==df.experimentID[1]) & (type_file.userID==df.userID[1])]
        
        # Initialize activityID. If no activityID is given in labels.txt
        # this variable will remain at 0
        df['activityID'] = 0
        
        # Iterate through each row of a certain set of experimentIDs and
        # userIDs (ie a sub-dataframe where experimentID==1 and userID==1)
        for row in type_files_temp.itertuples():
            # Get the start and end indexes from labels.txt
            s = getattr(row, 'start')
            e = getattr(row, 'end')
            
            # Set the value of activityID within these indexes
            df.activityID[s:e+1] = getattr(row, 'activityID')
            
        # Iterate through each of the frequencies, aka downsampling
        for hz in [5,10,25,50]:
            # Downsample by observing every n-th entry based on the ratio
            #butter_filt = scipy.signal.butter(3, 20/(50/2))
            butter_filt_2 = scipy.signal.butter(3, 0.3/(hz/2))
            if hz==50:
                df2 = df.reset_index(drop=True)
                # This is the median filter
                df_filt=df[[0,1,2]].apply(scipy.signal.medfilt)
                #df_filt_2 = df_filt.apply(lambda x: scipy.signal.lfilter(butter_filt[0],butter_filt[1],x))
                df_out = pd.concat([df2[['experimentID', 'userID', 'activityID']],df_filt], axis=1)
                if 'acc' in filename:
                    df_g = df_filt.apply(lambda x: scipy.signal.lfilter(butter_filt_2[0],butter_filt_2[1],x))
                    df_out['tGravityAcc-X'] = df_g[0]
                    df_out['tGravityAcc-Y'] = df_g[1]
                    df_out['tGravityAcc-Z'] = df_g[2]
                    df_out[0] = df_out[0]-df_g[0]
                    df_out[1] = df_out[1]-df_g[1]
                    df_out[2] = df_out[2]-df_g[2]
                    df_out = df_out.rename(columns={0:'tBodyAcc-X',1:'tBodyAcc-Y',2:'tBodyAcc-Z'})
                    acc_hz_50 = acc_hz_50.append(df_out)
                else:
                    df_out = df_out.rename(columns={0:'tBodyGyro-X',1:'tBodyGyro-Y',2:'tBodyGyro-Z'})
                    gyro_hz_50 = gyro_hz_50.append(df_out)
            elif hz==25:
                df2 = df[df.index%2==0].reset_index(drop=True)
                df_filt=df2[[0,1,2]].apply(scipy.signal.medfilt)
                #df_filt_2 = df_filt.apply(lambda x: scipy.signal.lfilter(butter_filt[0],butter_filt[1],x))
                df_out = pd.concat([df2[['experimentID', 'userID', 'activityID']],df_filt], axis=1)
                if 'acc' in filename:
                    df_g = df_filt.apply(lambda x: scipy.signal.lfilter(butter_filt_2[0],butter_filt_2[1],x))
                    df_out['tGravityAcc-X'] = df_g[0]
                    df_out['tGravityAcc-Y'] = df_g[1]
                    df_out['tGravityAcc-Z'] = df_g[2]
                    df_out[0] = df_out[0]-df_g[0]
                    df_out[1] = df_out[1]-df_g[1]
                    df_out[2] = df_out[2]-df_g[2]
                    df_out = df_out.rename(columns={0:'tBodyAcc-X',1:'tBodyAcc-Y',2:'tBodyAcc-Z'})
                    acc_hz_25 = acc_hz_25.append(df_out)
                else:
                    df_out = df_out.rename(columns={0:'tBodyGyro-X',1:'tBodyGyro-Y',2:'tBodyGyro-Z'})
                    gyro_hz_25 = gyro_hz_25.append(df_out)
            elif hz==10:
                df2 = df[df.index%5==0].reset_index(drop=True)
                df_filt=df2[[0,1,2]].apply(scipy.signal.medfilt)
                #df_filt_2 = df_filt.apply(lambda x: scipy.signal.lfilter(butter_filt[0],butter_filt[1],x))
                df_out = pd.concat([df2[['experimentID', 'userID', 'activityID']],df_filt], axis=1)
                if 'acc' in filename:
                    df_g = df_filt.apply(lambda x: scipy.signal.lfilter(butter_filt_2[0],butter_filt_2[1],x))
                    df_out['tGravityAcc-X'] = df_g[0]
                    df_out['tGravityAcc-Y'] = df_g[1]
                    df_out['tGravityAcc-Z'] = df_g[2]
                    df_out[0] = df_out[0]-df_g[0]
                    df_out[1] = df_out[1]-df_g[1]
                    df_out[2] = df_out[2]-df_g[2]
                    df_out = df_out.rename(columns={0:'tBodyAcc-X',1:'tBodyAcc-Y',2:'tBodyAcc-Z'})
                    acc_hz_10 = acc_hz_10.append(df_out)
                else:
                    df_out = df_out.rename(columns={0:'tBodyGyro-X',1:'tBodyGyro-Y',2:'tBodyGyro-Z'})
                    gyro_hz_10 = gyro_hz_10.append(df_out)
            else:
                df2 = df[df.index%10==0].reset_index(drop=True)
                df_filt=df2[[0,1,2]].apply(scipy.signal.medfilt)
                #df_filt_2 = df_filt.apply(lambda x: scipy.signal.lfilter(butter_filt[0],butter_filt[1],x))
                df_out = pd.concat([df2[['experimentID', 'userID', 'activityID']],df_filt], axis=1)
                if 'acc' in filename:
                    df_g = df_filt.apply(lambda x: scipy.signal.lfilter(butter_filt_2[0],butter_filt_2[1],x))
                    df_out['tGravityAcc-X'] = df_g[0]
                    df_out['tGravityAcc-Y'] = df_g[1]
                    df_out['tGravityAcc-Z'] = df_g[2]
                    df_out[0] = df_out[0]-df_g[0]
                    df_out[1] = df_out[1]-df_g[1]
                    df_out[2] = df_out[2]-df_g[2]
                    df_out = df_out.rename(columns={0:'tBodyAcc-X',1:'tBodyAcc-Y',2:'tBodyAcc-Z'})
                    acc_hz_5 = acc_hz_5.append(df_out)
                else:
                    df_out = df_out.rename(columns={0:'tBodyGyro-X',1:'tBodyGyro-Y',2:'tBodyGyro-Z'})
                    gyro_hz_5 = gyro_hz_5.append(df_out)

    # Merge the acc and gyro dataframes for a specific frequency
    # To make this shorter, find a way to iterate this through each hz
    # Also make sure to order the columns in a way that makes sense
    hz_5 = acc_hz_5
    hz_10 = acc_hz_10
    hz_25 = acc_hz_25
    hz_50 = acc_hz_50
    
    hz_5['tBodyGyro-X'] = gyro_hz_5['tBodyGyro-X']
    hz_5['tBodyGyro-Y'] = gyro_hz_5['tBodyGyro-Y']
    hz_5['tBodyGyro-Z'] = gyro_hz_5['tBodyGyro-Z']
    hz_5 = hz_5[['experimentID','userID','activityID','tBodyAcc-X', 'tBodyAcc-Y', 'tBodyAcc-Z', 'tGravityAcc-X', 'tGravityAcc-Y', 'tGravityAcc-Z', 'tBodyGyro-X', 'tBodyGyro-Y', 'tBodyGyro-Z']]

    hz_10['tBodyGyro-X'] = gyro_hz_10['tBodyGyro-X']
    hz_10['tBodyGyro-Y'] = gyro_hz_10['tBodyGyro-Y']
    hz_10['tBodyGyro-Z'] = gyro_hz_10['tBodyGyro-Z']
    hz_10 = hz_10[['experimentID','userID','activityID','tBodyAcc-X', 'tBodyAcc-Y', 'tBodyAcc-Z', 'tGravityAcc-X', 'tGravityAcc-Y', 'tGravityAcc-Z', 'tBodyGyro-X', 'tBodyGyro-Y', 'tBodyGyro-Z']]

    hz_25['tBodyGyro-X'] = gyro_hz_25['tBodyGyro-X']
    hz_25['tBodyGyro-Y'] = gyro_hz_25['tBodyGyro-Y']
    hz_25['tBodyGyro-Z'] = gyro_hz_25['tBodyGyro-Z']
    hz_25 = hz_25[['experimentID','userID','activityID','tBodyAcc-X', 'tBodyAcc-Y', 'tBodyAcc-Z', 'tGravityAcc-X', 'tGravityAcc-Y', 'tGravityAcc-Z', 'tBodyGyro-X', 'tBodyGyro-Y', 'tBodyGyro-Z']]
    
    hz_50['tBodyGyro-X'] = gyro_hz_50['tBodyGyro-X']
    hz_50['tBodyGyro-Y'] = gyro_hz_50['tBodyGyro-Y']
    hz_50['tBodyGyro-Z'] = gyro_hz_50['tBodyGyro-Z']
    hz_50 = hz_50[['experimentID','userID','activityID','tBodyAcc-X', 'tBodyAcc-Y', 'tBodyAcc-Z', 'tGravityAcc-X', 'tGravityAcc-Y', 'tGravityAcc-Z', 'tBodyGyro-X', 'tBodyGyro-Y', 'tBodyGyro-Z']]
    
    # Output the following files which are master files that contain all
    # the information in the raw data files, including downsampled copies
    print('1/4 Printing 5hz.csv')
    hz_5.to_csv('5hz.csv',sep='\t')
    print('2/4 Printing 10hz.csv')
    hz_10.to_csv('10hz.csv',sep='\t')
    print('3/4 Printing 25hz.csv')
    hz_25.to_csv('25hz.csv',sep='\t')
    print('4/4 Printing 50hz.csv')
    hz_50.to_csv('50hz.csv',sep='\t')
    
    print('Done')
    
if __name__=='__main__':
    get_data()
