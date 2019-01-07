
basepath=$(cd `dirname $0`; pwd)
echo $basepath
mkdir -p $basepath/logs

CUDA_VISIBLE_DEVICES=0 python3 -u eval.py --checkpoint logs-Tacotron/taco_pretrained/tacotron_model.ckpt-$1

