# -*- coding: utf-8 -*-

import argparse
import os

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("--txt")
	parser.add_argument("--dir")
	args = parser.parse_args()

	text_file = args.txt 
	with open(text_file, encoding='gbk') as fp:
		while True:
			names = fp.readline().split('\t');
			if len(names) == 0:
				break
			basename = names[0]
			text = names[1]
			print(basename)
			trns = fp.readline().split('\t')
			trn = trns[1]
			txt_file = os.path.join(args.dir, basename + '.txt')
			with open(txt_file, mode='w', encoding='utf-8') as txt_fp:
				txt_fp.write(text)
			trn_file = os.path.join(args.dir, basename + '.trn')
			with open(trn_file, mode='w', encoding='utf-8') as trn_fp:
				trn_fp.write(trn)

if __name__ == '__main__':
	main()
