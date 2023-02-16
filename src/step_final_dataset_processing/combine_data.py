import glob
import pandas as pd
import sys

###
# Read in arguments
###
working_directory = sys.argv[1]
output_file_name = sys.argv[2]

###
# Gather all files that end with output_file_name
###

# Read in as dataframes
all_data_frames = list()
for datafile in glob.glob(f'{working_directory}/*{output_file_name}'):
    df = pd.read_csv(datafile)
    all_data_frames.append(df)

# Combine them all
final_df = pd.concat(all_data_frames)

# Write out final output
final_df.to_csv(f'{working_directory}/{output_file_name}', index=False)
