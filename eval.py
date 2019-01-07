import argparse
import os
import re
from hparams import hparams, hparams_debug_string
from tacotron.synthesizer import Synthesizer


sentences = [
    "meng2 yuan1 A er4 shi2 ba1 nian2 A liu2 zhong1 lin2 A huo4 A si4 bai3 A liu4 shi2 A wan4 yuan2 A guo2 jia1 pei2 chang2 E"

]


def get_output_base_path(checkpoint_path):
  base_dir = os.path.dirname(checkpoint_path)
  m = re.compile(r'.*?\.ckpt\-([0-9]+)').match(checkpoint_path)
  name = 'eval-%d' % int(m.group(1)) if m else 'eval'
  return os.path.join(base_dir, name)


def run_eval(args):
  print(hparams_debug_string())
  synth = Synthesizer()
  modified_hp = hparams.parse(args.hparams)
  synth.load(args.checkpoint, modified_hp)

  base_path = get_output_base_path(args.checkpoint)
  for i, text in enumerate(sentences):
    path = '%s-%d.wav' % (base_path, i)
    print('Synthesizing: %s' % path)
    with open(path, 'wb') as f:
        data,wav = synth.eval(text)
        f.write(data)


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--checkpoint', required=True, help='Path to model checkpoint')
  parser.add_argument('--hparams', default='',
    help='Hyperparameter overrides as a comma-separated list of name=value pairs')
  args = parser.parse_args()
  os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
  hparams.parse(args.hparams)
  run_eval(args)


if __name__ == '__main__':
  main()