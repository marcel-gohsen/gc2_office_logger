#!/bin/bash

pushd ./src/

source activate gc2_office_logger
python setup.py build
conda deactivate

popd
shc -T -f run.sh
gcc -o ./build/linux/run run.sh.x.c
