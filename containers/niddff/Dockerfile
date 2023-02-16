# Get zeek from their official container image
ARG ZEEK_VERSION=4.2.1
FROM zeekurity/zeek:${ZEEK_VERSION} as zeekimage

# Begin final image
FROM ubuntu:20.04 
ARG USER_ID=1000
ARG GROUP_ID=1000
ARG PYTHON_VERSION=3.8.2-0ubuntu2
ARG ARGUS_VERSION=1:3.0.8.2-5ubuntu1

WORKDIR /niddff

COPY ZEEK_LICENSE .
COPY ARGUS_LICENSE . 

###
# PYTHON
###

RUN apt update; 
RUN apt install -y python3=${PYTHON_VERSION} python3-venv python3-pip python-is-python3

COPY requirements.txt .
RUN pip3 install -r requirements.txt

###
# TEXT EDITOR
###

RUN apt install -y vim

###
# ARGUS
###

RUN apt install -y argus-client=${ARGUS_VERSION}

###
# ZEEK
###

RUN apt update \
    && apt -y install --no-install-recommends libpcap0.8 libssl1.1 libmaxminddb0 python3.9-minimal \
    && apt clean && rm -rf /var/lib/apt/lists/*

COPY --from=zeekimage /usr/local/zeek /usr/local/zeek
RUN ln -s /usr/local/zeek /bro
RUN ln -s /usr/local/zeek /zeek
env PATH /zeek/bin:$PATH

###
# Add a non-root user
# - Users should match their uid and guid to make things easier
###

RUN addgroup --system --gid ${GROUP_ID} niddff && adduser --no-create-home --disabled-password --disabled-login --gecos '' -u ${USER_ID} --gid ${GROUP_ID} niddff
USER niddff:niddff

CMD ["bash"]
