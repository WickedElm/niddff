import numpy as np
import os
import pandas as pd
import sys

###
# Read in arguments
###
working_directory = sys.argv[1]
source_file_name = sys.argv[2]
output_file_name = sys.argv[3]

###
# Read in our sources of data
# - Check for standard zeek/argus features
# - Then find any custom features
###
merge_zeek = False
merge_argus = False

if os.path.exists(f'{working_directory}/{source_file_name}.zeek.features.csv'):
    merge_zeek = True
else:
    print('In order to use standard combine zeek features must exist!')
    sys.exit(1)

if os.path.exists(f'{working_directory}/{source_file_name}.argus.features.csv'):
    merge_argus = True

zeek_features = pd.read_csv(f'{working_directory}/{source_file_name}.zeek.features.csv')

# Read in feature processing __load__.python to check for features in there
dfs_to_merge = list()
with open(f'{working_directory}/../step_feature_processing/__load__.python', 'r') as f:
    python_features = f.readlines()

for python_feature in python_features:
    python_feature = python_feature.strip()
    if python_feature.startswith('#'):
        continue

    feature_file_path = f'{working_directory}/{source_file_name}.{python_feature}.csv'
    if os.path.exists(feature_file_path):
        dfs_to_merge = {python_feature:pd.read_csv(feature_file_path)}

# Read in label processing __load__.python to check for features in there
label_dfs_to_merge = list()
with open(f'{working_directory}/../step_label_processing/__load__.python', 'r') as f:
    python_features = f.readlines()

for python_feature in python_features:
    python_feature = python_feature.strip()
    if python_feature.startswith('#'):
        continue

    feature_file_path = f'{working_directory}/{source_file_name}.{python_feature}.csv'
    if os.path.exists(feature_file_path):
        label_dfs_to_merge = {python_feature:pd.read_csv(feature_file_path)}

###
# Perform pre-processing to make matching easier
###
if merge_argus:
    argus_features = pd.read_csv(f'{working_directory}/{source_file_name}.argus.features.csv')

    # Round start time column to match precision of zeek data
    argus_features.StartTime = argus_features.StartTime.apply(round)

    # Make these strings to account for hex values in argus files
    # - This just allows us to join on the columns
    zeek_features['id.orig_p'] = zeek_features['id.orig_p'].astype(str)
    zeek_features['id.resp_p'] = zeek_features['id.resp_p'].astype(str)

    ###
    # Merge data on unique columns to match flows 
    ###
    merged_features = pd.merge(
        zeek_features, 
        argus_features, 
        how='inner', 
        left_on=['id.orig_h', 'id.orig_p', 'id.resp_h', 'id.resp_p', 'proto', 'stime'], 
        right_on=['SrcAddr', 'Sport', 'DstAddr', 'Dport', 'Proto', 'StartTime']
    )
else:
    merged_features = zeek_features

###
# Add python generated features.
# -Assumes has the proper number of entries
###
for key in dfs_to_merge.keys():
    merged_features[key] = dfs_to_merge[key].iloc[:,-1]

###
# Add labels
###

for key in label_dfs_to_merge.keys():
    merged_features[key] = label_dfs_to_merge[key].iloc[:,-1]

# Replace bad zeek values with na to be dropped
merged_features = merged_features.replace('-', np.nan)
merged_features.dropna(inplace=True)

###
# Clean up duplicated columns
###
if merge_argus:
    merged_features = merged_features.drop(columns=['SrcAddr', 'Sport', 'DstAddr', 'Dport', 'Proto', 'StartTime'])

###
# Save out merged file
###
merged_features.to_csv(f'{working_directory}/{source_file_name}.{output_file_name}', index=False)
