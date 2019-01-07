# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
import itertools
from pypinyin import lazy_pinyin, load_phrases_dict,pinyin, Style
import pypinyin
import json
import re
import jieba
import os
import glob
from jieba import posseg


_replacement_expression = [(re.compile('{}'.format(x[0]), re.IGNORECASE), x[1]) for x in [
    ('#0', 'A'),
    ('#1', 'B'),
    ('#2', 'C'),
    ('#3', 'D'),
    ('#4', 'E')
]]

# PUNCTUATION = ['”', '"', ';', ':', '(', ")", ";", ",", "?", "!", "\"", "\'", "."]
# PUNCTUATION_FULL=['、', '”', '“', '；', '：', '（', "）", "：", "；", "，", "？", "！", "‘", "。"]



# alpha_pronuce = {"A": "ei ", "B": "bii ", "C": "sii ", "D": "dii ", "E": "ii ", "F": "ef ", "G": "dji ", "H": "eich ",
#                  "I": "ai ", "J": "jei ", "K": "kei ", "L": "el ", "M": "em ", "N": "en ",
#                  "O": "eo ", "P": "pii ", "Q": "kiu ", "R": "aa ", "S": "es ", "T": "tii ", "U": "iu ", "V": "vii ",
#                  "W": "dabliu ", "X ": "eiks ", "Y": "wai ", "Z": "zii "}

alpha_pronuce = {"A":"诶","B":"毕","C":"西","D":"弟","E":"易","F":"哎负","G":"记","H":"诶吃","I":"唉","J":"捷","K":"尅","L":"哎奥","M":"哎目","N":"嗯","O":"噢","P":"屁","Q":"可优","R":"啊","S":"艾斯","T":"替","U":"呦","V":"为","W":"大不溜","X":"埃克斯","Y":"歪","Z":"贼"}

# def punctuationProcess(content):
#     rep = {'\n':'','\r':'','“':'','”':'','。':'.','！':'.','；':'.','？':'.','、':' ','，':'#','：':','}
#     rep = dict((re.escape(k), v) for k, v in rep.items())
#     pattern = re.compile("|".join(rep.keys()))
#     content = pattern.sub(lambda m: rep[re.escape(m.group(0))], content)
#     return content

def json_load():
    with open("user_dict/fault-tolerant_word.json", "r") as rf:
        data = json.load(rf)
    return data


# usr_phrase = json_load()
# load_phrases_dict(usr_phrase)

def num2chinese(num, big=False, simp=True, o=False, twoalt=False):
    """
    Converts numbers to Chinese representations.
    `big`   : use financial characters.
    `simp`  : use simplified characters instead of traditional characters.
    `o`     : use 〇 for zero.
    `twoalt`: use 两/兩 for two when appropriate.
    Note that `o` and `twoalt` is ignored when `big` is used, 
    and `twoalt` is ignored when `o` is used for formal representations.
    """
    # check num first
   
    nd = str(num)
    if abs(float(nd)) >= 1e48:
        raise ValueError('number out of range')
    elif 'e' in nd:
        raise ValueError('scientific notation is not supported')
    c_symbol = '正负点' if simp else '正負點'
    if o:  # formal
        twoalt = False
    if big:
        c_basic = '零壹贰叁肆伍陆柒捌玖' if simp else '零壹貳參肆伍陸柒捌玖'
        c_unit1 = '拾佰仟'
        c_twoalt = '贰' if simp else '貳'
    else:
        c_basic = '〇一二三四五六七八九' if o else '零一二三四五六七八九'
        c_unit1 = '十百千'
        if twoalt:
            c_twoalt = '两' if simp else '兩'
        else:
            c_twoalt = '二'
    c_unit2 = '万亿兆京垓秭穰沟涧正载' if simp else '萬億兆京垓秭穰溝澗正載'
    revuniq = lambda l: ''.join(k for k, g in itertools.groupby(reversed(l)))
    nd = str(num)
    result = []
    if nd[0] == '+':
        result.append(c_symbol[0])
    elif nd[0] == '-':
        result.append(c_symbol[1])
    if '.' in nd:
        integer, remainder = nd.lstrip('+-').split('.')
    else:
        integer, remainder = nd.lstrip('+-'), None
    if int(integer):
        splitted = [integer[max(i - 4, 0):i]
                    for i in range(len(integer), 0, -4)]
        intresult = []
        for nu, unit in enumerate(splitted):
            # special cases
            if int(unit) == 0:  # 0000
                intresult.append(c_basic[0])
                continue
            elif nu > 0 and int(unit) == 2:  # 0002
                intresult.append(c_twoalt + c_unit2[nu - 1])
                continue
            ulist = []
            unit = unit.zfill(4)
            for nc, ch in enumerate(reversed(unit)):
                if ch == '0':
                    if ulist:  # ???0
                        ulist.append(c_basic[0])
                elif nc == 0:
                    ulist.append(c_basic[int(ch)])
                elif nc == 1 and ch == '1' and unit[1] == '0':
                    # special case for tens
                    # edit the 'elif' if you don't like
                    # 十四, 三千零十四, 三千三百一十四
                    ulist.append(c_unit1[0])
                elif nc > 1 and ch == '2':
                    ulist.append(c_twoalt + c_unit1[nc - 1])
                else:
                    ulist.append(c_basic[int(ch)] + c_unit1[nc - 1])
            ustr = revuniq(ulist)
            if nu == 0:
                intresult.append(ustr)
            else:
                intresult.append(ustr + c_unit2[nu - 1])
        result.append(revuniq(intresult).strip(c_basic[0]))
    else:
        result.append(c_basic[0])
    if remainder:
        result.append(c_symbol[2])
        result.append(''.join(c_basic[int(ch)] for ch in remainder))
    return ''.join(result)


def ch2p(speech):
    if type(speech) == str:
        # print('拼音转换: ', speech)
        syllables = lazy_pinyin(speech, style=pypinyin.TONE3)
        # print('---------1 ', speech, '----------')
        print(syllables)
        #syllables = text2pinyin(syllables)
        text = ' '.join(syllables)
        
        return text
    else:
        print("input format error")


def num2han(value):
    num_han = {0: '零', 1: '一', 2: '二', 3: '三', 4: '四', 5: '五', 6: '六', 7: '七', 8: '八', 9: '九'}
    value = ''.join(x for x in value if x in "0123456789")
    value = ''.join(num_han.get(int(x)) for x in value)
    return value


def num2phone(value):
    num_han = {0: '零', 1: '妖', 2: '二', 3: '三', 4: '四', 5: '五', 6: '六', 7: '七', 8: '八', 9: '九'}
    value = ''.join(x for x in value if x in "0123456789")
    value = ''.join(num_han.get(int(x)) for x in value)
    return value

def replaceNum(matched):
    try:
        data = matched.group("num")
        return num2chinese(data)
    except:
        return ""

def replacePercent(matched):
    try:
        data = matched.group("percent")
        return "百分之"+num2chinese(data)+","
    except:
        return ""


def replaceYMD(matched):

    arr = []
    opt = ["year","month","day","hour","minute","second"]
    for o in opt:
        try:
            data = matched.group(o)
            if o == "year":
                arr.append(num2han(data))
                arr.append("年")
            elif o == "month":
                arr.append(num2chinese(data))
                arr.append("月")
            elif o == "day":
                arr.append(num2chinese(data))
                arr.append("日")
            elif o == "hour":
                arr.append(num2chinese(data))
                arr.append("时")
            elif o == "minute":
                arr.append(num2chinese(data))
                arr.append("分")
            elif o == "second":
                arr.append(num2chinese(data))
                arr.append("秒")
        except IndexError:
            continue
  
    return "".join(arr)

def replaceYMDEx(matched):

    arr = []
    opt = ["year","year2"]
    for o in opt:
        try:
            data = matched.group(o)
            if o == "year":
                arr.append(num2han(data))
                arr.append("至")
            elif o == "year2":
                arr.append(num2han(data))
                arr.append("年")
            
        except IndexError:
            continue
  
    return "".join(arr)

def matchYMDEx(content):
    regs = [
        r"((?P<year>\d{4})[-|至](?P<year2>\d{4})年)"
    ]
    replacedStr = content
    for reg in regs:
        replacedStr = re.sub(reg, replaceYMDEx, replacedStr)

    return replacedStr

def matchYMD(content):
    regs = [
        r"((?P<year>\d{4})[-|\s|年|/](?P<month>\d{1,2})[-|\s|月|/](?P<day>\d{1,2})[日]*)",
        r"((?P<year>\d{4})[-|\s|年|/](?P<month>\d{1,2})[-|\s|月]*)",
        r"((?P<month>\d{1,2})[-|\s|月|/](?P<day>\d{1,2})[日]*)",
        r"((?P<year>\d{4})年)",
        r"((?P<hour>\d{1,2})[:|时](?P<minute>\d{1,2})[:|分](?P<second>\d{1,2})[秒]*)",
        r"((?P<hour>\d{1,2})[:|时](?P<minute>\d{1,2})[:|分]*)",
    ]
    replacedStr = content
    for reg in regs:
        replacedStr = re.sub(reg, replaceYMD, replacedStr)

    return replacedStr

def matchPercent(content):
    regs = [
        r"((?P<percent>[0-9.]+)%)",
    ]
    replacedStr = content
    for reg in regs:
        replacedStr = re.sub(reg, replacePercent, replacedStr)

    return replacedStr

def matchEn(content):
    regs = [
        r"((?P<english>[A-Z]*[a-z\/α]{1,})\s*)+"
    ]
    replacedStr = content
    for reg in regs:
        replacedStr = re.sub(reg, "叉叉", replacedStr)
    return replacedStr

def replacePhone(matched):
    try:
        data = matched.group("phone")
        if len(data) == 11:
            return num2phone(data)
        else:
            return num2chinese(data)
    except:
        return ""

def matchPhone(content):
    regs = [
        r'(?P<phone>1[3-9]\d{9,100})',
    ]
    replacedStr = content
    for reg in regs:
        replacedStr = re.sub(reg, replacePhone, replacedStr)

    return replacedStr

def matchNum(content):
    regs = [
        r"((?P<num>[0-9.]+))",
    ]
    replacedStr = content
    for reg in regs:
        replacedStr = re.sub(reg, replaceNum, replacedStr)

    return replacedStr

def replaceTag(content):
    for regex, replacement in _replacement_expression:
        content = re.sub(regex, " "+replacement+" ", content)
    return content

def matchAlpha(content):
    for alpha, pronuce in alpha_pronuce.items():
        content = content.replace(alpha, pronuce)
    content = content.replace("  "," ")
    # content = content.replace("  "," ")
    return content

def matchPronuce(content):
    rep = {'-':'至','《':'','》':'','【':'','】':'','—':'','“':'','”':'','～':'','~':'','「':'','」':'','*':'','……':',','◆':'','\n':'','\r':'','，':',','“':'','”':'','！':'。','；':'。','？':'。','、':',','：':'。','?':'。',':':'。','!':'。',"（":"","）":"","(":"",")":"","[":"","]":""}
    rep = dict((re.escape(k), v) for k, v in rep.items())

    pattern = re.compile("|".join(rep.keys()))
    content = pattern.sub(lambda m: rep[re.escape(m.group(0))], content)

    return content

# def preprocessText(content):
#     content = matchAlpha(content)
#     content = matchSplit(content)
#     content = matchYMD(content)
#     content = matchPercent(content)
#     content = matchPhone(content)
#     content = matchNum(content)
    
#     return content



def cutstrpos(txt):
    # 分词+词性
    cutstr = posseg.cut(txt)
    result = []
    for word, flag in cutstr:
        #result += word + "/" + flag + ' '
        if len(word.strip()) <= 0:
            continue
        result.append(word)
    
    return result
    # return " ".join(jieba.cut(txt,cut_all=True))

def _adjust(prosody_txt):
    prosody_words = re.split('#\d', prosody_txt)
    rhythms = re.findall('#\d', prosody_txt)
    txt = ''.join(prosody_words)
    words = []
    for word in cutstrpos(txt):
        words.append(word)
    index = 0
    insert_time = 0
    length = len(prosody_words[index])
    i = 0
    while i < len(words):
        done = False
        while not done:
            if (len(words[i]) > length):
                #print(words[i], prosody_words[index])
                length += len(prosody_words[index + 1])
                rhythms[index] = ''
                index += 1
            elif (len(words[i]) < length):
                # print(' less than ', words[i], prosody_words[index])
                rhythms.insert(index + insert_time, '#0')
                insert_time += 1
                length -= len(words[i])
                i += 1
            else:
                # print('equal :', words[i])
                # print(rhythms)
                done = True
                index += 1
        else:
            if (index < len(prosody_words)):
                length = len(prosody_words[index])
            i += 1
    if rhythms[-1] != '#4':
        rhythms.append('#4')
    rhythms = [x for x in rhythms if x != '']
    result = []
    for i in range(len(words)):
        result.append(words[i])
        result.append(rhythms[i])
        
    return result


def txt2label(txt):
   #txt = re.sub(r'(?!#)\W', '', txt)
    if '#' in txt:
        txt = re.sub(r'(?!#)\W', '', txt)
        words = _adjust(txt)
    else:
        
        words = []
        contents = re.split(r'[\,\，]', txt.strip())
        
        for content in contents:
            if len(content) <= 0:
                continue
            for word in cutstrpos(content):
                words.append(word.strip())
                words.append("#0")
            words.pop()
            words.append("#3")
        words.pop()
        words.append("#4")
    return "".join(words)

def p(input):
    txt = ""
    arr = pinyin(input, style=Style.TONE3)
    for i in arr:
        txt += i[0] + " "
    txt = txt.replace("  "," ")
    return txt

def cn_format(content):
    if '#' not in content:
        content = matchPercent(content)
        content = matchYMDEx(content)
        content = matchYMD(content)
        content = matchPronuce(content)
        content = matchEn(content)
        content = matchPhone(content)
        content = matchNum(content)
        content = matchAlpha(content)
        
    contents = []
    preContents = re.split(r'[\。\.]+', content.strip())
    preSplit = ""
    for txt in preContents:
        preSplit = ""
        txts = re.split(r'[\,\，]', txt.strip())
        for t in txts :
            if len(preSplit) == 0:
                preSplit = t
            else:
                preSplit += "，" + t

            if len(preSplit) > 40:
                contents.append(preSplit)
                preSplit = ""
        if len(preSplit) > 0:
            contents.append(preSplit)
            preSplit = ""
    if len(preSplit) > 0:
        contents.append(preSplit)
    return contents

def cn2pinyin(content):
    contents = cn_format(content)

    result = []
    for txt in contents:
        if len(txt) <= 0:
            continue
        txt = txt2label(txt)
        txt = replaceTag(txt)
        txt = p(txt)
        result.append(txt)
    return "".join(result)

def process_biaobei(input_dir):
    trn_files = glob.glob(os.path.join(input_dir, "data", '*.txt'))
    for trn in trn_files:
        with open(trn,encoding='utf-8') as f:
            basename = trn[:-4]
            print(basename)
            zhText = f.readline().strip()
            text = cn2pinyin(zhText)
            output_path = basename + ".new"
            print(text)
            with open(output_path, 'wb') as fout:
                fout.write(f'{text}'.encode('utf-8'))

def process_thcns(input_dir):
    trn_files = glob.glob(os.path.join(input_dir, "data", '*.wav.trn'))
    for trn in trn_files:
        with open(trn,encoding='utf-8') as f:
            basename = trn[:-4]
            print(basename)
            zhText = f.readline().strip()
            text = cn2pinyin(zhText)
            output_path = basename + ".new"
            with open(output_path, 'wb') as fout:
                fout.write(f'{zhText}\n{text}\n{text}'.encode('utf-8'))
if __name__ == "__main__":
    
    jieba.load_userdict("user_dict/jieba1.txt")
    jieba.load_userdict("user_dict/jieba.txt")
    jieba.load_userdict("user_dict/user_dict")

    # print(num2han(value="010194567898"))
    # print(num2chinese("3418.91"))
    # print(num2chinese("2418.91", twoalt=True))
    content = "北斗系统是中国自主建设、独立运行，与世界其他卫星导航系统兼容共用的全球卫星导航系统，可在全球范围，全天候、全天时，为各类用户提供高精度、高可靠的定位、导航、授时服务。自上世纪90年代开始，北斗系统启动研制，按“三步走”发展战略，先有源后无源，先区域后全球，先后建成北斗一号、北斗二号、北斗三号系统，走出了一条中国特色的卫星导航系统建设道路。"
    content =cn2pinyin(content)
    ts = content.split("E")
    for text in ts:
        print(text)
    # process_biaobei("data_thchs30")
    # process_thcns("data_thchs30")
