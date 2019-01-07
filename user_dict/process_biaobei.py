# -*- coding: utf-8 -*-
import glob
import os
import re

from zhon.hanzi import punctuation

if __name__ == "__main__":
    input_path = "000001-010000.txt"
    output_path = "jieba.txt"
    fout = open(output_path, 'wb')
    dic = {}
    with open(input_path,encoding="utf-8") as file :
        lines = list(file)
        maxLen = len(lines)
        i = 0
        while i < maxLen :
            chinese = lines[i]
            result = re.match( r'(\d+)\s(.*)', chinese)
            pinyin = lines[i+1].strip()
            no =(result.group(1))
            chinese = (result.group(2))

            content = re.sub(r'(#\d{1})','#', chinese)
            content = re.sub("[{}]+".format(punctuation), "", content)
            print(content)
            arr = content.split("#")
            for text in arr:
                if len(text.strip()) > 1:
                    dic[text] = text.strip()
            i+=2
            
    for k,v in dic.items():
        fout.write(f'{v}\n'.encode('utf-8'))