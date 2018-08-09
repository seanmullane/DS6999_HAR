# -*- coding: utf-8 -*-
import glob
import os
import pandas as pd
import scipy
import scipy.signal

"""
Contains helper functions to process data
"""

def add_labels_to_data(dataframe, labels):
    dataframe.columns = labels
    return dataframe

def apply_butter_filter(dataframe, hz):
    butter_filter = get_butter_filter(hz)
    return dataframe.apply(lambda x: scipy.signal.lfilter(butter_filter[0], butter_filter[1], x))

def apply_median_filter(dataframe, index_list):
    return dataframe[index_list].apply(get_median_filter())

def get_butter_filter(hz):
    return scipy.signal.butter(3, 0.3 / (hz/2))

def get_data(filename):
    return pd.read_table(filename, sep='\s', header=None, engine='python')

def get_data_hz(dataframe, hz):
    return dataframe[dataframe.index % (50/hz) == 0].reset_index(drop=True)
    
def get_empty_dataframe():
    return pd.DataFrame()

def get_files(path):
    return glob.glob(path)

def get_file_name_from_path(filepath):
    return os.path.splitext(os.path.basename(filepath))[0]
    
def get_median_filter():
    return scipy.signal.medfilt

def set_output_path(path):
    os.chdir(path)
    