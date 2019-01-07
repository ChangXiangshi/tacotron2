#!/bin/bash

basepath=$(cd `dirname $0`; pwd)
echo $basepath
cd $basepath

mkdir -p $basepath/logs
CUDA_VISIBLE_DEVICES=0 python3 -u $basepath/synthesize.py
