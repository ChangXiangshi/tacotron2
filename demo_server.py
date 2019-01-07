import falcon
import tensorflow as tf
import re
import io
from hparams import hparams
from infolog import log
from tacotron.synthesizer import Synthesizer
from wsgiref import simple_server
import argparse
from pypinyin import pinyin, lazy_pinyin, Style
from scipy.io.wavfile import write
import numpy as np
from datasets import audio
import itertools
import jieba
from pinyin2cn import cn2pinyin,cn_format
import hashlib
from pydub import AudioSegment
import json
import os
import mimetypes
from subprocess import Popen, PIPE
import pyaudio
from web_html import isWebUrl,get_article

html_body = '''<html><title>Tcotron-2 Demo</title><meta charset='utf-8'>
<style>
body {padding: 16px; font-family: sans-serif; font-size: 14px; color: #444}
input {font-size: 14px; padding: 8px 12px; outline: none; border: 1px solid #ddd}
input:focus {box-shadow: 0 1px 2px rgba(0,0,0,.15)}
p {padding: 12px}
button {background: #28d; padding: 9px 14px; margin-left: 8px; border: none; outline: none;
        color: #fff; font-size: 14px; border-radius: 4px; cursor: pointer;}
button:hover {box-shadow: 0 1px 2px rgba(0,0,0,.15); opacity: 0.9;}
button:active {background: #29f;}
button[disabled] {opacity: 0.4; cursor: default}
</style>
<body>
<form>
  <input id="text" type="text" size="40" placeholder="请输入文字或网址">
  <br/>
  <div>
		<input name="type" checked type="radio" value="g1"/><label>正常女</label>
		<input name="type" type="radio" value="g2"/><label>小姐姐</label>
    <input name="type" type="radio" value="g3"/><label>汤姆猫</label>
    <input name="type" type="radio" value="b1"/><label>正常男</label>
  </div>
   <br/>
  <button id="button" name="synthesize">合成</button>
</form>
</br>
<audio id="audio" controls autoplay hidden></audio>
<p id="message"></p>
<script>
function radio(name){
  var radios = document.getElementsByName(name)
  var value = ""
  for(var i=0;i<radios.length;i++){
    if(radios[i].checked == true){
      value = radios[i].value
    }
  }
  return value
}

contents = []
playlist = []
playerStatus = false

function q(selector) {return document.querySelector(selector)}
q('#text').focus()
q('#button').addEventListener('click', function(e) {
  text = q('#text').value.trim()
  if (text) {
    q('#message').textContent = '合成中...'
    q('#button').disabled = true
    q('#audio').hidden = true
    t = radio("type")
    //synthesize(text,t)
    contents = []
    playlist = []
    playerStatus = false

    parse(text,t)
  }
  e.preventDefault()
  return false
})



q('#audio').addEventListener("ended", function() {
  if(playlist.length == 0){
    q('#message').textContent = '播放完成.'
  }else{
    q('#message').textContent = '合成中...'
  }
  playerStatus = false
  play()
  
})


function parse(text,t){
  fetch('/read?text=' + encodeURIComponent(text), {cache: 'no-cache'})
    .then(function(res) {
      if (!res.ok) throw Error(res.statusText)
      return res.json()
    }).then(function(result) {
      q('#message').textContent = ''
      q('#button').disabled = false
      contents = result["content"]
      if( contents.length > 0){
        content = contents.shift()
        q('#message').textContent = '合成中...'
        synthesize(content,t)
      }
    }).catch(function(err) {
      q('#message').textContent = '出错: ' + err.message
      q('#button').disabled = false
    })
}
function play(){
  if(playerStatus) return
  if( playlist.length > 0){
    playerStatus = true
    c = playlist.shift()
    q('#message').textContent = c[0]
    q('#audio').src = URL.createObjectURL(c[1])
    q('#audio').hidden = false
  }
  if( contents.length > 0){
    content = contents.shift()
    synthesize(content,t)
  }
}
function synthesize(text,t) {
  fetch('/synthesize?type=' + t + '&text=' + encodeURIComponent(text), {cache: 'no-cache'})
    .then(function(res) {
      if (!res.ok) throw Error(res.statusText)
      return res.blob()
    }).then(function(blob) {
      //q('#message').textContent = text
      playlist.push([text,blob])
      play()
      q('#button').disabled = false
      //q('#audio').src = URL.createObjectURL(blob)
      //q('#audio').hidden = false
    }).catch(function(err) {
      q('#message').textContent = '出错: ' + err.message
      q('#button').disabled = false
    })
}
</script></body></html>
'''


jieba.load_userdict("user_dict/jieba1.txt")
jieba.load_userdict("user_dict/jieba.txt")
jieba.load_userdict("user_dict/user_dict")



parser = argparse.ArgumentParser()
parser.add_argument('--checkpoint', default='pretrained/', help='Path to model checkpoint')
parser.add_argument('--hparams', default='',help='Hyperparameter overrides as a comma-separated list of name=value pairs')
parser.add_argument('--port', default=9003,help='Port of Http service')
parser.add_argument('--host', default="localhost",help='Host of Http service')
parser.add_argument('--name', help='Name of logging directory if the two models were trained together.')
args = parser.parse_args()
synth = Synthesizer()
modified_hp = hparams.parse(args.hparams)
synth.load(args.checkpoint, modified_hp)

def gen(content,t):
  out = io.BytesIO()
  output = np.array([])
  mhash = hashlib.md5(content.encode(encoding='UTF-8')).hexdigest()
  print(content)
  content = cn2pinyin(content)
  print(len(content))
  ts = content.split("E")
  for text in ts:
    text = text.strip()
    if len(text) <= 0:
      continue
    text += " E"
    print(">>>>>"+text)
    data,wav = synth.eval(text)
    output = np.append(output, wav, axis=0)
  
  audio.save_wav(output,out, hparams.sample_rate)

  if t == "g1":
    mp3_path = "wavs/"+mhash + ".mp3"
    song = AudioSegment.from_file(out, format='wav')
    song.set_frame_rate(hparams.sample_rate)
    song.set_channels(2)
    filter = "atempo=0.95,highpass=f=300,lowpass=f=3000,aecho=0.8:0.88:6:0.4"
    song.export(mp3_path, format="mp3",parameters=["-filter_complex",filter,"-q:a", "4", "-vol", "150"])
    out2 = io.BytesIO()
    song.export(out2, format="mp3",parameters=["-filter_complex",filter,"-q:a", "4", "-vol", "150"])
    data = out2.getvalue()
    return mp3_path, data
  else:
    effect ="-rate=-5 -pitch=+4"
    if t == "g3":
      effect ="-rate=+45 -pitch=+3"
    elif t == "b1":
      effect ="-pitch=-4"
    wav_file = "wavs/"+mhash + ".wav"
    audio.save_wav(output,wav_file,hparams.sample_rate)
    mp3_file = "wavs/"+mhash + ".mp3"
    out_file = "wavs/"+mhash + "1.wav"
   # effect ="-rate=-5 -pitch=+4" #"-rate=-10 -pitch=+8" 小姐姐 #"-rate=+45 -pitch=+3" 汤姆猫
    popen = Popen("soundstretch "+wav_file+" "+out_file+" "+effect, shell=True, stdout=PIPE, stderr=PIPE)  
    popen.wait()  
    if popen.returncode != 0:  
      print("Error.")

    song = AudioSegment.from_wav(out_file)
    song.set_frame_rate(hparams.sample_rate)
    song.set_channels(1)
    filter = "atempo=0.95,highpass=f=200,lowpass=f=1000,aecho=0.8:0.88:6:0.4"
    song.export(mp3_file, format="mp3",parameters=["-filter_complex",filter,"-q:a", "4", "-vol", "200"])
    out2 = io.BytesIO()
    song.export(out2, format="mp3",parameters=["-filter_complex",filter,"-q:a", "4", "-vol", "200"])
    data = out2.getvalue()

  # mp3_path = "wavs/"+mhash + ".mp3"
  # song = AudioSegment.from_file(out, format='wav')
  # song.set_frame_rate(hparams.sample_rate)
  # song.set_channels(2)
  # filter = "atempo=0.95,highpass=f=300,lowpass=f=3000,aecho=0.8:0.88:6:0.4"
  # song.export(mp3_path, format="mp3",parameters=["-filter_complex",filter,"-q:a", "4", "-vol", "150"])
  # out2 = io.BytesIO()
  # song.export(out2, format="mp3",parameters=["-filter_complex",filter,"-q:a", "4", "-vol", "150"])
  # data = out2.getvalue()
  # return mp3_path, data
  
  return mp3_file, data

class Sound:
  def on_get(self,req,resp,mp3):
    file_path = os.path.join("wavs", mp3)
    if not os.path.exists(file_path):
        # from pudb import set_trace; set_trace()
        msg = 'Resource doesn\'t Exist'
        raise falcon.HTTPNotFound('Not Found', msg)
    resp.status = falcon.HTTP_200
    resp.content_type = mimetypes.guess_type(file_path, strict=False)
    resp.stream = open(file_path, 'rb')
    resp.stream_len = os.path.getsize(file_path)
    

class Res:
  def on_get(self,req,resp):
    resp.status = falcon.HTTP_200
    resp.body = html_body
    resp.content_type = "text/html"


class SynMp3:
  def on_get(self,req,resp):
    if not req.params.get('text'):
      raise falcon.HTTPBadRequest()
    content = req.params.get('text')
    mp3_path,out = gen(content,"g1")
    result={}
    result["code"] =0
    result["path"] = "http://"+ args.host + ":" + args.port +"/"+ mp3_path
    result["text"] = content

    resp.status = falcon.HTTP_200
    resp.body = json.dumps(result)
    resp.content_length = len(resp.body)

class Read:
    def on_get(self,req,resp):
      if not req.params.get('text'):
        raise falcon.HTTPBadRequest()
      content = req.params.get('text')
      title = ""
      if isWebUrl(content):
        title,content = get_article(content)
      result = cn_format(content)
      print(result)
      out = []
      splitStr =""
      for text in result:
        splitStr += text + "。"
        if len(splitStr) >= 120:
          out.append(splitStr)
          splitStr= ""

      if len(splitStr) > 0:
          out.append(splitStr)
          splitStr= ""
      print(out)
      resp.status = falcon.HTTP_200
      result={}
      result["code"] = 0
      result["content"] = out
      result["title"] = title
      resp.body = json.dumps(result)
      resp.content_length = len(resp.body)

class Syn:
  def on_get(self,req,resp):
    if not req.params.get('text'):
      raise falcon.HTTPBadRequest()
    content = req.params.get('text')
    t = req.params.get('type')
    if isWebUrl(content):
      title,content = get_article(content)
    print("type :",t)
    mp3_path,out = gen(content,t)
    resp.status = falcon.HTTP_200
    resp.data = out
    resp.content_type = "audio/mp3"
    


api = falcon.API()
api.add_route("/",Res())
api.add_route("/synthesize", Syn())
api.add_route("/create",SynMp3())
api.add_route("/wavs/{mp3}",Sound())
api.add_route("/read", Read())
print("host:{},port:{}".format(args.host,int(args.port)))
simple_server.make_server(args.host,int(args.port),api).serve_forever()
