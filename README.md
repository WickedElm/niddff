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
The generate this dataset the following steps can be taken:

```
# Change directories to the cloned repo
cd niddff

# Run the niddff container calling our script with the demo_dataset config.yaml file as input
# - We map the repo directory to the /niddff volume in the container
# - The container was generated to match user id / group id of 1000
#   Follow the steps "Rebuilding the niddff Container" to change this if desired
docker run -it -v `pwd`:/niddff niddff:0.1  python ./src/create_dataset.py ./datasets/demo_dataset/config.yaml
```
