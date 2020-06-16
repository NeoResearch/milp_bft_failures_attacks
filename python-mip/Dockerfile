FROM ubuntu:18.04

RUN apt-get update \
    && apt-get install -y python3-pip git
    
RUN python3 -m pip install --upgrade pip    

RUN python3 -m pip install flake8 black
    
RUN git clone https://github.com/coin-or/python-mip.git

WORKDIR python-mip

RUN git pull && git checkout $PYTHON_MIP_BRANCH && git checkout $PYTHON_MIP_COMMIT
    
RUN python3 -m black mip --line-length=89 --check

RUN python3 -m flake8 mip --select=F401 --exclude=__init__.py
