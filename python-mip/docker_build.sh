#!/bin/bash
source .env

docker build --build-arg PYTHON_MIP_BRANCH=$PYTHON_MIP_BRANCH --build-arg PYTHON_MIP_COMMIT=$PYTHON_MIP_COMMIT -t python-mip-test .
