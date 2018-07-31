import glob
import os
import pandas as pd

# This is the directory where your raw data files are located
path = 'F:\DS 6999\data\HAPT\RawData\*.txt'
files = glob.glob(path)

# This is the directory where you want to write the new csvs to
os.chdir('F:\\DS 6999\\project\\NewData')

def get_data():
    """
    Input: Raw data files from HAPT data set.
    Output: Data files which have new columns experimentID, userID, and
    activityID associated with labels.txt
    """
    
    # This is just reading in labels.txt
    type_file = pd.read_table(files[-1], sep='\s', header=None)
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
        df=pd.read_table(name, sep='\s', header=None)
        
        # If accelerometer data, then set the variable filename to something
        # like 'acc_exp01_user01' and name the columns accordingly
        if 'acc' in name[-21:-4]:
            filename = name[-20:-4]
            df.columns = ['tAcc-X', 'tAcc-Y', 'tAcc-Z']
        # If gyroscopic data, use different headers
        else:
            filename = name[-21:-4]
            df.columns = ['tGyro-X', 'tGyro-Y', 'tGyro-Z']
            
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
            if hz==50:
                df2 = df
                if 'acc' in filename:
                    acc_hz_50 = acc_hz_50.append(df2)
                else:
                    gyro_hz_50 = gyro_hz_50.append(df2)
            elif hz==25:
                df2 = df[df.index%2==0]
                if 'acc' in filename:
                    acc_hz_25 = acc_hz_25.append(df2)
                else:
                    gyro_hz_25 = gyro_hz_25.append(df2)
            elif hz==10:
                df2 = df[df.index%5==0]
                if 'acc' in filename:
                    acc_hz_10 = acc_hz_10.append(df2)
                else:
                    gyro_hz_10 = gyro_hz_10.append(df2)
            else:
                df2 = df[df.index%10==0]
                if 'acc' in filename:
                    acc_hz_5 = acc_hz_5.append(df2)
                else:
                    gyro_hz_5 = gyro_hz_5.append(df2)
    
    # Merge the acc and gyro dataframes for a specific frequency
    # To make this shorter, find a way to iterate this through each hz
    # Also make sure to order the columns in a way that makes sense
    
    print('1/4 Processing hz5.')
    hz_5 = acc_hz_5
    hz_5['tGyro-X'] = gyro_hz_5['tGyro-X']
    hz_5['tGyro-Y'] = gyro_hz_5['tGyro-Y']
    hz_5['tGyro-Z'] = gyro_hz_5['tGyro-Z']
    hz_5 = hz_5[['experimentID','userID','activityID','tAcc-X', 'tAcc-Y', 'tAcc-Z','tGyro-X', 'tGyro-Y', 'tGyro-Z']]
    
    print('2/4 Processing hz10.')
    hz_10 = acc_hz_10
    hz_10['tGyro-X'] = gyro_hz_10['tGyro-X']
    hz_10['tGyro-Y'] = gyro_hz_10['tGyro-Y']
    hz_10['tGyro-Z'] = gyro_hz_10['tGyro-Z']
    hz_10 = hz_10[['experimentID','userID','activityID','tAcc-X', 'tAcc-Y', 'tAcc-Z','tGyro-X', 'tGyro-Y', 'tGyro-Z']]
    
    print('3/4 Processing hz25.')
    hz_25 = acc_hz_25
    hz_25['tGyro-X'] = gyro_hz_25['tGyro-X']
    hz_25['tGyro-Y'] = gyro_hz_25['tGyro-Y']
    hz_25['tGyro-Z'] = gyro_hz_25['tGyro-Z']
    hz_25 = hz_25[['experimentID','userID','activityID','tAcc-X', 'tAcc-Y', 'tAcc-Z','tGyro-X', 'tGyro-Y', 'tGyro-Z']]
    
    print('4/4 Processing hz50.')
    hz_50 = acc_hz_50
    hz_50['tGyro-X'] = gyro_hz_50['tGyro-X']
    hz_50['tGyro-Y'] = gyro_hz_50['tGyro-Y']
    hz_50['tGyro-Z'] = gyro_hz_50['tGyro-Z']
    hz_50 = hz_50[['experimentID','userID','activityID','tAcc-X', 'tAcc-Y', 'tAcc-Z','tGyro-X', 'tGyro-Y', 'tGyro-Z']]
    
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