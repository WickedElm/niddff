import io
import pandas as pd
import sys
import subprocess

###
# Process inputs
# - We are already in the working directory so all inputs and 
#   outputs are relative to it
###

source_file_name = sys.argv[1]

###
# Read in actual data
###

zeek_data = subprocess.getoutput([f'cat {source_file_name}.features.log | zeek-cut -m'])
zeek_data_df = pd.read_csv(io.StringIO(zeek_data), sep='\t')

###
# Save actual data with updated label
###

zeek_data_df.to_csv(f'{source_file_name}.zeek.features.csv', index=False)
