# niddff - Guidelines and a Framework to Improve the Delivery of Network Intrusion Datasets
Full source code repository to accompany the paper "Guidelines and a Framework to Improve the Delivery of Network Intrusion Datasets".

## Installation of Framework
The framework consists of this repository of code in addition to a container environment.
Getting started is relatively simple:

```
git clone git@github.com:WickedElm/niddff.git
docker pull wickedelm/niddff
```

The most recent version of the container consists of the following software versions:
```
Ubuntu    20.04
Zeek      4.2.1
Argus     3.0.8.2
ra        3.0.8.2
python    3.8.10
scapy     2.5.0
pandas    1.4.3
requests  2.28.1
omegaconf 2.2.2
```

## Getting Started
We have a demo dataset included in the repository called "demo_datset" which can be used as a way to get familiar with using the framework.
The demo dataset constructs a final dataset using a single PCAP from the UNSW-NB15 dataset as its source.
To generate this dataset the following steps can be taken:

```
# Change directories to the cloned repo
cd niddff

# Run the niddff container calling the framework's main script with the demo_dataset config.yaml file as input
# - We map the repo directory to the /niddff volume in the container
# - The container was generated to match user id / group id of 1000
#   Follow the steps "Rebuilding the niddff Container" to change this if desired
docker run --rm -it -v `pwd`:/niddff niddff:0.1  python ./src/create_dataset.py ./datasets/demo_dataset/config.yaml
```

## Dataset Processing Overview
The dataset process consists of executing the ./src/create_dataset.py script with a required argument which is the path to the YAML file for a dataset along with any overrides for values within the config file.
The create_dataset.py script reads in the YAML files and processes commands in a top down manner.
For certain steps, we assume multiple large source files are being processed and so we process them separately and then combine them at the end of the script.
The general algorithm we follow is represented below:

![Algorithm for niddff processing.](./docs/algorithm.png)

## Configuration File Details
One can review the demo dataset file below and conained in ./datasets/demo_dataset/config.yaml in this repository to get familiar with its contents and section.
![Sample configuration yaml file.](./docs/yamlfile.png)

### Configuration File Sections

#### documentation
The documentation section is present to store any documentation notes for the dataset.
Currently, we simply put our version of the container being used so that users of the dataset will know what version to use when working with it.
No functionality is currently performed based on this section aside from storing the values during script execution.

#### setup_options
The setup_options section contains important information regarding the dataset which we discuss below in turn.

```
dataset_name:
This is the name of the dataset and must correspond to the directory name in which it is stored.

source_data:
This indicates where to read the source meta data file.
This should be a path to a .meta file within some datasets's source directory.
Note that we do not include the .meta extension here.

In this example, unsw-nb15-sample/sourc/pcaps will inform the script to read in the
./datasets/unsw-nb15-sample/source/pcaps.meta file.

NOTE:  This path can reference a given dataset's own source files or some other
       dataset's source files as done here with our demo dataset.

ground_truth_data:
Similar to source_data, this indicates where to obtain any ground_truth_data.
It is optional, but if used, should be a path to a .meta file in some dataset's
ground_truth directory.

In this example, unsw-nb15/ground_truth/gt refers to the 
./datasets/unsw-nb15/ground_truth/gt.meta file.

NOTE:  This path can reference a given dataset's own source files or some other
       dataset's source files as done here with our demo dataset.

clean_output_directory:
Valid values for this are True or False.
Indicates if the script should recreate the output directory used for holding any
output data produced.

expected_outputs:
This is currently a convenience entry to indicate to users of the dataset which
files will be of interest after constructing the dataset.

We expect to have additional functionality behind this entry in the future but
currently it is just providing the user useful information.
```

#### step_acquire_source_data
During this step, the script reads in the source data and ground truth data specified in the setup_options section of the configuration file.
It then sequentially downloads all of the source and ground truth data locally.

Setting the download field to False in the configuration file or overriding it on the command line will prevent downloading of the data and the script will assume the files are already available locally.

#### step_feature_processing
The entries of this step get executed in a top down manner for each source file used to generate the features of the target dataset.
While our example shows built-in functions such as "run_zeek" one can input arbitrary commands in this section to run.

The expectation is that scripts executed in this section are located in the dataset's step_feature_processing directory.

#### step_label_processing
The entries of this step get executed in a top down manner for each source file used to generate the labels of the target dataset.
While our example shows using the built-in function "run_python" to execute a python script, one can input arbitrary commands in this section to run.

The expectation is that scripts executed in this section are located in the dataset's step_label_processing directory.

#### step_post_processing
The entries of this step are executed in a top down manner for each source file.
These entries are intended to perform any post-processing needed due to the previous step_feature_processing and step_label_processing commands that were run.
For example, we use this step in our demo dataset to combine the features from zeek, argus, and the labels into a single file using the built-in "run_combine_features" function.

#### step_final_dataset_processing
The entries in this step are executed in a top down manner after all of the source data files have been processed.
The intention of entries in this section is the perform any processing needed to produce the final dataset.
In our example, we use this step to combine all of the intermediate files generated for each source file into a final single dataset file using the "run_combine_data" function.

### Command Line Overrides
The framework uses the python omegaconf package for handling its configuration data.
This makes all the options made available by omegaconf to override settings on the command line available to uses of the framework.
For example to execute the framework without downloading source data one can run the following:

```
# Container arguments have been exluded for brevity
python ./src/create_dataset.py ./datasets/demo_dataset/config.yaml step_acquire_source_data.download=False
```
### Framework Variables
Within the YAML configuration file, users can reference previously declared items using the standard syntax supported by omegaconf.
For example, if you wanted to reference the dataset_name declared in setup_options somewhere later in the file, you can use the syntax 

```
${setup_options.dataset_name}
```

In addition to this functionality, we provide our own variables that can be referenced within the configuration file with the actual values replaced at runtime.
All of these variables consist of the format:

```
{variable name}
``` 

Below are the details regarding these variables:

```
{output_directory}
At runtime this resolves to the path where all of a dataset's output data will be stored.
This is generally ./dataseets/<dataset_name>/output

{source_file}
At runtime this resolves to the full path of the current source file being processed.

{source_file_name}
At runtime this resolves to just the name portion of the current source file being processed.
``` 

## Dataset Directory Structure
Each dataset contains a standard direcory structure as shown below:

![Directory structure for a dataset.](./docs/dirsctructure.png)

Below are the details of what is expected to be in each directory:

```
In the top level directory one will find the configuration yaml file.

source/
In the source directory it is expected that metadata for downloading source files would appear.
After source files have been downloaded this is also where those files would appear.
Note that many datasets would not have this directory populated if they are using source data from an external dataset.

ground_truth/
In the ground_truth directory it is expected that metadata for downloading ground truth files would appear.
After the step_acquire_source_data has been performed any downloaded ground truth files would be in this directory.
Note that many datasets would not have this directory populated if they are using ground truth data from an external dataset.

output/
This directory is empty by default and generally gets cleaned out between executions of the dataset creation.
All output data including intermediary files and the final output files would be populated in this directory.
It can be referenced in the YAML input file as {output_directory}.

step_acquire_source_data/
This directory contains any __load__.<tool> files and associated scripts that are used to acquire source data.

step_feature_processing/
This directory contains any __load__.<tool> files and associated scripts that are used during the feature processing step.

step_label_processing/
This directory contains any __load__.<tool> files and associated scripts that are used during the label processing step.

step_post_processing/
This directory contains any __load__.<tool> files and associated scripts that are used during the post processing step.

step_final_dataset_processing/
This directory contains any __load__.<tool> files and associated scripts that are used during the final dataset processing step.
```

## Supported Tools
Here we provide an overview of the support the framework provides for various tools.
This is expected to grow in the future to meet the needs of more researchers.

### Zeek
The framework comes with default support for using the zeek network analysis tool.
In particular, we provide wrapper syntax in order to provide the ability to have custom features based on zeek's default conn.log processing architecture.
In other words, we focus on generating flow-based features using zeek.
To use this built in feature there are three main steps as outlined below:

```
1.  Generate a zeek script for a feature or label
    - Follow the example scripts found in the ./datasets/demo_dataset/step_feature_processing directory
    - Name script in the format <feature name>.zeek
    - Place script in ./dataset/<dataset name>/step_feature_processing directory for features
    - Place script in ./dataset/<dataset name>/step_label_processing directory for labeling

2.  Create or update a __load__.zeek file
    - Add the following to a line in the file:

        @load ./<script_name>

    - Do not include the .zeek file extension
      
    - Place file in ./dataset/<dataset name>/step_feature_processing directory for features
    - Place file in ./dataset/<dataset name>/step_label_processing directory for labeling

3.  Add the run_zeek instruction to the proper section of the YAML configuration file
    - No arguments are needed for this instruction
```

If the default setup for using zeek does not meet your needs, you can also simply add zeek calls to your YAML file to use the tool directly.

### Argus
The framework comes with default support for using the argus network analysis tool and its ra client tool.
There are several simple steps that can be performed to take advantage of the argus functionality:

```
1.  Create an argus entry in the setup_options portion of the YAML file

  EX:

  argus:
    clean: True
    arguments: -S 60 -m
    execute_ra: True

  clean:      Indicates to remove any .argus files before running argus
  arguments:  Include any command lines options that the argus CLI accepts 
  execute_ra: Indicates if the ra client should be ran after executing argus

2.  Create or update a __load__.argus file.
    - Each line in this file is an option accepted by the "-s" parameter of the ra client tool
    - See man ra for additional details for valid values
    - Place file in ./dataset/<dataset name>/step_feature_processing directory for features
    - Place file in ./dataset/<dataset name>/step_label_processing directory for labeling

3.  Add the run_argus instruction to the proper section of the YAML configuration file
    - No arguments are needed for this instruction
```

Similar to our zeek support, if the default support does not meet your needs, you can also simply add argus and ra calls to your YAML file to use the tool directly.

### Python
Similar to the default support for zeek and argus, the framework provides support for python scripting in a similar manner:

```
1.  Create or update a __load__.python file.
    - Each line in this file refers to a python script in the same directory without the .py extension.
    - Place file in ./dataset/<dataset name>/step_feature_processing directory for features
    - Place file in ./dataset/<dataset name>/step_label_processing directory for labeling

2.  Create corresponding python script.
    - Use the same name as the entry in __load__.python
    - Scripts called with the framework get are provided with the following four arguments:

    working_directory (arg1)
    - The output directory where intermediary files and all output files should be stored.

    source_file_name (arg2)
    - The name of the current source file being processed.

    data_file (arg3)
    - This is provided as part of the call to run_python_scripts and specified in the YAML file.
    - It is intended to be the data file to be processed by the script but there are no restrictions on what is passed here.

    ground_truth_file (arg4)
    - The path to the ground truth file (if present).
    - If no ground truth is specified then this is provided with /dev/null

3.  Add the run_python_scripts instruction to the proper section of the YAML configuration file.
    - This takes one argument which is the data file to be processed
    - EX:

        run_python_scripts {output_directory}/{source_file_name}.zeek.features.csv
```

Similar to other built-in support, users can call arbitrary python scripts by specifying the commands and arguments needed in the YAML configuration file.

## Rebuilding a Dataset
Rebuilding a dataset an existing dataset from source is relatively straightforward:

```
docker run --rm -it -v `pwd`:/niddff niddff:0.1  python ./src/create_dataset.py ./datasets/<dataset name>/<configuration file name>.yaml
```

After the dataset processing is complete, one should expect the output to be in the ./datasets/<dataset name>/output directory.
If a datset is not part of the default framework repository, simply pull down the dataset from its repo and put the dataset directory into the ./datasets/ directory.

## Creating a Dataset
There are several broad steps needed to create a new dataset:

```
1.  Create the default directory structure
    
        docker run --rm -it -v `pwd`:/niddff niddff:0.1 ./scripts/create_dataset_template <dataset name> 
        - This command creates an empty directory structure with template files in ./datasets/<dataset name>
        - NOTE:  This will recursively remove the ./datasets/<dataset name> directory if it exists.

2.  Fill out YAML configuration file.

3.  Implement any processing scripts needed.
```

Note that it is expected that steps 2 and 3 would likely be done iteratively together.

## Adding/Removing/Exchanging Features
For a given dataset, the process of adding a feature generally involves creating a script in the step_feature_processing directory and then adding its reference to the appropriate __load__.<tool> file.

To remove a feature, one can simply remove its entry from the __load__.<tool> file.
To be complete the associated script may want to be removed as well though it is not necessary.

If a feature has already been created using the standard supported tools and source data one can simply copy in the appropriate script and add its reference to the appropriate __load__.<tool> file.
Note that it is possible to exchange features that were not generated from the same source file provided the scripts do not contain anything specific to that source dataset in them.

## Rebuilding the niddff Container
In order to re-build the niddff container one can perform the following steps:
```
# The Docker file supports the following arguments:
# ZEEK_VERSION
# ARGUS_VERSION
# PYTHON_VERSION
# USER_ID
# GROUP_ID
#
# NOTE:  If you are rebuilding the container to change tooling, please open a pull request
#        or open an issue so we can collaborate to get it into a common container image.
#
# Assuming you are in the top-level directory of the repo
cd ./containers/niddff/
./build.bash <tag> <any valid arguments to docker-build>
```
