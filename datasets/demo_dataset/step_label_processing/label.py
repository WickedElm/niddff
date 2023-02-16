import io
import pandas as pd
import sys
import subprocess
import pdb

###
# Process inputs
###
working_directory = sys.argv[1]
source_file_name = sys.argv[2]
data_file = sys.argv[3]
ground_truth_file = sys.argv[4]

###
# Read in ground truth data
# - Read in data
# - Construct hash using 5-tuple
###

with open(ground_truth_file, 'r') as f:
    ground_truth = f.readlines()

ground_truth_lookup = dict()
for line in ground_truth:
    fields = line.split(',')
    if len(fields) < 9:
        continue
    key = f'{fields[0]},{fields[1]},{fields[4]},{fields[5]},{fields[6]},{fields[7]},{fields[8]}'
    ground_truth_lookup[key] = 1

###
# Read in actual data
###
zeek_data_df = pd.read_csv(data_file)

###
# Construct array of labels
###

zeek_data_keys = \
    (zeek_data_df['stime'].astype(str) + ',' + \
    zeek_data_df['ltime'].astype(str) + ',' + \
    zeek_data_df['proto'].astype(str) + ',' +  \
    zeek_data_df['id.orig_h'].astype(str) + ',' + \
    zeek_data_df['id.orig_p'].astype(str) + ',' + \
    zeek_data_df['id.resp_h'].astype(str) + ',' + \
    zeek_data_df['id.resp_p'].astype(str)).tolist()

labels = list()
for key in zeek_data_keys:
    if key.startswith('stime'):
        continue

    if key in ground_truth_lookup:
        labels.append(1)
    else:
        labels.append(0)

###
# Label the data
###

zeek_data_df['label'] = labels
zeek_label_df = zeek_data_df[['stime', 'ltime', 'proto', 'id.orig_h', 'id.orig_p', 'id.resp_h', 'id.resp_p', 'label']]

###
# Save actual data with updated label
###

zeek_label_df.to_csv(f'{working_directory}/{source_file_name}.label.csv', index=False)
