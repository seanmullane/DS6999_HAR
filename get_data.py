# -*- coding: utf-8 -*-
import utility as ut
import pandas as pd

"""
Input: Raw data files from HAPT Data Set\RawData
       acc_expXX_userYY.txt: The raw triaxial acceleration signal for the experiment number XX and associated to the user number YY. 
                             Every row is one acceleration sample (three axis) captured at a frequency of 50Hz. 

       gyro_expXX_userYY.txt: The raw triaxial angular speed signal for the experiment number XX and associated to the user number YY. 
                              Every row is one angular velocity sample (three axis) captured at a frequency of 50Hz. 

       labels.txt: include all the activity labels available for the dataset (1 per row). 
                   Column 1: experiment number ID, 
                   Column 2: user number ID, 
                   Column 3: activity number ID 
                   Column 4: Label start point (in number of signal log samples (recorded at 50Hz))
                   Column 5: Label end point (in number of signal log samples)
                    
Output: .csv files containing data at 5Hz, 10Hz, 25Hz and 50Hz with labels 
        [experimentID userID activityID tBodyAcc-X tBodyAcc-Y tBodyAcc-Z tGravityAcc-X tGravityAcc-Y tGravityAcc-Z tBodyGyro-X tBodyGyro-Y]
        Time domain signals are prefixed with 't' to denote time.
"""

# get raw data files
path_to_raw_data_files = "C:\\Users\sri01\Downloads\DS 6999\HAPT Data Set\RawData\*.txt"
files = ut.get_files(path_to_raw_data_files)

# This is the directory where you want to write the new csvs to
path_to_output_directory = "C:\\Users\sri01\Downloads\DS 6999\HAPT Processed2"
ut.set_output_path(path_to_output_directory)

# get data from labels file
def get_label_data(files):
    for file in files:
        if file.__contains__('labels'):
            label_file = file
            break
    return ut.get_data(label_file)

def downsample_and_filter_acc(dataframe, hz):
    df_reset = ut.get_data_hz(dataframe, hz)
    df_filtered = ut.apply_median_filter(df_reset, [0, 1, 2])
    df_out = pd.concat([df_reset[['experimentID', 'userID', 'activityID']], df_filtered], axis=1)
    df_gravity = ut.apply_butter_filter(df_filtered, hz)
    
    df_out[[0,1,2]] -= df_gravity[[0,1,2]]
        
    df_out['tGravityAcc-X'] = df_gravity[0]
    df_out['tGravityAcc-Y'] = df_gravity[1]
    df_out['tGravityAcc-Z'] = df_gravity[2]
        
    df_out = df_out.rename(columns={0: 'tBodyAcc-X', 1: 'tBodyAcc-Y', 2: 'tBodyAcc-Z'})
    
    return(df_out)
    
def downsample_and_filter_gyro(dataframe, hz):
    df_reset = ut.get_data_hz(dataframe, hz)
    df_filtered = ut.apply_median_filter(df_reset, [0, 1, 2])
    df_out = pd.concat([df_reset[['experimentID', 'userID', 'activityID']], df_filtered], axis=1)
    df_out = df_out.rename(columns={0: 'tBodyGyro-X', 1: 'tBodyGyro-Y', 2: 'tBodyGyro-Z'})
    return(df_out)
    
# read label data in labels.txt
label_data = get_label_data(files)
labels = ['experimentID', 'userID', 'activityID', 'start', 'end']
label_data = ut.add_labels_to_data(label_data, labels)

# initialize empty dataframes for acc and gyro data for different frequencies
acc_hz_5 = ut.get_empty_dataframe();
acc_hz_10 = ut.get_empty_dataframe();
acc_hz_25 = ut.get_empty_dataframe();
acc_hz_50 = ut.get_empty_dataframe();
gyro_hz_5 = ut.get_empty_dataframe();
gyro_hz_10 = ut.get_empty_dataframe();
gyro_hz_25 = ut.get_empty_dataframe();
gyro_hz_50 = ut.get_empty_dataframe();

# for each file
for file in files:
    # read into dataframe
    df = ut.get_data(file)
    
    # get filename from filepath
    filename = ut.get_file_name_from_path(file)    
    
    # for all files other than labels.txt file
    if(not(filename.__contains__('labels'))):
    
        # get experimentID and userID from filename
        exp_id = int(filename.split('_')[1][3:])
        user_id = int(filename.split('_')[2][4:])
        
        # add experimentID userID and activityID to the data
        df['experimentID'] = exp_id
        df['userID'] = user_id
        df['activityID'] = 0
        
        # get the rows from label data where the experimentID and userID match
        label_rows = label_data[(label_data.experimentID == exp_id) & (label_data.userID == user_id)]
    
        # Iterate through each row of a certain set of experimentIDs and
        # userIDs (ie a sub-dataframe where experimentID==1 and userID==1)
        for row in label_rows.itertuples():
            
            # Get the start and end indexes from labels.txt
            s = getattr(row, 'start')
            e = getattr(row, 'end')
    
            # Set the value of activityID within these indexes
            df.activityID[s:e + 1] = getattr(row, 'activityID')
    
        if 'acc' in filename:
            acc_hz_5 = acc_hz_5.append(downsample_and_filter_acc(df, 5))
            acc_hz_10 = acc_hz_10.append(downsample_and_filter_acc(df, 10))
            acc_hz_25 = acc_hz_25.append(downsample_and_filter_acc(df, 25))
            acc_hz_50 = acc_hz_50.append(downsample_and_filter_acc(df, 50))

        else:
            gyro_hz_5 = gyro_hz_5.append(downsample_and_filter_gyro(df, 5))
            gyro_hz_10 = gyro_hz_10.append(downsample_and_filter_gyro(df, 10))
            gyro_hz_25 = gyro_hz_25.append(downsample_and_filter_gyro(df, 25))
            gyro_hz_50 = gyro_hz_50.append(downsample_and_filter_gyro(df, 50))
            
hz_5 = pd.concat([acc_hz_5, gyro_hz_5.drop(columns=['experimentID', 'userID', 'activityID'])], axis=1)
hz_10 = pd.concat([acc_hz_10, gyro_hz_10.drop(columns=['experimentID', 'userID', 'activityID'])], axis=1)
hz_25 = pd.concat([acc_hz_25, gyro_hz_25.drop(columns=['experimentID', 'userID', 'activityID'])], axis=1)
hz_50 = pd.concat([acc_hz_50, gyro_hz_50.drop(columns=['experimentID', 'userID', 'activityID'])], axis=1)

label_list = ['experimentID', 'userID', 'activityID', 'tBodyAcc-X', 'tBodyAcc-Y', 'tBodyAcc-Z', 'tGravityAcc-X',
         'tGravityAcc-Y', 'tGravityAcc-Z', 'tBodyGyro-X', 'tBodyGyro-Y', 'tBodyGyro-Z']
hz_5 = hz_5[label_list]
hz_10 = hz_10[label_list]
hz_25 = hz_25[label_list]
hz_50 = hz_50[label_list]
 
print('1/4 Printing 5hz.csv')
hz_5.to_csv('5hz.csv', sep='\t')
print('2/4 Printing 10hz.csv')
hz_10.to_csv('10hz.csv', sep='\t')
print('3/4 Printing 25hz.csv')
hz_25.to_csv('25hz.csv', sep='\t')
print('4/4 Printing 50hz.csv')
hz_50.to_csv('50hz.csv', sep='\t')

print('Done')