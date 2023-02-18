# niddff - Guidelines and a Framework to Improve the Delivery of Network Intrusion Datasets
Full source code repository to accompany the paper "Guidelines and a Framework to Improve the Delivery of Network Intrusion Datasets".

## Installation of Framework
The framework consists of this repository of code in addition to a container environment.
Getting started is relatively simple:

```
git clone git@github.com:WickedElm/niddff.git
docker pull wickedelm/niddff
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
docker run -it -v `pwd`:/niddff niddff:0.1  python ./src/create_dataset.py ./datasets/demo_dataset/config.yaml
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

### Sections Overview

#### documentation

#### setup_options

#### step_acquire_source_data

#### step_feature_processing

#### step_label_processing

#### step_post_processing

#### step_final_dataset_processing

### Command Line Overrides

### Framework Variables

## Dataset Directory Structure

## Supported Tools

### Zeek

### Argus

### Python

## Creating a Dataset

## Rebuilding a Dataset

## Adding/Removing Features

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
