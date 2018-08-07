# DS6999_HAR
Independent study on sampling rate and window size effect on human activity recognition model performance

# Data files

Frequency Data: https://drive.google.com/open?id=1-vi2KLF_FhjBXSLqdTtb48EArqGHVJAN
- This is the raw data processed through get_data.py.
- It takes the raw data and applies all preliminary filters (median filter n=3, butterworth 0.3 Hz cutoff) and then downsamples it by taking every n-th reading.
- Downsample sets are 50 Hz (original), 25 Hz, 10 Hz, and 5 Hz.

Features Data: https://drive.google.com/open?id=1kki2UFE8WxfY-i_g2wXpwq60GZEPj8ue
- This is the Frequency data processed through feature_extract.py.
- It takes the frequency data and splits it into different observation windows (1s, 2s, 3s, 5s, and 10s).
- It calculates features from the time and frequency domain.

Training Data: https://drive.google.com/open?id=1_u81cMzNdJiTvHeI01k634HKwW8kvJ54
- This is the Features data processed through split_scale.py.
- This is the training data.
- It is preprocessed by removing all empty rows and empty/bad columns.
- The values are scaled between -1 and 1.

Test Data: https://drive.google.com/open?id=1Km_gLf2uo6jPu8VH_0isMLG31gxw-zS1
- This is the Features data processed through split_scale.py.
- This is the training data.
- It is preprocessed by removing all empty rows and empty/bad columns.
- The values are scaled between -1 and 1.

ML Data: <Add link when ready>
- This is the Test and Training data processed through different ML techniques.
- There are R and Python variants.

Writeup: <Add link when ready>
- This is the writeup for the findings of the data.

# To-do list:
Apply ML techniques
