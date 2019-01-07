# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals

import re
import chardet
import requests
from lxml import etree
from pinyin2cn import cn_format

class CxExtractor:
    """cx-extractor implemented in Python"""

    __text = []
    __indexDistribution = []

    def __init__(self, threshold=86, blocksWidth=3):
        self.__blocksWidth = blocksWidth
        self.__threshold = threshold

    def getText(self, content):
        if self.__text:
            self.__text = []
        lines = re.split(r'[\n]', content)
       
        for i in range(len(lines)):
            lines[i] = re.sub("\r|\n|\\s", "",lines[i])
        self.__indexDistribution.clear()
        for i in range(0, len(lines) - self.__blocksWidth):
            wordsNum = 0
            for j in range(i, i + self.__blocksWidth):
                lines[j] = lines[j].replace("\\s", "")
                wordsNum += len(lines[j])
            self.__indexDistribution.append(wordsNum)
        start = -1
        end = -1
        boolstart = False
        boolend = False
        if len(self.__indexDistribution) < 3:
            return "",None
        for i in range(len(self.__indexDistribution) - 3):
            if(self.__indexDistribution[i] > self.__threshold and (not boolstart)):
                if (self.__indexDistribution[i + 1] != 0 or self.__indexDistribution[i + 2] != 0 or self.__indexDistribution[i + 3] != 0):
                    boolstart = True
                    start = i
                    continue
            if (boolstart):
                if (self.__indexDistribution[i] == 0 or self.__indexDistribution[i + 1] == 0):
                    end = i
                    boolend = True
            tmp = []
            if(boolend):
                for ii in range(start, end + 1):
                    if(len(lines[ii]) < 5):
                        continue
                    tmp.append(lines[ii] + "\n")
                str = "".join(list(tmp))
                if ("Copyright" in str or "版权所有" in str):
                    continue
                self.__text.append(str)
                boolstart = boolend = False
        result = "".join(list(self.__text))
        if result == '':
            #return 'This page has no content to extract'
            return "",None
        else:
            return "",result

    def replaceCharEntity(self, htmlstr):
        CHAR_ENTITIES = {'nbsp': ' ', '160': ' ',
                         'lt': '<', '60': '<',
                         'gt': '>', '62': '>',
                         'amp': '&', '38': '&',
                         'quot': '"', '34': '"', }
        re_charEntity = re.compile(r'&#?(?P<name>\w+);')
        sz = re_charEntity.search(htmlstr)
        while sz:
            entity = sz.group()
            key = sz.group('name')
            try:
                htmlstr = re_charEntity.sub(CHAR_ENTITIES[key], htmlstr, 1)
                sz = re_charEntity.search(htmlstr)
            except KeyError:
                htmlstr = re_charEntity.sub('', htmlstr, 1)
                sz = re_charEntity.search(htmlstr)
        return htmlstr

    def getHtml(self, url):
        response = requests.get(url)
        encode_info = chardet.detect(response.content)
        response.encoding = encode_info['encoding']
        return response.text

    def readHtml(self, path, coding):
        page = open(path, encoding=coding)
        lines = page.readlines()
        s = ''
        for line in lines:
            s += line
        page.close()
        return s

    def filter_tags(self, htmlstr):
        
        re_doctype = re.compile('<![DOCTYPE|doctype].*>')
        re_nav = re.compile('<nav.+</nav>')
        re_cdata = re.compile('//<!\[CDATA\[.*//\]\]>', re.DOTALL)
        re_script = re.compile(
            '<\s*script[^>]*>.*?<\s*/\s*script\s*>', re.DOTALL | re.I)
        re_style = re.compile(
            '<\s*style[^>]*>.*?<\s*/\s*style\s*>', re.DOTALL | re.I)
        re_textarea = re.compile(
            '<\s*textarea[^>]*>.*?<\s*/\s*textarea\s*>', re.DOTALL | re.I)
        re_p = re.compile('</?p\s*?>', re.DOTALL)
        re_br = re.compile('<br\s*?/?>')
        
        re_h = re.compile('</?\w+.*?>', re.DOTALL)
        re_comment = re.compile('<!--.*?-->', re.DOTALL)
        re_space = re.compile(' +')
        s = re_cdata.sub('', htmlstr)
        s = re_doctype.sub('',s)
        s = re_nav.sub('\n', s)
        s = re_script.sub('\n', s)
        s = re_style.sub('\n', s)
        s = re_textarea.sub('', s)
        s = re_p.sub('。',s)
        s = re_br.sub('', s)
        s = re_h.sub('', s)
        s = re_comment.sub('', s)
        s = re.sub('\\t', '', s)
        s = re_space.sub(' ', s)
        s = s.replace('#','')
        s = self.replaceCharEntity(s)
        return s
def parseBaidu(url,content):
    if "mbd.baidu.com" in url:
        htmlDom = etree.HTML(content)
        try:
            title = htmlDom.xpath("//div[@class='article-title']//h2/text()")[0]
            content = htmlDom.xpath("//div[@class='article-content']")[0]
            body = etree.tounicode(content)
            return True,title,body
        except Exception as e:
            print('文章解析失败')
            return False,"",""
    else:
        return False,"",""
def parseWX(url,content):
    if "mp.weixin.qq.com" in url:
        htmlDom = etree.HTML(content)
        try:
            title = htmlDom.xpath("//h2[@id='activity-name']/text()")[0]
            if len(title.strip()) == 0:
                title = re.search("rich_media_title_ios'>(.*?)</span",content).group(1)
            content = htmlDom.xpath("//div[@class='rich_media_content ']")[0]
            body = etree.tounicode(content)
            return True,title,body
        except Exception as e:
            print('文章解析失败')
            return False,"",""
    else:
        return False,"",""

def isWebUrl(where):
    regex = re.compile(
        r'^(?:http|ftp)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    v=regex.match(where)
    if v :
        return True
    else:
        return False

def get_article(url):
    cx = CxExtractor(threshold=80)
    #html = cx.getHtml("http://news.163.com/17/0810/09/CRFF02Q100018AOR.html")
    content = cx.getHtml(url)
    result,title,s =parseWX(url,content)
    if result:
        content = s
    result,title,s = parseBaidu(url,content)
    if result:
        content = s
    content = cx.filter_tags(content)
   
    t,s = cx.getText(content)
    if s == None:
         #print("get none")
         pass
    else:
         content = s
         title = t
    
    return title.strip(),content.strip()

if __name__ == "__main__":
    url = "https://mbd.baidu.com/newspage/data/landingsuper?context=%7B%22nid%22%3A%22news_9068434347012614858%22%7D&n_type=0&p_from=1"
    title,content = get_article(url)
    print(title,"\n")
   
    print("。".join(cn_format(content)))
   
    print(isWebUrl(url))