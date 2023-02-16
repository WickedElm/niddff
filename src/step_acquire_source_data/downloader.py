import requests
import sys
import os

###
# A simple script to download source data based on a list of url,destination pairs.
###

source_data_meta_file = sys.argv[1]
source_type = sys.argv[2]
source_data_dir = os.path.split(source_data_meta_file)[0]

if not os.path.exists(source_data_meta_file):
    print(f'Meta file [{source_data_meta_file}] does not exist')
    sys.exit(1)

with open(source_data_meta_file, 'r') as f:
    meta_data = f.readlines()

replace_string = '/pcaps'
if source_type == 'ground_truth':
    replace_string = '/gt'

for download_info in meta_data:
    url, destination = download_info.split(',')
    full_destination_path = f'{source_data_dir}/{destination}'.replace(replace_string, '').strip()

    # Assumes single ground truth file
    # - This allows easier reference later in scripting but made more robust later
    if source_type == 'ground_truth':
        full_destination_path = f'{source_data_dir}/ground_truth'

    print(f'Downloading {url} into {full_destination_path}')
    if '/' in destination:
        full_path_only, _ = os.path.split(full_destination_path)
        if not os.path.exists(full_path_only):
            os.makedirs(full_path_only, exist_ok=True)

    response = requests.get(f'{url}')
    with open(f'{full_destination_path}', 'wb') as f:
        f.write(response.content)
