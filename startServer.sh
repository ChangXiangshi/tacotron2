#!/usr/bin/env bash

basepath=$(cd `dirname $0`; pwd)
echo $basepath
mkdir -p $basepath/logs

CUDA_VISIBLE_DEVICES=0 python3 -u demo_server.py --name Tacotron --host 0.0.0.0 --port 8080 --checkpoint logs-Tacotron/taco_pretrained/tacotron_model.ckpt-$1  > $basepath/logs/server.log 2>&1  &
