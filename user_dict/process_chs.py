# -*- coding: utf-8 -*-
import glob
import os
import re

from zhon.hanzi import punctuation

if __name__ == "__main__":
    
    output_path = "jieba1.txt"
    fout = open(output_path, 'wb')
    dic = {}
    input_dir = "/Volumes/MyDisk/studio/ai/Tacotron/data_thchs30/"
    trn_files = glob.glob(os.path.join(input_dir, "data", '*.trn'))
    for trn in trn_files:
        with open(trn,encoding='utf-8') as f:
            basename = trn[:-4]
            zhText = f.readline()
            arr = zhText.split(" ")
            print(zhText)
            for text in arr:
                if len(text.strip()) > 1:
                    dic[text] = text.strip()

    for k,v in dic.items():
        fout.write(f'{v}\n'.encode('utf-8'))