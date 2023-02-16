import io
import os
import pandas as pd
import subprocess
import sys

###
# Number of the past 100 connections that have the 
# same source ip address as a given current flow.
###

# Get path to our previously created flow data file
working_directory = sys.argv[1]
source_file_name = sys.argv[2]
data_source_path = sys.argv[3]
ground_truth_path = sys.argv[4] # Not used here

# Read in data
zeek_data_df = pd.read_csv(data_source_path)

# Store values for saving
all_ct_src_ltm = []

# Goal of this is to output a single feature in our working directory
# Slow but only used for demonstration purposes
for index, row in zeek_data_df.iterrows():
    if index < 100:
        df_slice = zeek_data_df[:index]
    else:
        df_slice = zeek_data_df[index - 100:index]
    all_ct_src_ltm.append(df_slice[df_slice['id.orig_h'] == row['id.orig_h']].shape[0])

# Save our feature to be combined later
pd.DataFrame(all_ct_src_ltm, columns=['ct_src_ltm'], index=zeek_data_df.index).to_csv(f'{working_directory}/{source_file_name}.ct_src_ltm.csv')
