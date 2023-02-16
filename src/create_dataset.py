import os
import subprocess
import sys
import pdb
import shutil
from omegaconf import OmegaConf

###
# Helper functions
###
def perform_replacements(input_string, setup_options, output_directory, full_source_path=''):
    if 'ENV_PWD' in input_string:
        env_pwd = os.getcwd()
        input_string = input_string.replace('ENV_PWD', env_pwd)

    for key, value in setup_options.items():
        string_key = '{setup_options.' + key + '}'
        if string_key in input_string:
            input_string = input_string.replace(string_key, value)

    if '{output_directory}' in input_string:
            input_string = input_string.replace('{output_directory}', output_directory)

    if '{source_file}' in input_string:
        input_string = input_string.replace('{source_file}', full_source_path)

    source_file_name = os.path.split(full_source_path)[1]
    if '{source_file_name}' in input_string:
        input_string = input_string.replace('{source_file_name}', source_file_name)

    return input_string

def generate_argus_commands(stage):
    commands = []
    if argus_options['clean']:
        commands.append('rm -f {output_directory}/{source_file_name}.argus')

    commands.append(f'argus {argus_options["arguments"]} ' + ' -r {source_file} -w {output_directory}/{source_file_name}.argus')

    if argus_options['execute_ra']:
        commands.append('./src/argus/ra_wrapper.bash {output_directory} {source_file_name}.argus {source_file_name}.argus.features.csv ' + f'{DATASET_ROOT}/{stage}/__load__.argus')
    return commands

def perform_command(command, output_directory, full_source_path=''):
    stage = 'step_feature_processing'
    if PROCESSING_STAGE == 'label':
        stage = 'step_label_processing'

    if command == EXECUTE_ARGUS:
        commands = generate_argus_commands(stage)
    elif command == EXECUTE_ZEEK:
        command = './src/zeek/zeek-wrapper.bash /niddff/src/zeek/packages {output_directory} {source_file_name} ' + f'{DATASET_ROOT} mlfeatures ' + '-r {source_file}'
        commands = [command]
    elif command.startswith(EXECUTE_PYTHON):
        data_file = command.split(' ')[1]
        ground_truth_file = "/dev/null"
        if setup_options["ground_truth_data"]:
            ground_truth_file = f'{ground_truth_data_dir}/ground_truth'
        command = './src/python/python-wrapper.bash {output_directory} ' + f'{DATASET_ROOT}/{stage} ' + '{source_file_name} ' + f'{data_file} ' + ground_truth_file
        commands = [command]
    elif command.startswith(EXECUTE_COMBINE_FEATURES):
        output_file_base = command.split(' ')[1]
        command = 'python ./src/step_post_processing/combine_features.py {output_directory} {source_file_name} ' + f'{output_file_base}'
        commands = [command]
    elif command.startswith(EXECUTE_COMBINE_DATA):
        output_file = command.split(' ')[1]
        command = 'python ./src/step_final_dataset_processing/combine_data.py {output_directory} ' + output_file
        commands = [command]
    else:
        commands = [command]

    for command in commands:
        command = perform_replacements(command, setup_options, output_directory, full_source_path)
        command_array = command.split()
        print('')
        print(f'Executing [{command}]')
        subprocess.run(command_array)
        print('Complete.')
        print('')

###
# Read in yaml file
###
if __name__ == '__main__':
    yaml_file_path = sys.argv[1]
    output_directory = os.path.split(yaml_file_path)[0] + '/output'

    if not os.path.exists(yaml_file_path):
        print(f'Config file does not exist [{yaml_file_path}]')
        sys.exit(1)

    ###
    # Print out major software versions
    ###

    zeek_version = subprocess.getoutput(['zeek --version'])
    python_version  = subprocess.getoutput(['python --version'])
    argus_version = subprocess.getoutput(['argus -h']).split('\n')[0]
    ra_client_version = subprocess.getoutput(['ra -h']).split('\n')[0]
    all_versions = [f'{zeek_version}\n', f'{python_version}\n', f'{argus_version}\n', f'{ra_client_version}\n']

    with open('.versions', 'w') as f:
        f.writelines(all_versions)
    print('')
    print('---')
    print('Running with software:')
    [print(version.strip()) for version in all_versions]
    print('---')
    print('')

    ###
    # Load base configuration and any overrides
    ###

    base_conf = OmegaConf.load(yaml_file_path)
    cli_conf = OmegaConf.from_cli()
    dataset_instructions = OmegaConf.merge(base_conf, cli_conf)

    ###
    # Separate our base steps
    ###

    documentation = dataset_instructions['documentation']
    setup_options = dataset_instructions['setup_options']
    step_acquire_source_data = dataset_instructions['step_acquire_source_data']
    step_feature_processing = dataset_instructions['step_feature_processing']
    step_label_processing = dataset_instructions['step_label_processing']
    step_post_processing = dataset_instructions['step_post_processing']
    step_final_dataset_processing = dataset_instructions['step_final_dataset_processing']

    # General dataset settings
    DATASET_ROOT = f'/niddff/datasets/{setup_options["dataset_name"]}'

    # Settings to use when executing argus
    EXECUTE_ARGUS = 'run_argus'
    if setup_options['argus']:
        argus_options = setup_options['argus']
    else:
        argus_options = {'clean':True, 'arguments':'', 'execute_ra':True}

    # Settings to use when executing zeek
    EXECUTE_ZEEK = 'run_zeek'

    # Settings to use when executing python scripts
    EXECUTE_PYTHON = 'run_python_scripts'

    # Settings to use when executing our standard combine features script
    EXECUTE_COMBINE_FEATURES = 'run_combine_features'

    # Settings to sue when executing our standard combine data
    EXECUTE_COMBINE_DATA = 'run_combine_data'

    ###
    # Resolve replacements in our setup_options
    ###
    for key, value in setup_options.items():
        if isinstance(value, bool):
            setup_options[key] = value
        else:
            if value:
                setup_options[key] = perform_replacements(value, setup_options, output_directory)

    ###
    # Perform Steps
    ###

    # Create output directory if needed 
    if setup_options['clean_output_directory']:
        shutil.rmtree(output_directory, ignore_errors=True)

    if not os.path.exists(output_directory):
        os.makedirs(output_directory, exist_ok=True)

    # Acquire Source Data
    # Each command is a source to download
    if step_acquire_source_data is not None:
        PROCESSING_STAGE = 'acquire_source_data'
        if setup_options["source_data"]:
            source_data_meta_file = f'./datasets/{setup_options["source_data"]}.meta'
        else:
            print('Every dataset must contain at least one source_data entry.')
            sys.exit(1)

        if setup_options["ground_truth_data"]:
            ground_truth_data_meta_file = f'./datasets/{setup_options["ground_truth_data"]}.meta'
            ground_truth_data_dir = os.path.split(ground_truth_data_meta_file)[0]
        if step_acquire_source_data['download']:
            # Source data
            if setup_options["source_data"]:
                print(source_data_meta_file)
                perform_command(f'python src/step_acquire_source_data/downloader.py {source_data_meta_file} data', output_directory)

            # Ground truth
            if setup_options["ground_truth_data"]:
                print(ground_truth_data_meta_file)
                perform_command(f'python src/step_acquire_source_data/downloader.py {ground_truth_data_meta_file} ground_truth', output_directory)
        else:
            print('Using local files.')

    ###
    # By default we iterate through our source files
    # producing complementary output files.
    # The expectation is that there will be post processing that
    # combines them together at the end.
    ###

    with open(source_data_meta_file, 'r') as f:
        source_meta_data = f.readlines()

    source_data_dir = os.path.split(source_data_meta_file)[0]
    for download_info in source_meta_data:
        url, destination = download_info.split(',')
        full_source_path = f'{source_data_dir}/{destination}'.strip()
        full_source_path = full_source_path.replace('./', '/niddff/')
        print(f'Processing [{full_source_path}]')

        # Feature Processing
        if step_feature_processing is not None:
            PROCESSING_STAGE = 'feature'
            for command in step_feature_processing:
                perform_command(command, output_directory, full_source_path)

        # Label Processing
        if step_label_processing is not None:
            PROCESSING_STAGE = 'label'
            for command in step_label_processing:
                perform_command(command, output_directory, full_source_path)

        # Post Processing
        if step_post_processing is not None:
            PROCESSING_STAGE = 'post'
            for command in step_post_processing:
                perform_command(command, output_directory, full_source_path)

    if step_final_dataset_processing:
        PROCESSING_STAGE = 'final'
        for command in step_final_dataset_processing:
            perform_command(command, output_directory)
