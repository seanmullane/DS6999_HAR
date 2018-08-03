from burg import _arburg2
import glob
from astropy.stats import median_absolute_deviation
import numpy as np
import os
import pandas as pd
from scipy.stats import pearsonr
from scipy.stats import entropy

# This is the directory where your hz data files are located
path = 'F:\\DS 6999\\project\\hzData\\*.csv'
files = glob.glob(path)

# This is the directory where you want to write the new csvs to
os.chdir('F:\\DS 6999\\project\\FeatureData')

# https://stackoverflow.com/questions/8930370/where-can-i-find-mad-mean-absolute-deviation-in-scipy
def mad2(arr):
    """ Median Absolute Deviation: a "Robust" version of standard deviation.
        Indices variabililty of the sample.
        https://en.wikipedia.org/wiki/Median_absolute_deviation 
    """
    arr = np.ma.array(arr).compressed() # should be faster to not use masked arrays.
    med = np.median(arr)
    return np.median(np.abs(arr - med))

# Ignore this for now, when the program is complete this will be in use
# =============================================================================
# def feature_extract():
#     """
#     """
# =============================================================================

# Counting variable to track progress
ct = 0

# Check all 4 hz files
for name in files[:1]: # Remove the limiter [:1] before the final product
    ct += 1
    print(ct, "/", 4, name)

    # Set the value of hz based on the name of the file
    if '5hz' in name:
        hz = 5
    elif '10hz' in name:
        hz = 10
    elif '25hz' in name:
        hz = 25
    else:
        hz = 50
    
    # Read the csv
    df=pd.DataFrame.from_csv(name, sep='\t')
    df_out = df
    df_out=df_out.reset_index()

    # This creates a new index between groups (of experiment ID's)
    # For example, if the first few entries of the data looked something
    # like (experiment ID's): 1 1 1 1 1 2 2 2 3 ....
    # then the new index would look something like:
    # 0 1 2 3 4 0 1 2 0 ...
    sub_index = df_out.groupby(['experimentID']).cumcount()
    df_out['index'] = sub_index
    
    for seconds in [1]:
#   for seconds in [1,2,3,5,10]: In the final product use this!
        
        # Group by experiment ID AND also in sets of (seconds*hz).
        # For example, if seconds is 10 and hz is 5, then a total of
        # 10*5=50 observations are grouped together within an experiment ID.
        # And in this case, 50 observations at 5hz = 10 seconds
        group = df_out.groupby(['experimentID',sub_index//(seconds*hz)*hz], as_index=False)
        group_square = pow(df_out,2).groupby(['experimentID',sub_index//(seconds*hz)*hz], as_index=False)
        # Initilze the feature list, which is a list that contains several
        # dataframes. At the end all of these dataframes will be concatinated
        df_feature = [group['index','tBodyAcc-X','tBodyAcc-Y','tBodyAcc-Z','tGravityAcc-X','tGravityAcc-Y','tGravityAcc-Z','tBodyGyro-X','tBodyGyro-Y','tBodyGyro-Z','experimentID','userID','activityID'].first()]

        # Tracks progress
        print('Window in seconds:',seconds)
        print('Processing tBodyAcc')

        ####################
        # Very important note: The end product for each of these dataframes we
        # are creating should ONLY contain new columns which we want to concat
        # together with the other dataframes. AVOID repeating things like
        # experimentID because some dataframes will automatically include it.
        # You can use the .drop(columns=['experimentID']) function to do this.
        # Fruthermore, sometimes the index will be different. Again, use the
        # .reset_index(drop=True) if this occurs. The purpose of this step
        # is to append all of these dataframes to the list of dataframes,
        # df_feature, and at the end they will be concatinated. Try to get
        # as many as done as possible.
        ####################

        # tBodyAcc-Mean-1
        # tBodyAcc-Mean-2                
        # tBodyAcc-Mean-3
        df_feature.append(group['tBodyAcc-X','tBodyAcc-Y','tBodyAcc-Z'].mean().rename(columns={'tBodyAcc-X':'tBodyAcc-Mean-1','tBodyAcc-Y':'tBodyAcc-Mean-2','tBodyAcc-Z':'tBodyAcc-Mean-3'}).drop(columns=['experimentID']))

        # tBodyAcc-STD-1                 
        # tBodyAcc-STD-2                 
        # tBodyAcc-STD-3                 
        df_feature.append(group['tBodyAcc-X','tBodyAcc-Y','tBodyAcc-Z'].std().rename(columns={'tBodyAcc-X':'tBodyAcc-STD-1','tBodyAcc-Y':'tBodyAcc-STD-2','tBodyAcc-Z':'tBodyAcc-STD-3'}).drop(columns=['experimentID']))
          
        # tBodyAcc-Mad-1
        # tBodyAcc-Mad-2                 
        # tBodyAcc-Mad-3                 
        df_feature.append(pd.DataFrame(group['tBodyAcc-X'].apply(lambda x: median_absolute_deviation(x)).rename(columns={'tBodyAcc-X':'tBodyAcc-Mad-1'}).reset_index(drop=True)).rename(columns={0:'tBodyAcc-Mad-1'}))
        df_feature.append(pd.DataFrame(group['tBodyAcc-Y'].apply(lambda x: median_absolute_deviation(x)).rename(columns={'tBodyAcc-Y':'tBodyAcc-Mad-2'}).reset_index(drop=True)).rename(columns={0:'tBodyAcc-Mad-2'}))
        df_feature.append(pd.DataFrame(group['tBodyAcc-Z'].apply(lambda x: median_absolute_deviation(x)).rename(columns={'tBodyAcc-Z':'tBodyAcc-Mad-2'}).reset_index(drop=True)).rename(columns={0:'tBodyAcc-Mad-3'}))
                
        # tBodyAcc-Max-1
        # tBodyAcc-Max-2                 
        # tBodyAcc-Max-3                 
        df_feature.append(group['tBodyAcc-X','tBodyAcc-Y','tBodyAcc-Z'].max().rename(columns={'tBodyAcc-X':'tBodyAcc-Max-1','tBodyAcc-Y':'tBodyAcc-Max-2','tBodyAcc-Z':'tBodyAcc-Max-3'}).drop(columns=['experimentID']))

        # tBodyAcc-Min-1                 
        # tBodyAcc-Min-2                 
        # tBodyAcc-Min-3                 
        df_feature.append(group['tBodyAcc-X','tBodyAcc-Y','tBodyAcc-Z'].min().rename(columns={'tBodyAcc-X':'tBodyAcc-Min-1','tBodyAcc-Y':'tBodyAcc-Min-2','tBodyAcc-Z':'tBodyAcc-Min-3'}).drop(columns=['experimentID']))

        # tBodyAcc-SMA-1
        # https://www.hindawi.com/journals/mpe/2015/790412/
        x=group['tBodyAcc-X'].apply(lambda x:list(x)).reset_index(drop=True)
        y=group['tBodyAcc-Y'].apply(lambda x:list(x)).reset_index(drop=True)
        z=group['tBodyAcc-Z'].apply(lambda x:list(x)).reset_index(drop=True)
        
        x=pd.DataFrame(x.apply(lambda lst: [abs(x) for x in lst]).apply(lambda x: sum(x)))
        y=pd.DataFrame(y.apply(lambda lst: [abs(x) for x in lst]).apply(lambda x: sum(x)))
        z=pd.DataFrame(z.apply(lambda lst: [abs(x) for x in lst]).apply(lambda x: sum(x)))
        
        sma=(x+y+z).rename(columns={0:'tBodyAcc-SMA-1'})
        df_feature.append(sma)
        
        # tBodyAcc-Energy-1
        # tBodyAcc-Energy-2              
        # tBodyAcc-Energy-3
        a=group_square['tBodyAcc-X','tBodyAcc-Y','tBodyAcc-Z'].sum().drop(columns=['experimentID'])
        b=group['tBodyAcc-X','tBodyAcc-Y','tBodyAcc-Z'].count().drop(columns=['experimentID'])
        df_feature.append((a/b).rename(columns={'tBodyAcc-X':'tBodyAcc-Energy-1','tBodyAcc-Y':'tBodyAcc-Energy-2','tBodyAcc-Z':'tBodyAcc-Energy-3'}))
        
        # tBodyAcc-IQR-1         
        # tBodyAcc-IQR-2                 
        # tBodyAcc-IQR-3      
        a=group['tBodyAcc-X','tBodyAcc-Y','tBodyAcc-Z'].quantile(0.75).reset_index(drop=True)
        b=group['tBodyAcc-X','tBodyAcc-Y','tBodyAcc-Z'].quantile(0.25).reset_index(drop=True)
        df_feature.append((a-b).rename(columns={'tBodyAcc-X':'tBodyAcc-IQR-1','tBodyAcc-Y':'tBodyAcc-IQR-2','tBodyAcc-Z':'tBodyAcc-IQR-3'}))
        
        # tBodyAcc-ropy-1                
        # tBodyAcc-ropy-2
        # tBodyAcc-ropy-3   
        x=pd.DataFrame(group['tBodyAcc-X'].apply(entropy).reset_index(drop=True)).rename(columns={0:'tBodyAcc-ropy-1'})
        y=pd.DataFrame(group['tBodyAcc-Y'].apply(entropy).reset_index(drop=True)).rename(columns={0:'tBodyAcc-ropy-2'})
        z=pd.DataFrame(group['tBodyAcc-Z'].apply(entropy).reset_index(drop=True)).rename(columns={0:'tBodyAcc-ropy-3'})
        df_feature.append(x)
        df_feature.append(y)
        df_feature.append(z)

        # tBodyAcc-ARCoeff-1             
        # tBodyAcc-ARCoeff-2             
        # tBodyAcc-ARCoeff-3             
        # tBodyAcc-ARCoeff-4    
        a=group['tBodyAcc-X'].apply(lambda x: list(x)).drop(columns='experimentID').reset_index(drop=True)
        b=pd.DataFrame(a)
        mask=(group['tBodyAcc-X'].count()['tBodyAcc-X']>3).values.tolist()
        b_valid = b[mask]
        c=b_valid[0].apply(lambda x: _arburg2(x,4))
        d = pd.DataFrame(c)
        e=d.apply(lambda x: [y[0] for y in list(x)])
        df_feature.append(e.apply(lambda x: [y[1] for y in list(x)]).apply(lambda x: x.real).rename(columns={0:'tBodyAcc-ARCoeff-1'}))
        df_feature.append(e.apply(lambda x: [y[2] for y in list(x)]).apply(lambda x: x.real).rename(columns={0:'tBodyAcc-ARCoeff-2'}))
        df_feature.append(e.apply(lambda x: [y[3] for y in list(x)]).apply(lambda x: x.real).rename(columns={0:'tBodyAcc-ARCoeff-3'}))
        df_feature.append(e.apply(lambda x: [y[4] for y in list(x)]).apply(lambda x: x.real).rename(columns={0:'tBodyAcc-ARCoeff-4'}))
        
        # tBodyAcc-ARCoeff-5             
        # tBodyAcc-ARCoeff-6             
        # tBodyAcc-ARCoeff-7             
        # tBodyAcc-ARCoeff-8
        a=group['tBodyAcc-Y'].apply(lambda x: list(x)).drop(columns='experimentID').reset_index(drop=True)
        b=pd.DataFrame(a)
        mask=(group['tBodyAcc-Y'].count()['tBodyAcc-Y']>3).values.tolist()
        b_valid = b[mask]
        c=b_valid[0].apply(lambda x: _arburg2(x,4))
        d = pd.DataFrame(c)
        e=d.apply(lambda x: [y[0] for y in list(x)])
        df_feature.append(e.apply(lambda x: [y[1] for y in list(x)]).apply(lambda x: x.real).rename(columns={0:'tBodyAcc-ARCoeff-5'}))
        df_feature.append(e.apply(lambda x: [y[2] for y in list(x)]).apply(lambda x: x.real).rename(columns={0:'tBodyAcc-ARCoeff-6'}))
        df_feature.append(e.apply(lambda x: [y[3] for y in list(x)]).apply(lambda x: x.real).rename(columns={0:'tBodyAcc-ARCoeff-7'}))
        df_feature.append(e.apply(lambda x: [y[4] for y in list(x)]).apply(lambda x: x.real).rename(columns={0:'tBodyAcc-ARCoeff-8'}))        

        # tBodyAcc-ARCoeff-9             
        # tBodyAcc-ARCoeff-10            
        # tBodyAcc-ARCoeff-11            
        # tBodyAcc-ARCoeff-12
        a=group['tBodyAcc-Z'].apply(lambda x: list(x)).drop(columns='experimentID').reset_index(drop=True)
        b=pd.DataFrame(a)
        mask=(group['tBodyAcc-Z'].count()['tBodyAcc-Z']>3).values.tolist()
        b_valid = b[mask]
        c=b_valid[0].apply(lambda x: _arburg2(x,4))
        d = pd.DataFrame(c)
        e=d.apply(lambda x: [y[0] for y in list(x)])
        df_feature.append(e.apply(lambda x: [y[1] for y in list(x)]).apply(lambda x: x.real).rename(columns={0:'tBodyAcc-ARCoeff-9'}))
        df_feature.append(e.apply(lambda x: [y[2] for y in list(x)]).apply(lambda x: x.real).rename(columns={0:'tBodyAcc-ARCoeff-10'}))
        df_feature.append(e.apply(lambda x: [y[3] for y in list(x)]).apply(lambda x: x.real).rename(columns={0:'tBodyAcc-ARCoeff-11'}))
        df_feature.append(e.apply(lambda x: [y[4] for y in list(x)]).apply(lambda x: x.real).rename(columns={0:'tBodyAcc-ARCoeff-12'}))
        
        # tBodyAcc-Correlation-1         
        # tBodyAcc-Correlation-2         
        # tBodyAcc-Correlation-3
        x=pd.DataFrame(group['tBodyAcc-X'].apply(lambda x:list(x))).reset_index(drop=True)
        y=pd.DataFrame(group['tBodyAcc-Y'].apply(lambda x:list(x))).reset_index(drop=True)
        z=pd.DataFrame(group['tBodyAcc-Z'].apply(lambda x:list(x))).reset_index(drop=True)
        
        yz=pd.concat([y,z],axis=1)
        yz.columns = ['y','z']
        yz=yz.apply(lambda row: pearsonr(row['y'],row['z']), axis=1)
        df_feature.append(pd.DataFrame(yz.apply(lambda x: x[0])).rename(columns={0:'tBodyAcc-Correlation-1'}))
        
        xz=pd.concat([x,z],axis=1)
        xz.columns = ['x','z']
        xz=xz.apply(lambda row: pearsonr(row['x'],row['z']), axis=1)
        df_feature.append(pd.DataFrame(xz.apply(lambda x: x[0])).rename(columns={0:'tBodyAcc-Correlation-2'}))

        xy=pd.concat([x,y],axis=1)
        xy.columns = ['x','y']
        xy=xy.apply(lambda row: pearsonr(row['x'],row['y']), axis=1)
        df_feature.append(pd.DataFrame(xy.apply(lambda x: x[0])).rename(columns={0:'tBodyAcc-Correlation-3'}))
        
        print('Processing tGravityAcc')
        
        # tGravityAcc-Mean-1             
        # tGravityAcc-Mean-2             
        # tGravityAcc-Mean-3  
        df_feature.append(group['tGravityAcc-X','tGravityAcc-Y','tGravityAcc-Z'].mean().rename(columns={'tGravityAcc-X':'tGravityAcc-Mean-1','tGravityAcc-Y':'tGravityAcc-Mean-2','tGravityAcc-Z':'tGravityAcc-Mean-3'}).drop(columns=['experimentID']))
           
        # tGravityAcc-STD-1              
        # tGravityAcc-STD-2              
        # tGravityAcc-STD-3     
        df_feature.append(group['tGravityAcc-X','tGravityAcc-Y','tGravityAcc-Z'].std().rename(columns={'tGravityAcc-X':'tGravityAcc-STD-1','tGravityAcc-Y':'tGravityAcc-STD-2','tGravityAcc-Z':'tGravityAcc-STD-3'}).drop(columns=['experimentID']))

         
        # tGravityAcc-Mad-1              
        # tGravityAcc-Mad-2              
        # tGravityAcc-Mad-3
        df_feature.append(pd.DataFrame(group['tGravityAcc-X'].apply(lambda x: median_absolute_deviation(x)).rename(columns={'tGravityAcc-X':'tGravityAcc-Mad-1'}).reset_index(drop=True)).rename(columns={0:'tGravityAcc-Mad-1'}))
        df_feature.append(pd.DataFrame(group['tGravityAcc-Y'].apply(lambda x: median_absolute_deviation(x)).rename(columns={'tGravityAcc-Y':'tGravityAcc-Mad-2'}).reset_index(drop=True)).rename(columns={0:'tGravityAcc-Mad-2'}))
        df_feature.append(pd.DataFrame(group['tGravityAcc-Z'].apply(lambda x: median_absolute_deviation(x)).rename(columns={'tGravityAcc-Z':'tGravityAcc-Mad-2'}).reset_index(drop=True)).rename(columns={0:'tGravityAcc-Mad-3'}))
          
        # tGravityAcc-Max-1              
        # tGravityAcc-Max-2              
        # tGravityAcc-Max-3
        df_feature.append(group['tGravityAcc-X','tGravityAcc-Y','tGravityAcc-Z'].max().rename(columns={'tGravityAcc-X':'tGravityAcc-Max-1','tGravityAcc-Y':'tGravityAcc-Max-2','tGravityAcc-Z':'tGravityAcc-Max-3'}).drop(columns=['experimentID']))
            
        # tGravityAcc-Min-1              
        # tGravityAcc-Min-2              
        # tGravityAcc-Min-3
        df_feature.append(group['tGravityAcc-X','tGravityAcc-Y','tGravityAcc-Z'].min().rename(columns={'tGravityAcc-X':'tGravityAcc-Min-1','tGravityAcc-Y':'tGravityAcc-Min-2','tGravityAcc-Z':'tGravityAcc-Min-3'}).drop(columns=['experimentID']))
        
        # tGravityAcc-SMA-1
        x=group['tGravityAcc-X'].apply(lambda x:list(x)).reset_index(drop=True)
        y=group['tGravityAcc-Y'].apply(lambda x:list(x)).reset_index(drop=True)
        z=group['tGravityAcc-Z'].apply(lambda x:list(x)).reset_index(drop=True)
        
        x=pd.DataFrame(x.apply(lambda lst: [abs(x) for x in lst]).apply(lambda x: sum(x)))
        y=pd.DataFrame(y.apply(lambda lst: [abs(x) for x in lst]).apply(lambda x: sum(x)))
        z=pd.DataFrame(z.apply(lambda lst: [abs(x) for x in lst]).apply(lambda x: sum(x)))
        
        sma=(x+y+z).rename(columns={0:'tGravityAcc-SMA-1'})
        df_feature.append(sma)
           
        # tGravityAcc-Energy-1           
        # tGravityAcc-Energy-2           
        # tGravityAcc-Energy-3
        a=group_square['tGravityAcc-X','tGravityAcc-Y','tGravityAcc-Z'].sum().drop(columns=['experimentID'])
        b=group['tGravityAcc-X','tGravityAcc-Y','tGravityAcc-Z'].count().drop(columns=['experimentID'])
        df_feature.append((a/b).rename(columns={'tGravityAcc-X':'tGravityAcc-Energy-1','tGravityAcc-Y':'tGravityAcc-Energy-2','tGravityAcc-Z':'tGravityAcc-Energy-3'}))
          
        # tGravityAcc-IQR-1              
        # tGravityAcc-IQR-2              
        # tGravityAcc-IQR-3
        a=group['tGravityAcc-X','tGravityAcc-Y','tGravityAcc-Z'].quantile(0.75).reset_index(drop=True)
        b=group['tGravityAcc-X','tGravityAcc-Y','tGravityAcc-Z'].quantile(0.25).reset_index(drop=True)
        df_feature.append((a-b).rename(columns={'tGravityAcc-X':'tGravityAcc-IQR-1','tGravityAcc-Y':'tGravityAcc-IQR-2','tGravityAcc-Z':'tGravityAcc-IQR-3'}))
    
        # tGravityAcc-ropy-1             
        # tGravityAcc-ropy-1             
        # tGravityAcc-ropy-1
        x=pd.DataFrame(group['tGravityAcc-X'].apply(entropy).reset_index(drop=True)).rename(columns={0:'tGravityAcc-ropy-1'})
        y=pd.DataFrame(group['tGravityAcc-Y'].apply(entropy).reset_index(drop=True)).rename(columns={0:'tGravityAcc-ropy-2'})
        z=pd.DataFrame(group['tGravityAcc-Z'].apply(entropy).reset_index(drop=True)).rename(columns={0:'tGravityAcc-ropy-3'})
        df_feature.append(x)
        df_feature.append(y)
        df_feature.append(z)
             
        # tGravityAcc-ARCoeff-1          
        # tGravityAcc-ARCoeff-2          
        # tGravityAcc-ARCoeff-3          
        # tGravityAcc-ARCoeff-4 
        a=group['tGravityAcc-X'].apply(lambda x: list(x)).drop(columns='experimentID').reset_index(drop=True)
        b=pd.DataFrame(a)
        mask=(group['tGravityAcc-X'].count()['tGravityAcc-X']>3).values.tolist()
        b_valid = b[mask]
        c=b_valid[0].apply(lambda x: _arburg2(x,4))
        d = pd.DataFrame(c)
        e=d.apply(lambda x: [y[0] for y in list(x)])
        df_feature.append(e.apply(lambda x: [y[1] for y in list(x)]).apply(lambda x: x.real).rename(columns={0:'tGravityAcc-ARCoeff-1'}))
        df_feature.append(e.apply(lambda x: [y[2] for y in list(x)]).apply(lambda x: x.real).rename(columns={0:'tGravityAcc-ARCoeff-2'}))
        df_feature.append(e.apply(lambda x: [y[3] for y in list(x)]).apply(lambda x: x.real).rename(columns={0:'tGravityAcc-ARCoeff-3'}))
        df_feature.append(e.apply(lambda x: [y[4] for y in list(x)]).apply(lambda x: x.real).rename(columns={0:'tGravityAcc-ARCoeff-4'}))
         
        # tGravityAcc-ARCoeff-5          
        # tGravityAcc-ARCoeff-6          
        # tGravityAcc-ARCoeff-7          
        # tGravityAcc-ARCoeff-8  
        a=group['tGravityAcc-Y'].apply(lambda x: list(x)).drop(columns='experimentID').reset_index(drop=True)
        b=pd.DataFrame(a)
        mask=(group['tGravityAcc-Y'].count()['tGravityAcc-Y']>3).values.tolist()
        b_valid = b[mask]
        c=b_valid[0].apply(lambda x: _arburg2(x,4))
        d = pd.DataFrame(c)
        e=d.apply(lambda x: [y[0] for y in list(x)])
        df_feature.append(e.apply(lambda x: [y[1] for y in list(x)]).apply(lambda x: x.real).rename(columns={0:'tGravityAcc-ARCoeff-5'}))
        df_feature.append(e.apply(lambda x: [y[2] for y in list(x)]).apply(lambda x: x.real).rename(columns={0:'tGravityAcc-ARCoeff-6'}))
        df_feature.append(e.apply(lambda x: [y[3] for y in list(x)]).apply(lambda x: x.real).rename(columns={0:'tGravityAcc-ARCoeff-7'}))
        df_feature.append(e.apply(lambda x: [y[4] for y in list(x)]).apply(lambda x: x.real).rename(columns={0:'tGravityAcc-ARCoeff-8'}))
        
        # tGravityAcc-ARCoeff-9          
        # tGravityAcc-ARCoeff-10         
        # tGravityAcc-ARCoeff-11         
        # tGravityAcc-ARCoeff-12         
        a=group['tGravityAcc-Z'].apply(lambda x: list(x)).drop(columns='experimentID').reset_index(drop=True)
        b=pd.DataFrame(a)
        mask=(group['tGravityAcc-Z'].count()['tGravityAcc-Z']>3).values.tolist()
        b_valid = b[mask]
        c=b_valid[0].apply(lambda x: _arburg2(x,4))
        d = pd.DataFrame(c)
        e=d.apply(lambda x: [y[0] for y in list(x)])
        df_feature.append(e.apply(lambda x: [y[1] for y in list(x)]).apply(lambda x: x.real).rename(columns={0:'tGravityAcc-ARCoeff-9'}))
        df_feature.append(e.apply(lambda x: [y[2] for y in list(x)]).apply(lambda x: x.real).rename(columns={0:'tGravityAcc-ARCoeff-10'}))
        df_feature.append(e.apply(lambda x: [y[3] for y in list(x)]).apply(lambda x: x.real).rename(columns={0:'tGravityAcc-ARCoeff-11'}))
        df_feature.append(e.apply(lambda x: [y[4] for y in list(x)]).apply(lambda x: x.real).rename(columns={0:'tGravityAcc-ARCoeff-12'}))
        
        # tGravityAcc-Correlation-1      
        # tGravityAcc-Correlation-2      
        # tGravityAcc-Correlation-3
        x=pd.DataFrame(group['tGravityAcc-X'].apply(lambda x:list(x))).reset_index(drop=True)
        y=pd.DataFrame(group['tGravityAcc-Y'].apply(lambda x:list(x))).reset_index(drop=True)
        z=pd.DataFrame(group['tGravityAcc-Z'].apply(lambda x:list(x))).reset_index(drop=True)
        
        yz=pd.concat([y,z],axis=1)
        yz.columns = ['y','z']
        yz=yz.apply(lambda row: pearsonr(row['y'],row['z']), axis=1)
        df_feature.append(pd.DataFrame(yz.apply(lambda x: x[0])).rename(columns={0:'tGravityAcc-Correlation-1'}))
        
        xz=pd.concat([x,z],axis=1)
        xz.columns = ['x','z']
        xz=xz.apply(lambda row: pearsonr(row['x'],row['z']), axis=1)
        df_feature.append(pd.DataFrame(xz.apply(lambda x: x[0])).rename(columns={0:'tGravityAcc-Correlation-2'}))

        xy=pd.concat([x,y],axis=1)
        xy.columns = ['x','y']
        xy=xy.apply(lambda row: pearsonr(row['x'],row['y']), axis=1)
        df_feature.append(pd.DataFrame(xy.apply(lambda x: x[0])).rename(columns={0:'tGravityAcc-Correlation-3'}))

        print('Processing tBodyAccJerk')
        
        tBodyAccJerkX = pd.DataFrame(group['tBodyAcc-X'].apply(lambda x: list(x)).apply(lambda row: np.diff(row)/(1/hz)).reset_index(drop=True)).rename(columns={0:'tBodyAccJerk-X'})
        tBodyAccJerkY = pd.DataFrame(group['tBodyAcc-Y'].apply(lambda x: list(x)).apply(lambda row: np.diff(row)/(1/hz)).reset_index(drop=True)).rename(columns={0:'tBodyAccJerk-Y'})
        tBodyAccJerkZ = pd.DataFrame(group['tBodyAcc-Z'].apply(lambda x: list(x)).apply(lambda row: np.diff(row)/(1/hz)).reset_index(drop=True)).rename(columns={0:'tBodyAccJerk-Z'})
        # Remove all cases where there is no data.
        tBodyAccJerkX = tBodyAccJerkX[tBodyAccJerkX['tBodyAccJerk-X'].map(len)>0]
        tBodyAccJerkY = tBodyAccJerkY[tBodyAccJerkY['tBodyAccJerk-Y'].map(len)>0]
        tBodyAccJerkZ = tBodyAccJerkZ[tBodyAccJerkZ['tBodyAccJerk-Z'].map(len)>0]
        
        # tBodyAccJerk-Mean-1       
        # tBodyAccJerk-Mean-2            
        # tBodyAccJerk-Mean-3
        df_feature.append(tBodyAccJerkX.apply(lambda row: [np.mean(y) for y in row]).rename(columns={'tBodyAccJerk-X':'tBodyAccJerk-Mean-1'}))
        df_feature.append(tBodyAccJerkY.apply(lambda row: [np.mean(y) for y in row]).rename(columns={'tBodyAccJerk-Y':'tBodyAccJerk-Mean-2'}))
        df_feature.append(tBodyAccJerkZ.apply(lambda row: [np.mean(y) for y in row]).rename(columns={'tBodyAccJerk-Z':'tBodyAccJerk-Mean-3'}))
    
        # tBodyAccJerk-STD-1                 
        # tBodyAccJerk-STD-2                 
        # tBodyAccJerk-STD-3                 
        df_feature.append(tBodyAccJerkX.apply(lambda row: [np.std(y) for y in row]).rename(columns={'tBodyAccJerk-X':'tBodyAccJerk-STD-1'}))
        df_feature.append(tBodyAccJerkY.apply(lambda row: [np.std(y) for y in row]).rename(columns={'tBodyAccJerk-Y':'tBodyAccJerk-STD-2'}))
        df_feature.append(tBodyAccJerkZ.apply(lambda row: [np.std(y) for y in row]).rename(columns={'tBodyAccJerk-Z':'tBodyAccJerk-STD-3'}))
          
        # tBodyAccJerk-Mad-1
        # tBodyAccJerk-Mad-2                 
        # tBodyAccJerk-Mad-3
        df_feature.append(tBodyAccJerkX.apply(lambda row: [mad2(y) for y in row]).rename(columns={'tBodyAccJerk-X':'tBodyAccJerk-Mad-1'}))
        df_feature.append(tBodyAccJerkY.apply(lambda row: [mad2(y) for y in row]).rename(columns={'tBodyAccJerk-Y':'tBodyAccJerk-Mad-2'}))
        df_feature.append(tBodyAccJerkZ.apply(lambda row: [mad2(y) for y in row]).rename(columns={'tBodyAccJerk-Z':'tBodyAccJerk-Mad-3'}))
              
        # tBodyAccJerk-Max-1
        # tBodyAccJerk-Max-2                 
        # tBodyAccJerk-Max-3
        df_feature.append(tBodyAccJerkX.apply(lambda x: [np.sort(y)[-1:].sum() for y in x]).rename(columns={'tBodyAccJerk-X':'tBodyJerk-Max-1'}))
        df_feature.append(tBodyAccJerkY.apply(lambda x: [np.sort(y)[-1:].sum() for y in x]).rename(columns={'tBodyAccJerk-Y':'tBodyJerk-Max-2'}))
        df_feature.append(tBodyAccJerkZ.apply(lambda x: [np.sort(y)[-1:].sum() for y in x]).rename(columns={'tBodyAccJerk-Z':'tBodyJerk-Max-3'}))
        
        # tBodyAccJerk-Min-1                 
        # tBodyAccJerk-Min-2                 
        # tBodyAccJerk-Min-3                 
        df_feature.append(tBodyAccJerkX.apply(lambda x: [np.sort(y)[:1].sum() for y in x]).rename(columns={'tBodyAccJerk-X':'tBodyJerk-Min-1'}))
        df_feature.append(tBodyAccJerkY.apply(lambda x: [np.sort(y)[:1].sum() for y in x]).rename(columns={'tBodyAccJerk-Y':'tBodyJerk-Min-2'}))
        df_feature.append(tBodyAccJerkZ.apply(lambda x: [np.sort(y)[:1].sum() for y in x]).rename(columns={'tBodyAccJerk-Z':'tBodyJerk-Min-3'}))

        # tBodyAccJerk-SMA-1
        x=tBodyAccJerkX.apply(lambda lst: [sum(abs(x)) for x in lst])
        y=tBodyAccJerkX.apply(lambda lst: [sum(abs(x)) for x in lst])
        z=tBodyAccJerkX.apply(lambda lst: [sum(abs(x)) for x in lst])
        sma=(x+y+z).rename(columns={'tBodyAccJerk-X':'tBodyAccJerk-SMA-1'})
        df_feature.append(sma)
          
        # tBodyAccJerk-Energy-1          
        # tBodyAccJerk-Energy-2          
        # tBodyAccJerk-Energy-3 
        x=(tBodyAccJerkX**2).apply(lambda lst: [sum(x)/len(x) for x in lst]).rename(columns={'tBodyAccJerk-X':'tBodyJerk-Energy-1'})
        y=(tBodyAccJerkY**2).apply(lambda lst: [sum(x)/len(x) for x in lst]).rename(columns={'tBodyAccJerk-Y':'tBodyJerk-Energy-2'})
        z=(tBodyAccJerkZ**2).apply(lambda lst: [sum(x)/len(x) for x in lst]).rename(columns={'tBodyAccJerk-Z':'tBodyJerk-Energy-3'})
        df_feature.append(x)
        df_feature.append(y)
        df_feature.append(z)
        
        # tBodyAccJerk-IQR-1             
        # tBodyAccJerk-IQR-2             
        # tBodyAccJerk-IQR-3
        x=pd.DataFrame(tBodyAccJerkX['tBodyAccJerk-X'].apply(lambda x: np.percentile(x,75)-np.percentile(x,25))).rename(columns={'tBodyAccJerk-X':'tBodyJerk-IQR-1'})
        y=pd.DataFrame(tBodyAccJerkY['tBodyAccJerk-Y'].apply(lambda x: np.percentile(x,75)-np.percentile(x,25))).rename(columns={'tBodyAccJerk-Y':'tBodyJerk-IQR-2'})
        z=pd.DataFrame(tBodyAccJerkZ['tBodyAccJerk-Z'].apply(lambda x: np.percentile(x,75)-np.percentile(x,25))).rename(columns={'tBodyAccJerk-Z':'tBodyJerk-IQR-3'})
        df_feature.append(x)
        df_feature.append(y)
        df_feature.append(z)
           
        # tBodyAccJerk-ropy-1            
        # tBodyAccJerk-ropy-2            
        # tBodyAccJerk-ropy-3
        x=pd.DataFrame(tBodyAccJerkX['tBodyAccJerk-X'].apply(lambda x: entropy(x))).rename(columns={'tBodyAccJerk-X':'tBodyAccJerk-ropy-1'})
        y=pd.DataFrame(tBodyAccJerkY['tBodyAccJerk-Y'].apply(lambda x: entropy(x))).rename(columns={'tBodyAccJerk-Y':'tBodyAccJerk-ropy-2'})
        z=pd.DataFrame(tBodyAccJerkZ['tBodyAccJerk-Z'].apply(lambda x: entropy(x))).rename(columns={'tBodyAccJerk-Z':'tBodyAccJerk-ropy-3'})
        df_feature.append(x)
        df_feature.append(y)
        df_feature.append(z)
         
        # tBodyAccJerk-ARCoeff-1         
        # tBodyAccJerk-ARCoeff-2         
        # tBodyAccJerk-ARCoeff-3         
        # tBodyAccJerk-ARCoeff-4
        mask=tBodyAccJerkX.apply(lambda lst: [len(x) for x in lst])>3
        # This will just return NaN values for too small of sample sizes
        valid=tBodyAccJerkX[mask].dropna()
        c=valid.apply(lambda lst: [_arburg2(x,4) for x in lst])
        d = pd.DataFrame(c)
        e=d.apply(lambda x: [y[0] for y in list(x)])
        df_feature.append(e.apply(lambda x: [y[1] for y in list(x)]).apply(lambda x: x.real).rename(columns={'tBodyAccJerk-X':'tBodyAccJerk-ARCoeff-1'}))
        df_feature.append(e.apply(lambda x: [y[2] for y in list(x)]).apply(lambda x: x.real).rename(columns={'tBodyAccJerk-X':'tBodyAccJerk-ARCoeff-2'}))
        df_feature.append(e.apply(lambda x: [y[3] for y in list(x)]).apply(lambda x: x.real).rename(columns={'tBodyAccJerk-X':'tBodyAccJerk-ARCoeff-3'}))
        df_feature.append(e.apply(lambda x: [y[4] for y in list(x)]).apply(lambda x: x.real).rename(columns={'tBodyAccJerk-X':'tBodyAccJerk-ARCoeff-4'}))
        
        # tBodyAccJerk-ARCoeff-5         
        # tBodyAccJerk-ARCoeff-6         
        # tBodyAccJerk-ARCoeff-7         
        # tBodyAccJerk-ARCoeff-8
        mask=tBodyAccJerkY.apply(lambda lst: [len(x) for x in lst])>3
        # This will just return NaN values for too small of sample sizes
        valid=tBodyAccJerkY[mask].dropna()
        c=valid.apply(lambda lst: [_arburg2(x,4) for x in lst])
        d = pd.DataFrame(c)
        e=d.apply(lambda x: [y[0] for y in list(x)])
        df_feature.append(e.apply(lambda x: [y[1] for y in list(x)]).apply(lambda x: x.real).rename(columns={'tBodyAccJerk-Y':'tBodyAccJerk-ARCoeff-5'}))
        df_feature.append(e.apply(lambda x: [y[2] for y in list(x)]).apply(lambda x: x.real).rename(columns={'tBodyAccJerk-Y':'tBodyAccJerk-ARCoeff-6'}))
        df_feature.append(e.apply(lambda x: [y[3] for y in list(x)]).apply(lambda x: x.real).rename(columns={'tBodyAccJerk-Y':'tBodyAccJerk-ARCoeff-7'}))
        df_feature.append(e.apply(lambda x: [y[4] for y in list(x)]).apply(lambda x: x.real).rename(columns={'tBodyAccJerk-Y':'tBodyAccJerk-ARCoeff-8'}))
        
        # tBodyAccJerk-ARCoeff-9         
        # tBodyAccJerk-ARCoeff-10        
        # tBodyAccJerk-ARCoeff-11        
        # tBodyAccJerk-ARCoeff-12        
        mask=tBodyAccJerkZ.apply(lambda lst: [len(x) for x in lst])>3
        # This will just return NaN values for too small of sample sizes
        valid=tBodyAccJerkZ[mask].dropna()
        c=valid.apply(lambda lst: [_arburg2(x,4) for x in lst])
        d = pd.DataFrame(c)
        e=d.apply(lambda x: [y[0] for y in list(x)])
        df_feature.append(e.apply(lambda x: [y[1] for y in list(x)]).apply(lambda x: x.real).rename(columns={'tBodyAccJerk-Z':'tBodyAccJerk-ARCoeff-9'}))
        df_feature.append(e.apply(lambda x: [y[2] for y in list(x)]).apply(lambda x: x.real).rename(columns={'tBodyAccJerk-Z':'tBodyAccJerk-ARCoeff-10'}))
        df_feature.append(e.apply(lambda x: [y[3] for y in list(x)]).apply(lambda x: x.real).rename(columns={'tBodyAccJerk-Z':'tBodyAccJerk-ARCoeff-11'}))
        df_feature.append(e.apply(lambda x: [y[4] for y in list(x)]).apply(lambda x: x.real).rename(columns={'tBodyAccJerk-Z':'tBodyAccJerk-ARCoeff-12'}))

        # tBodyAccJerk-Correlation-1     
        # tBodyAccJerk-Correlation-2     
        # tBodyAccJerk-Correlation-3
        x=tBodyAccJerkX
        y=tBodyAccJerkY
        z=tBodyAccJerkZ
        
        yz=pd.concat([y,z],axis=1)
        yz.columns = ['y','z']
        yz=yz.apply(lambda row: pearsonr(row['y'],row['z']), axis=1)
        df_feature.append(pd.DataFrame(yz.apply(lambda x: x[0])).rename(columns={0:'tBodyAccJerk-Correlation-1'}))
        
        xz=pd.concat([x,z],axis=1)
        xz.columns = ['x','z']
        xz=xz.apply(lambda row: pearsonr(row['x'],row['z']), axis=1)
        df_feature.append(pd.DataFrame(xz.apply(lambda x: x[0])).rename(columns={0:'tBodyAccJerk-Correlation-2'}))

        xy=pd.concat([x,y],axis=1)
        xy.columns = ['x','y']
        xy=xy.apply(lambda row: pearsonr(row['x'],row['y']), axis=1)
        df_feature.append(pd.DataFrame(xy.apply(lambda x: x[0])).rename(columns={0:'tBodyAccJerk-Correlation-3'}))

        print('Processing tBodyGyro')
        
        # tBodyGyro-Mean-1
        # tBodyGyro-Mean-2                
        # tBodyGyro-Mean-3
        df_feature.append(group['tBodyGyro-X','tBodyGyro-Y','tBodyGyro-Z'].mean().rename(columns={'tBodyGyro-X':'tBodyGyro-Mean-1','tBodyGyro-Y':'tBodyGyro-Mean-2','tBodyGyro-Z':'tBodyGyro-Mean-3'}).drop(columns=['experimentID']))

        # tBodyGyro-STD-1                 
        # tBodyGyro-STD-2                 
        # tBodyGyro-STD-3                 
        df_feature.append(group['tBodyGyro-X','tBodyGyro-Y','tBodyGyro-Z'].std().rename(columns={'tBodyGyro-X':'tBodyGyro-STD-1','tBodyGyro-Y':'tBodyGyro-STD-2','tBodyGyro-Z':'tBodyGyro-STD-3'}).drop(columns=['experimentID']))
          
        # tBodyGyro-Mad-1
        # tBodyGyro-Mad-2                 
        # tBodyGyro-Mad-3                 
        df_feature.append(pd.DataFrame(group['tBodyGyro-X'].apply(lambda x: median_absolute_deviation(x)).rename(columns={'tBodyGyro-X':'tBodyGyro-Mad-1'}).reset_index(drop=True)).rename(columns={0:'tBodyGyro-Mad-1'}))
        df_feature.append(pd.DataFrame(group['tBodyGyro-Y'].apply(lambda x: median_absolute_deviation(x)).rename(columns={'tBodyGyro-Y':'tBodyGyro-Mad-2'}).reset_index(drop=True)).rename(columns={0:'tBodyGyro-Mad-2'}))
        df_feature.append(pd.DataFrame(group['tBodyGyro-Z'].apply(lambda x: median_absolute_deviation(x)).rename(columns={'tBodyGyro-Z':'tBodyGyro-Mad-2'}).reset_index(drop=True)).rename(columns={0:'tBodyGyro-Mad-3'}))

        # tBodyGyro-Max-1
        # tBodyGyro-Max-2                 
        # tBodyGyro-Max-3                 
        df_feature.append(group['tBodyGyro-X','tBodyGyro-Y','tBodyGyro-Z'].max().rename(columns={'tBodyGyro-X':'tBodyGyro-Max-1','tBodyGyro-Y':'tBodyGyro-Max-2','tBodyGyro-Z':'tBodyGyro-Max-3'}).drop(columns=['experimentID']))

        # tBodyGyro-Min-1                 
        # tBodyGyro-Min-2                 
        # tBodyGyro-Min-3                 
        df_feature.append(group['tBodyGyro-X','tBodyGyro-Y','tBodyGyro-Z'].min().rename(columns={'tBodyGyro-X':'tBodyGyro-Min-1','tBodyGyro-Y':'tBodyGyro-Min-2','tBodyGyro-Z':'tBodyGyro-Min-3'}).drop(columns=['experimentID']))
        
        # tBodyGyro-SMA-1
        x=group['tBodyGyro-X'].apply(lambda x:list(x)).reset_index(drop=True)
        y=group['tBodyGyro-Y'].apply(lambda x:list(x)).reset_index(drop=True)
        z=group['tBodyGyro-Z'].apply(lambda x:list(x)).reset_index(drop=True)
        
        x=pd.DataFrame(x.apply(lambda lst: [abs(x) for x in lst]).apply(lambda x: sum(x)))
        y=pd.DataFrame(y.apply(lambda lst: [abs(x) for x in lst]).apply(lambda x: sum(x)))
        z=pd.DataFrame(z.apply(lambda lst: [abs(x) for x in lst]).apply(lambda x: sum(x)))
        
        sma=(x+y+z).rename(columns={0:'tBodyGyro-SMA-1'})
        df_feature.append(sma)
        
        # tBodyGyro-Energy-1
        # tBodyGyro-Energy-2              
        # tBodyGyro-Energy-3
        a=group_square['tBodyGyro-X','tBodyGyro-Y','tBodyGyro-Z'].sum().drop(columns=['experimentID'])
        b=group['tBodyGyro-X','tBodyGyro-Y','tBodyGyro-Z'].count().drop(columns=['experimentID'])
        df_feature.append((a/b).rename(columns={'tBodyGyro-X':'tBodyGyro-Energy-1','tBodyGyro-Y':'tBodyGyro-Energy-2','tBodyGyro-Z':'tBodyGyro-Energy-3'}))
        
        # tBodyGyro-IQR-1         
        # tBodyGyro-IQR-2                 
        # tBodyGyro-IQR-3      
        a=group['tBodyGyro-X','tBodyGyro-Y','tBodyGyro-Z'].quantile(0.75).reset_index(drop=True)
        b=group['tBodyGyro-X','tBodyGyro-Y','tBodyGyro-Z'].quantile(0.25).reset_index(drop=True)
        df_feature.append((a-b).rename(columns={'tBodyGyro-X':'tBodyGyro-IQR-1','tBodyGyro-Y':'tBodyGyro-IQR-2','tBodyGyro-Z':'tBodyGyro-IQR-3'}))
        
        # tBodyGyro-ropy-1                
        # tBodyGyro-ropy-1                
        # tBodyGyro-ropy-1   
        x=pd.DataFrame(group['tBodyGyro-X'].apply(entropy).reset_index(drop=True)).rename(columns={0:'tBodyGyro-ropy-1'})
        y=pd.DataFrame(group['tBodyGyro-Y'].apply(entropy).reset_index(drop=True)).rename(columns={0:'tBodyGyro-ropy-2'})
        z=pd.DataFrame(group['tBodyGyro-Z'].apply(entropy).reset_index(drop=True)).rename(columns={0:'tBodyGyro-ropy-3'})
        df_feature.append(x)
        df_feature.append(y)
        df_feature.append(z)

        # tBodyGyro-ARCoeff-1             
        # tBodyGyro-ARCoeff-2             
        # tBodyGyro-ARCoeff-3             
        # tBodyGyro-ARCoeff-4    
        a=group['tBodyGyro-X'].apply(lambda x: list(x)).drop(columns='experimentID').reset_index(drop=True)
        b=pd.DataFrame(a)
        mask=(group['tBodyGyro-X'].count()['tBodyGyro-X']>3).values.tolist()
        b_valid = b[mask]
        c=b_valid[0].apply(lambda x: _arburg2(x,4))
        d = pd.DataFrame(c)
        e=d.apply(lambda x: [y[0] for y in list(x)])
        df_feature.append(e.apply(lambda x: [y[1] for y in list(x)]).apply(lambda x: x.real).rename(columns={0:'tBodyGyro-ARCoeff-1'}))
        df_feature.append(e.apply(lambda x: [y[2] for y in list(x)]).apply(lambda x: x.real).rename(columns={0:'tBodyGyro-ARCoeff-2'}))
        df_feature.append(e.apply(lambda x: [y[3] for y in list(x)]).apply(lambda x: x.real).rename(columns={0:'tBodyGyro-ARCoeff-3'}))
        df_feature.append(e.apply(lambda x: [y[4] for y in list(x)]).apply(lambda x: x.real).rename(columns={0:'tBodyGyro-ARCoeff-4'}))
        
        # tBodyGyro-ARCoeff-5             
        # tBodyGyro-ARCoeff-6             
        # tBodyGyro-ARCoeff-7             
        # tBodyGyro-ARCoeff-8
        a=group['tBodyGyro-Y'].apply(lambda x: list(x)).drop(columns='experimentID').reset_index(drop=True)
        b=pd.DataFrame(a)
        mask=(group['tBodyGyro-Y'].count()['tBodyGyro-Y']>3).values.tolist()
        b_valid = b[mask]
        c=b_valid[0].apply(lambda x: _arburg2(x,4))
        d = pd.DataFrame(c)
        e=d.apply(lambda x: [y[0] for y in list(x)])
        df_feature.append(e.apply(lambda x: [y[1] for y in list(x)]).apply(lambda x: x.real).rename(columns={0:'tBodyGyro-ARCoeff-5'}))
        df_feature.append(e.apply(lambda x: [y[2] for y in list(x)]).apply(lambda x: x.real).rename(columns={0:'tBodyGyro-ARCoeff-6'}))
        df_feature.append(e.apply(lambda x: [y[3] for y in list(x)]).apply(lambda x: x.real).rename(columns={0:'tBodyGyro-ARCoeff-7'}))
        df_feature.append(e.apply(lambda x: [y[4] for y in list(x)]).apply(lambda x: x.real).rename(columns={0:'tBodyGyro-ARCoeff-8'}))        

        # tBodyGyro-ARCoeff-9             
        # tBodyGyro-ARCoeff-10            
        # tBodyGyro-ARCoeff-11            
        # tBodyGyro-ARCoeff-12
        a=group['tBodyGyro-Z'].apply(lambda x: list(x)).drop(columns='experimentID').reset_index(drop=True)
        b=pd.DataFrame(a)
        mask=(group['tBodyGyro-Z'].count()['tBodyGyro-Z']>3).values.tolist()
        b_valid = b[mask]
        c=b_valid[0].apply(lambda x: _arburg2(x,4))
        d = pd.DataFrame(c)
        e=d.apply(lambda x: [y[0] for y in list(x)])
        df_feature.append(e.apply(lambda x: [y[1] for y in list(x)]).apply(lambda x: x.real).rename(columns={0:'tBodyGyro-ARCoeff-9'}))
        df_feature.append(e.apply(lambda x: [y[2] for y in list(x)]).apply(lambda x: x.real).rename(columns={0:'tBodyGyro-ARCoeff-10'}))
        df_feature.append(e.apply(lambda x: [y[3] for y in list(x)]).apply(lambda x: x.real).rename(columns={0:'tBodyGyro-ARCoeff-11'}))
        df_feature.append(e.apply(lambda x: [y[4] for y in list(x)]).apply(lambda x: x.real).rename(columns={0:'tBodyGyro-ARCoeff-12'}))
        
        # tBodyGyro-Correlation-1         
        # tBodyGyro-Correlation-2         
        # tBodyGyro-Correlation-3
        x=pd.DataFrame(group['tBodyGyro-X'].apply(lambda x:list(x))).reset_index(drop=True)
        y=pd.DataFrame(group['tBodyGyro-Y'].apply(lambda x:list(x))).reset_index(drop=True)
        z=pd.DataFrame(group['tBodyGyro-Z'].apply(lambda x:list(x))).reset_index(drop=True)
        
        yz=pd.concat([y,z],axis=1)
        yz.columns = ['y','z']
        yz=yz.apply(lambda row: pearsonr(row['y'],row['z']), axis=1)
        df_feature.append(pd.DataFrame(yz.apply(lambda x: x[0])).rename(columns={0:'tBodyGyro-Correlation-1'}))
        
        xz=pd.concat([x,z],axis=1)
        xz.columns = ['x','z']
        xz=xz.apply(lambda row: pearsonr(row['x'],row['z']), axis=1)
        df_feature.append(pd.DataFrame(xz.apply(lambda x: x[0])).rename(columns={0:'tBodyGyro-Correlation-2'}))

        xy=pd.concat([x,y],axis=1)
        xy.columns = ['x','y']
        xy=xy.apply(lambda row: pearsonr(row['x'],row['y']), axis=1)
        df_feature.append(pd.DataFrame(xy.apply(lambda x: x[0])).rename(columns={0:'tBodyGyro-Correlation-3'}))      
    
        print('Processing tBodyGyroJerk')
     
        tBodyGyroJerkX = pd.DataFrame(group['tBodyGyro-X'].apply(lambda x: list(x)).apply(lambda row: np.diff(row)/(1/hz)).reset_index(drop=True)).rename(columns={0:'tBodyGyroJerk-X'})
        tBodyGyroJerkY = pd.DataFrame(group['tBodyGyro-Y'].apply(lambda x: list(x)).apply(lambda row: np.diff(row)/(1/hz)).reset_index(drop=True)).rename(columns={0:'tBodyGyroJerk-Y'})
        tBodyGyroJerkZ = pd.DataFrame(group['tBodyGyro-Z'].apply(lambda x: list(x)).apply(lambda row: np.diff(row)/(1/hz)).reset_index(drop=True)).rename(columns={0:'tBodyGyroJerk-Z'})
        # Remove all cases where there is no data.
        tBodyGyroJerkX = tBodyGyroJerkX[tBodyGyroJerkX['tBodyGyroJerk-X'].map(len)>0]
        tBodyGyroJerkY = tBodyGyroJerkY[tBodyGyroJerkY['tBodyGyroJerk-Y'].map(len)>0]
        tBodyGyroJerkZ = tBodyGyroJerkZ[tBodyGyroJerkZ['tBodyGyroJerk-Z'].map(len)>0]
        
        # tBodyGyroJerk-Mean-1       
        # tBodyGyroJerk-Mean-2            
        # tBodyGyroJerk-Mean-3
        df_feature.append(tBodyGyroJerkX.apply(lambda row: [np.mean(y) for y in row]).rename(columns={'tBodyGyroJerk-X':'tBodyGyroJerk-Mean-1'}))
        df_feature.append(tBodyGyroJerkY.apply(lambda row: [np.mean(y) for y in row]).rename(columns={'tBodyGyroJerk-Y':'tBodyGyroJerk-Mean-2'}))
        df_feature.append(tBodyGyroJerkZ.apply(lambda row: [np.mean(y) for y in row]).rename(columns={'tBodyGyroJerk-Z':'tBodyGyroJerk-Mean-3'}))
    
        # tBodyGyroJerk-STD-1                 
        # tBodyGyroJerk-STD-2                 
        # tBodyGyroJerk-STD-3                 
        df_feature.append(tBodyGyroJerkX.apply(lambda row: [np.std(y) for y in row]).rename(columns={'tBodyGyroJerk-X':'tBodyGyroJerk-STD-1'}))
        df_feature.append(tBodyGyroJerkY.apply(lambda row: [np.std(y) for y in row]).rename(columns={'tBodyGyroJerk-Y':'tBodyGyroJerk-STD-2'}))
        df_feature.append(tBodyGyroJerkZ.apply(lambda row: [np.std(y) for y in row]).rename(columns={'tBodyGyroJerk-Z':'tBodyGyroJerk-STD-3'}))
          
        # tBodyGyroJerk-Mad-1
        # tBodyGyroJerk-Mad-2                 
        # tBodyGyroJerk-Mad-3
        df_feature.append(tBodyGyroJerkX.apply(lambda row: [mad2(y) for y in row]).rename(columns={'tBodyGyroJerk-X':'tBodyGyroJerk-Mad-1'}))
        df_feature.append(tBodyGyroJerkY.apply(lambda row: [mad2(y) for y in row]).rename(columns={'tBodyGyroJerk-Y':'tBodyGyroJerk-Mad-2'}))
        df_feature.append(tBodyGyroJerkZ.apply(lambda row: [mad2(y) for y in row]).rename(columns={'tBodyGyroJerk-Z':'tBodyGyroJerk-Mad-3'}))
              
        # tBodyGyroJerk-Max-1
        # tBodyGyroJerk-Max-2                 
        # tBodyGyroJerk-Max-3
        df_feature.append(tBodyGyroJerkX.apply(lambda x: [np.sort(y)[-1:].sum() for y in x]).rename(columns={'tBodyGyroJerk-X':'tBodyJerk-Max-1'}))
        df_feature.append(tBodyGyroJerkY.apply(lambda x: [np.sort(y)[-1:].sum() for y in x]).rename(columns={'tBodyGyroJerk-Y':'tBodyJerk-Max-2'}))
        df_feature.append(tBodyGyroJerkZ.apply(lambda x: [np.sort(y)[-1:].sum() for y in x]).rename(columns={'tBodyGyroJerk-Z':'tBodyJerk-Max-3'}))
        
        # tBodyGyroJerk-Min-1                 
        # tBodyGyroJerk-Min-2                 
        # tBodyGyroJerk-Min-3                 
        df_feature.append(tBodyGyroJerkX.apply(lambda x: [np.sort(y)[:1].sum() for y in x]).rename(columns={'tBodyGyroJerk-X':'tBodyJerk-Min-1'}))
        df_feature.append(tBodyGyroJerkY.apply(lambda x: [np.sort(y)[:1].sum() for y in x]).rename(columns={'tBodyGyroJerk-Y':'tBodyJerk-Min-2'}))
        df_feature.append(tBodyGyroJerkZ.apply(lambda x: [np.sort(y)[:1].sum() for y in x]).rename(columns={'tBodyGyroJerk-Z':'tBodyJerk-Min-3'}))

        # tBodyGyroJerk-SMA-1
        x=tBodyGyroJerkX.apply(lambda lst: [sum(abs(x)) for x in lst])
        y=tBodyGyroJerkX.apply(lambda lst: [sum(abs(x)) for x in lst])
        z=tBodyGyroJerkX.apply(lambda lst: [sum(abs(x)) for x in lst])
        sma=(x+y+z).rename(columns={'tBodyGyroJerk-X':'tBodyGyroJerk-SMA-1'})
        df_feature.append(sma)
          
        # tBodyGyroJerk-Energy-1          
        # tBodyGyroJerk-Energy-2          
        # tBodyGyroJerk-Energy-3 
        x=(tBodyGyroJerkX**2).apply(lambda lst: [sum(x)/len(x) for x in lst]).rename(columns={'tBodyGyroJerk-X':'tBodyJerk-Energy-1'})
        y=(tBodyGyroJerkY**2).apply(lambda lst: [sum(x)/len(x) for x in lst]).rename(columns={'tBodyGyroJerk-Y':'tBodyJerk-Energy-2'})
        z=(tBodyGyroJerkZ**2).apply(lambda lst: [sum(x)/len(x) for x in lst]).rename(columns={'tBodyGyroJerk-Z':'tBodyJerk-Energy-3'})
        df_feature.append(x)
        df_feature.append(y)
        df_feature.append(z)
        
        # tBodyGyroJerk-IQR-1             
        # tBodyGyroJerk-IQR-2             
        # tBodyGyroJerk-IQR-3
        x=pd.DataFrame(tBodyGyroJerkX['tBodyGyroJerk-X'].apply(lambda x: np.percentile(x,75)-np.percentile(x,25))).rename(columns={'tBodyGyroJerk-X':'tBodyJerk-IQR-1'})
        y=pd.DataFrame(tBodyGyroJerkY['tBodyGyroJerk-Y'].apply(lambda x: np.percentile(x,75)-np.percentile(x,25))).rename(columns={'tBodyGyroJerk-Y':'tBodyJerk-IQR-2'})
        z=pd.DataFrame(tBodyGyroJerkZ['tBodyGyroJerk-Z'].apply(lambda x: np.percentile(x,75)-np.percentile(x,25))).rename(columns={'tBodyGyroJerk-Z':'tBodyJerk-IQR-3'})
        df_feature.append(x)
        df_feature.append(y)
        df_feature.append(z)
           
        # tBodyGyroJerk-ropy-1            
        # tBodyGyroJerk-ropy-2            
        # tBodyGyroJerk-ropy-3
        x=pd.DataFrame(tBodyGyroJerkX['tBodyGyroJerk-X'].apply(lambda x: entropy(x))).rename(columns={'tBodyGyroJerk-X':'tBodyGyroJerk-ropy-1'})
        y=pd.DataFrame(tBodyGyroJerkY['tBodyGyroJerk-Y'].apply(lambda x: entropy(x))).rename(columns={'tBodyGyroJerk-Y':'tBodyGyroJerk-ropy-2'})
        z=pd.DataFrame(tBodyGyroJerkZ['tBodyGyroJerk-Z'].apply(lambda x: entropy(x))).rename(columns={'tBodyGyroJerk-Z':'tBodyGyroJerk-ropy-3'})
        df_feature.append(x)
        df_feature.append(y)
        df_feature.append(z)
         
        # tBodyGyroJerk-ARCoeff-1         
        # tBodyGyroJerk-ARCoeff-2         
        # tBodyGyroJerk-ARCoeff-3         
        # tBodyGyroJerk-ARCoeff-4
        mask=tBodyGyroJerkX.apply(lambda lst: [len(x) for x in lst])>3
        # This will just return NaN values for too small of sample sizes
        valid=tBodyGyroJerkX[mask].dropna()
        c=valid.apply(lambda lst: [_arburg2(x,4) for x in lst])
        d = pd.DataFrame(c)
        e=d.apply(lambda x: [y[0] for y in list(x)])
        df_feature.append(e.apply(lambda x: [y[1] for y in list(x)]).apply(lambda x: x.real).rename(columns={'tBodyGyroJerk-X':'tBodyGyroJerk-ARCoeff-1'}))
        df_feature.append(e.apply(lambda x: [y[2] for y in list(x)]).apply(lambda x: x.real).rename(columns={'tBodyGyroJerk-X':'tBodyGyroJerk-ARCoeff-2'}))
        df_feature.append(e.apply(lambda x: [y[3] for y in list(x)]).apply(lambda x: x.real).rename(columns={'tBodyGyroJerk-X':'tBodyGyroJerk-ARCoeff-3'}))
        df_feature.append(e.apply(lambda x: [y[4] for y in list(x)]).apply(lambda x: x.real).rename(columns={'tBodyGyroJerk-X':'tBodyGyroJerk-ARCoeff-4'}))
        
        # tBodyGyroJerk-ARCoeff-5         
        # tBodyGyroJerk-ARCoeff-6         
        # tBodyGyroJerk-ARCoeff-7         
        # tBodyGyroJerk-ARCoeff-8
        mask=tBodyGyroJerkY.apply(lambda lst: [len(x) for x in lst])>3
        # This will just return NaN values for too small of sample sizes
        valid=tBodyGyroJerkY[mask].dropna()
        c=valid.apply(lambda lst: [_arburg2(x,4) for x in lst])
        d = pd.DataFrame(c)
        e=d.apply(lambda x: [y[0] for y in list(x)])
        df_feature.append(e.apply(lambda x: [y[1] for y in list(x)]).apply(lambda x: x.real).rename(columns={'tBodyGyroJerk-Y':'tBodyGyroJerk-ARCoeff-5'}))
        df_feature.append(e.apply(lambda x: [y[2] for y in list(x)]).apply(lambda x: x.real).rename(columns={'tBodyGyroJerk-Y':'tBodyGyroJerk-ARCoeff-6'}))
        df_feature.append(e.apply(lambda x: [y[3] for y in list(x)]).apply(lambda x: x.real).rename(columns={'tBodyGyroJerk-Y':'tBodyGyroJerk-ARCoeff-7'}))
        df_feature.append(e.apply(lambda x: [y[4] for y in list(x)]).apply(lambda x: x.real).rename(columns={'tBodyGyroJerk-Y':'tBodyGyroJerk-ARCoeff-8'}))
        
        # tBodyGyroJerk-ARCoeff-9         
        # tBodyGyroJerk-ARCoeff-10        
        # tBodyGyroJerk-ARCoeff-11        
        # tBodyGyroJerk-ARCoeff-12        
        mask=tBodyGyroJerkZ.apply(lambda lst: [len(x) for x in lst])>3
        # This will just return NaN values for too small of sample sizes
        valid=tBodyGyroJerkZ[mask].dropna()
        c=valid.apply(lambda lst: [_arburg2(x,4) for x in lst])
        d = pd.DataFrame(c)
        e=d.apply(lambda x: [y[0] for y in list(x)])
        df_feature.append(e.apply(lambda x: [y[1] for y in list(x)]).apply(lambda x: x.real).rename(columns={'tBodyGyroJerk-Z':'tBodyGyroJerk-ARCoeff-9'}))
        df_feature.append(e.apply(lambda x: [y[2] for y in list(x)]).apply(lambda x: x.real).rename(columns={'tBodyGyroJerk-Z':'tBodyGyroJerk-ARCoeff-10'}))
        df_feature.append(e.apply(lambda x: [y[3] for y in list(x)]).apply(lambda x: x.real).rename(columns={'tBodyGyroJerk-Z':'tBodyGyroJerk-ARCoeff-11'}))
        df_feature.append(e.apply(lambda x: [y[4] for y in list(x)]).apply(lambda x: x.real).rename(columns={'tBodyGyroJerk-Z':'tBodyGyroJerk-ARCoeff-12'}))

        # tBodyGyroJerk-Correlation-1     
        # tBodyGyroJerk-Correlation-2     
        # tBodyGyroJerk-Correlation-3
        x=tBodyGyroJerkX
        y=tBodyGyroJerkY
        z=tBodyGyroJerkZ
        
        yz=pd.concat([y,z],axis=1)
        yz.columns = ['y','z']
        yz=yz.apply(lambda row: pearsonr(row['y'],row['z']), axis=1)
        df_feature.append(pd.DataFrame(yz.apply(lambda x: x[0])).rename(columns={0:'tBodyGyroJerk-Correlation-1'}))
        
        xz=pd.concat([x,z],axis=1)
        xz.columns = ['x','z']
        xz=xz.apply(lambda row: pearsonr(row['x'],row['z']), axis=1)
        df_feature.append(pd.DataFrame(xz.apply(lambda x: x[0])).rename(columns={0:'tBodyGyroJerk-Correlation-2'}))

        xy=pd.concat([x,y],axis=1)
        xy.columns = ['x','y']
        xy=xy.apply(lambda row: pearsonr(row['x'],row['y']), axis=1)
        df_feature.append(pd.DataFrame(xy.apply(lambda x: x[0])).rename(columns={0:'tBodyGyroJerk-Correlation-3'}))

        print('Processing tBodyAccMag')
        # tBodyAccMag-Mean-1             
        # tBodyAccMag-STD-1              
        # tBodyAccMag-Mad-1              
        # tBodyAccMag-Max-1              
        # tBodyAccMag-Min-1              
        # tBodyAccMag-SMA-1              
        # tBodyAccMag-Energy-1           
        # tBodyAccMag-IQR-1              
        # tBodyAccMag-ropy-1             
        # tBodyAccMag-ARCoeff-1          
        # tBodyAccMag-ARCoeff-2          
        # tBodyAccMag-ARCoeff-3          
        # tBodyAccMag-ARCoeff-4     
        
        print('Processing tGravityAccMag')
        # tGravityAccMag-Mean-1          
        # tGravityAccMag-STD-1           
        # tGravityAccMag-Mad-1           
        # tGravityAccMag-Max-1           
        # tGravityAccMag-Min-1           
        # tGravityAccMag-SMA-1           
        # tGravityAccMag-Energy-1        
        # tGravityAccMag-IQR-1           
        # tGravityAccMag-ropy-1          
        # tGravityAccMag-ARCoeff-1       
        # tGravityAccMag-ARCoeff-2       
        # tGravityAccMag-ARCoeff-3       
        # tGravityAccMag-ARCoeff-4
    
        print('Processing tBodyAccJerkMag')    
        # tBodyAccJerkMag-Mean-1         
        # tBodyAccJerkMag-STD-1          
        # tBodyAccJerkMag-Mad-1          
        # tBodyAccJerkMag-Max-1          
        # tBodyAccJerkMag-Min-1          
        # tBodyAccJerkMag-SMA-1          
        # tBodyAccJerkMag-Energy-1       
        # tBodyAccJerkMag-IQR-1          
        # tBodyAccJerkMag-ropy-1         
        # tBodyAccJerkMag-ARCoeff-1      
        # tBodyAccJerkMag-ARCoeff-2      
        # tBodyAccJerkMag-ARCoeff-3      
        # tBodyAccJerkMag-ARCoeff-4     
        
        print('Processing tBodyGyroMag')
        # tBodyGyroMag-Mean-1            
        # tBodyGyroMag-STD-1             
        # tBodyGyroMag-Mad-1             
        # tBodyGyroMag-Max-1             
        # tBodyGyroMag-Min-1             
        # tBodyGyroMag-SMA-1             
        # tBodyGyroMag-Energy-1          
        # tBodyGyroMag-IQR-1             
        # tBodyGyroMag-ropy-1            
        # tBodyGyroMag-ARCoeff-1         
        # tBodyGyroMag-ARCoeff-2         
        # tBodyGyroMag-ARCoeff-3         
        # tBodyGyroMag-ARCoeff-4   
    
        print('Processing tBodyGyroJerkMag')      
        # tBodyGyroJerkMag-Mean-1        
        # tBodyGyroJerkMag-STD-1         
        # tBodyGyroJerkMag-Mad-1         
        # tBodyGyroJerkMag-Max-1         
        # tBodyGyroJerkMag-Min-1         
        # tBodyGyroJerkMag-SMA-1         
        # tBodyGyroJerkMag-Energy-1      
        # tBodyGyroJerkMag-IQR-1         
        # tBodyGyroJerkMag-ropy-1        
        # tBodyGyroJerkMag-ARCoeff-1     
        # tBodyGyroJerkMag-ARCoeff-2     
        # tBodyGyroJerkMag-ARCoeff-3     
        # tBodyGyroJerkMag-ARCoeff-4
        
        print('Processing f-transformed')
        # fBodyAcc-Mean-1                
        # fBodyAcc-Mean-2                
        # fBodyAcc-Mean-3                
        # fBodyAcc-STD-1                 
        # fBodyAcc-STD-2                 
        # fBodyAcc-STD-3                 
        # fBodyAcc-Mad-1                 
        # fBodyAcc-Mad-2                 
        # fBodyAcc-Mad-3                 
        # fBodyAcc-Max-1                 
        # fBodyAcc-Max-2                 
        # fBodyAcc-Max-3                 
        # fBodyAcc-Min-1                 
        # fBodyAcc-Min-2                 
        # fBodyAcc-Min-3                 
        # fBodyAcc-SMA-1                 
        # fBodyAcc-Energy-1              
        # fBodyAcc-Energy-2              
        # fBodyAcc-Energy-3              
        # fBodyAcc-IQR-1                 
        # fBodyAcc-IQR-2                 
        # fBodyAcc-IQR-3                 
        # fBodyAcc-ropy-1                
        # fBodyAcc-ropy-1                
        # fBodyAcc-ropy-1                
        # fBodyAcc-MaxInds-1             
        # fBodyAcc-MaxInds-2             
        # fBodyAcc-MaxInds-3             
        # fBodyAcc-MeanFreq-1            
        # fBodyAcc-MeanFreq-2            
        # fBodyAcc-MeanFreq-3            
        # fBodyAcc-Skewness-1            
        # fBodyAcc-Kurtosis-1            
        # fBodyAcc-Skewness-1            
        # fBodyAcc-Kurtosis-1            
        # fBodyAcc-Skewness-1            
        # fBodyAcc-Kurtosis-1            
        # fBodyAcc-BandsEnergyOld-1      
        # fBodyAcc-BandsEnergyOld-2      
        # fBodyAcc-BandsEnergyOld-3      
        # fBodyAcc-BandsEnergyOld-4      
        # fBodyAcc-BandsEnergyOld-5      
        # fBodyAcc-BandsEnergyOld-6      
        # fBodyAcc-BandsEnergyOld-7      
        # fBodyAcc-BandsEnergyOld-8      
        # fBodyAcc-BandsEnergyOld-9      
        # fBodyAcc-BandsEnergyOld-10     
        # fBodyAcc-BandsEnergyOld-11     
        # fBodyAcc-BandsEnergyOld-12     
        # fBodyAcc-BandsEnergyOld-13     
        # fBodyAcc-BandsEnergyOld-14     
        # fBodyAcc-BandsEnergyOld-15     
        # fBodyAcc-BandsEnergyOld-16     
        # fBodyAcc-BandsEnergyOld-17     
        # fBodyAcc-BandsEnergyOld-18     
        # fBodyAcc-BandsEnergyOld-19     
        # fBodyAcc-BandsEnergyOld-20     
        # fBodyAcc-BandsEnergyOld-21     
        # fBodyAcc-BandsEnergyOld-22     
        # fBodyAcc-BandsEnergyOld-23     
        # fBodyAcc-BandsEnergyOld-24     
        # fBodyAcc-BandsEnergyOld-25     
        # fBodyAcc-BandsEnergyOld-26     
        # fBodyAcc-BandsEnergyOld-27     
        # fBodyAcc-BandsEnergyOld-28     
        # fBodyAcc-BandsEnergyOld-29     
        # fBodyAcc-BandsEnergyOld-30     
        # fBodyAcc-BandsEnergyOld-31     
        # fBodyAcc-BandsEnergyOld-32     
        # fBodyAcc-BandsEnergyOld-33     
        # fBodyAcc-BandsEnergyOld-34     
        # fBodyAcc-BandsEnergyOld-35     
        # fBodyAcc-BandsEnergyOld-36     
        # fBodyAcc-BandsEnergyOld-37     
        # fBodyAcc-BandsEnergyOld-38     
        # fBodyAcc-BandsEnergyOld-39     
        # fBodyAcc-BandsEnergyOld-40     
        # fBodyAcc-BandsEnergyOld-41     
        # fBodyAcc-BandsEnergyOld-42     
        # fBodyAccJerk-Mean-1            
        # fBodyAccJerk-Mean-2            
        # fBodyAccJerk-Mean-3            
        # fBodyAccJerk-STD-1             
        # fBodyAccJerk-STD-2             
        # fBodyAccJerk-STD-3             
        # fBodyAccJerk-Mad-1             
        # fBodyAccJerk-Mad-2             
        # fBodyAccJerk-Mad-3             
        # fBodyAccJerk-Max-1             
        # fBodyAccJerk-Max-2             
        # fBodyAccJerk-Max-3             
        # fBodyAccJerk-Min-1             
        # fBodyAccJerk-Min-2             
        # fBodyAccJerk-Min-3             
        # fBodyAccJerk-SMA-1             
        # fBodyAccJerk-Energy-1          
        # fBodyAccJerk-Energy-2          
        # fBodyAccJerk-Energy-3          
        # fBodyAccJerk-IQR-1             
        # fBodyAccJerk-IQR-2             
        # fBodyAccJerk-IQR-3             
        # fBodyAccJerk-ropy-1            
        # fBodyAccJerk-ropy-1            
        # fBodyAccJerk-ropy-1            
        # fBodyAccJerk-MaxInds-1         
        # fBodyAccJerk-MaxInds-2         
        # fBodyAccJerk-MaxInds-3         
        # fBodyAccJerk-MeanFreq-1        
        # fBodyAccJerk-MeanFreq-2        
        # fBodyAccJerk-MeanFreq-3        
        # fBodyAccJerk-Skewness-1        
        # fBodyAccJerk-Kurtosis-1        
        # fBodyAccJerk-Skewness-1        
        # fBodyAccJerk-Kurtosis-1        
        # fBodyAccJerk-Skewness-1        
        # fBodyAccJerk-Kurtosis-1        
        # fBodyAccJerk-BandsEnergyOld-1  
        # fBodyAccJerk-BandsEnergyOld-2  
        # fBodyAccJerk-BandsEnergyOld-3  
        # fBodyAccJerk-BandsEnergyOld-4  
        # fBodyAccJerk-BandsEnergyOld-5  
        # fBodyAccJerk-BandsEnergyOld-6  
        # fBodyAccJerk-BandsEnergyOld-7  
        # fBodyAccJerk-BandsEnergyOld-8  
        # fBodyAccJerk-BandsEnergyOld-9  
        # fBodyAccJerk-BandsEnergyOld-10 
        # fBodyAccJerk-BandsEnergyOld-11 
        # fBodyAccJerk-BandsEnergyOld-12 
        # fBodyAccJerk-BandsEnergyOld-13 
        # fBodyAccJerk-BandsEnergyOld-14 
        # fBodyAccJerk-BandsEnergyOld-15 
        # fBodyAccJerk-BandsEnergyOld-16 
        # fBodyAccJerk-BandsEnergyOld-17 
        # fBodyAccJerk-BandsEnergyOld-18 
        # fBodyAccJerk-BandsEnergyOld-19 
        # fBodyAccJerk-BandsEnergyOld-20 
        # fBodyAccJerk-BandsEnergyOld-21 
        # fBodyAccJerk-BandsEnergyOld-22 
        # fBodyAccJerk-BandsEnergyOld-23 
        # fBodyAccJerk-BandsEnergyOld-24 
        # fBodyAccJerk-BandsEnergyOld-25 
        # fBodyAccJerk-BandsEnergyOld-26 
        # fBodyAccJerk-BandsEnergyOld-27 
        # fBodyAccJerk-BandsEnergyOld-28 
        # fBodyAccJerk-BandsEnergyOld-29 
        # fBodyAccJerk-BandsEnergyOld-30 
        # fBodyAccJerk-BandsEnergyOld-31 
        # fBodyAccJerk-BandsEnergyOld-32 
        # fBodyAccJerk-BandsEnergyOld-33 
        # fBodyAccJerk-BandsEnergyOld-34 
        # fBodyAccJerk-BandsEnergyOld-35 
        # fBodyAccJerk-BandsEnergyOld-36 
        # fBodyAccJerk-BandsEnergyOld-37 
        # fBodyAccJerk-BandsEnergyOld-38 
        # fBodyAccJerk-BandsEnergyOld-39 
        # fBodyAccJerk-BandsEnergyOld-40 
        # fBodyAccJerk-BandsEnergyOld-41 
        # fBodyAccJerk-BandsEnergyOld-42 
        # fBodyGyro-Mean-1               
        # fBodyGyro-Mean-2               
        # fBodyGyro-Mean-3               
        # fBodyGyro-STD-1                
        # fBodyGyro-STD-2                
        # fBodyGyro-STD-3                
        # fBodyGyro-Mad-1                
        # fBodyGyro-Mad-2                
        # fBodyGyro-Mad-3                
        # fBodyGyro-Max-1                
        # fBodyGyro-Max-2                
        # fBodyGyro-Max-3                
        # fBodyGyro-Min-1                
        # fBodyGyro-Min-2                
        # fBodyGyro-Min-3                
        # fBodyGyro-SMA-1                
        # fBodyGyro-Energy-1             
        # fBodyGyro-Energy-2             
        # fBodyGyro-Energy-3             
        # fBodyGyro-IQR-1                
        # fBodyGyro-IQR-2                
        # fBodyGyro-IQR-3                
        # fBodyGyro-ropy-1               
        # fBodyGyro-ropy-1               
        # fBodyGyro-ropy-1               
        # fBodyGyro-MaxInds-1            
        # fBodyGyro-MaxInds-2            
        # fBodyGyro-MaxInds-3            
        # fBodyGyro-MeanFreq-1           
        # fBodyGyro-MeanFreq-2           
        # fBodyGyro-MeanFreq-3           
        # fBodyGyro-Skewness-1           
        # fBodyGyro-Kurtosis-1           
        # fBodyGyro-Skewness-1           
        # fBodyGyro-Kurtosis-1           
        # fBodyGyro-Skewness-1           
        # fBodyGyro-Kurtosis-1           
        # fBodyGyro-BandsEnergyOld-1     
        # fBodyGyro-BandsEnergyOld-2     
        # fBodyGyro-BandsEnergyOld-3     
        # fBodyGyro-BandsEnergyOld-4     
        # fBodyGyro-BandsEnergyOld-5     
        # fBodyGyro-BandsEnergyOld-6     
        # fBodyGyro-BandsEnergyOld-7     
        # fBodyGyro-BandsEnergyOld-8     
        # fBodyGyro-BandsEnergyOld-9     
        # fBodyGyro-BandsEnergyOld-10    
        # fBodyGyro-BandsEnergyOld-11    
        # fBodyGyro-BandsEnergyOld-12    
        # fBodyGyro-BandsEnergyOld-13    
        # fBodyGyro-BandsEnergyOld-14    
        # fBodyGyro-BandsEnergyOld-15    
        # fBodyGyro-BandsEnergyOld-16    
        # fBodyGyro-BandsEnergyOld-17    
        # fBodyGyro-BandsEnergyOld-18    
        # fBodyGyro-BandsEnergyOld-19    
        # fBodyGyro-BandsEnergyOld-20    
        # fBodyGyro-BandsEnergyOld-21    
        # fBodyGyro-BandsEnergyOld-22    
        # fBodyGyro-BandsEnergyOld-23    
        # fBodyGyro-BandsEnergyOld-24    
        # fBodyGyro-BandsEnergyOld-25    
        # fBodyGyro-BandsEnergyOld-26    
        # fBodyGyro-BandsEnergyOld-27    
        # fBodyGyro-BandsEnergyOld-28    
        # fBodyGyro-BandsEnergyOld-29    
        # fBodyGyro-BandsEnergyOld-30    
        # fBodyGyro-BandsEnergyOld-31    
        # fBodyGyro-BandsEnergyOld-32    
        # fBodyGyro-BandsEnergyOld-33    
        # fBodyGyro-BandsEnergyOld-34    
        # fBodyGyro-BandsEnergyOld-35    
        # fBodyGyro-BandsEnergyOld-36    
        # fBodyGyro-BandsEnergyOld-37    
        # fBodyGyro-BandsEnergyOld-38    
        # fBodyGyro-BandsEnergyOld-39    
        # fBodyGyro-BandsEnergyOld-40    
        # fBodyGyro-BandsEnergyOld-41    
        # fBodyGyro-BandsEnergyOld-42    
        # fBodyAccMag-Mean-1             
        # fBodyAccMag-STD-1              
        # fBodyAccMag-Mad-1              
        # fBodyAccMag-Max-1              
        # fBodyAccMag-Min-1              
        # fBodyAccMag-SMA-1              
        # fBodyAccMag-Energy-1           
        # fBodyAccMag-IQR-1              
        # fBodyAccMag-ropy-1             
        # fBodyAccMag-MaxInds-1          
        # fBodyAccMag-MeanFreq-1         
        # fBodyAccMag-Skewness-1         
        # fBodyAccMag-Kurtosis-1         
        # fBodyAccJerkMag-Mean-1         
        # fBodyAccJerkMag-STD-1          
        # fBodyAccJerkMag-Mad-1          
        # fBodyAccJerkMag-Max-1          
        # fBodyAccJerkMag-Min-1          
        # fBodyAccJerkMag-SMA-1          
        # fBodyAccJerkMag-Energy-1       
        # fBodyAccJerkMag-IQR-1          
        # fBodyAccJerkMag-ropy-1         
        # fBodyAccJerkMag-MaxInds-1      
        # fBodyAccJerkMag-MeanFreq-1     
        # fBodyAccJerkMag-Skewness-1     
        # fBodyAccJerkMag-Kurtosis-1     
        # fBodyGyroMag-Mean-1            
        # fBodyGyroMag-STD-1             
        # fBodyGyroMag-Mad-1             
        # fBodyGyroMag-Max-1             
        # fBodyGyroMag-Min-1             
        # fBodyGyroMag-SMA-1             
        # fBodyGyroMag-Energy-1          
        # fBodyGyroMag-IQR-1             
        # fBodyGyroMag-ropy-1            
        # fBodyGyroMag-MaxInds-1         
        # fBodyGyroMag-MeanFreq-1        
        # fBodyGyroMag-Skewness-1        
        # fBodyGyroMag-Kurtosis-1        
        # fBodyGyroJerkMag-Mean-1        
        # fBodyGyroJerkMag-STD-1         
        # fBodyGyroJerkMag-Mad-1         
        # fBodyGyroJerkMag-Max-1         
        # fBodyGyroJerkMag-Min-1         
        # fBodyGyroJerkMag-SMA-1         
        # fBodyGyroJerkMag-Energy-1      
        # fBodyGyroJerkMag-IQR-1         
        # fBodyGyroJerkMag-ropy-1        
        # fBodyGyroJerkMag-MaxInds-1     
        # fBodyGyroJerkMag-MeanFreq-1    
        # fBodyGyroJerkMag-Skewness-1    
        # fBodyGyroJerkMag-Kurtosis-1    
        # tBodyAcc-AngleWRTGravity-1     
        # tBodyAccJerk-AngleWRTGravity-1 
        # tBodyGyro-AngleWRTGravity-1    
        # tBodyGyroJerk-AngleWRTGravity-1
        # tXAxisAcc-AngleWRTGravity-1    
        # tYAxisAcc-AngleWRTGravity-1    
        # tZAxisAcc-AngleWRTGravity-1    
    xx=pd.concat(df_feature, axis=1)
    xx.head()
    
    
# Ignore this until the final product
# =============================================================================
# =============================================================================
# if __name__ == '__main__':
#     feature_extract()
#     
# =============================================================================
