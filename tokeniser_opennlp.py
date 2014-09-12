#!/usr/bin/env python
#-*- coding: utf8 *-*

import sys
import getopt
from subprocess import Popen, PIPE
from lxml.etree import ElementTree as ET, Element as EL
import time
import os

__version__ = '1.0 27 February 2013'
this_folder = os.path.dirname(os.path.realpath(__file__))


######### VARS ######
opennlp_folder = '/home/ruben/apache-opennlp-1.5.2-incubating'
model_folder = os.path.join(opennlp_folder,'models')
################

opennlp_exe = os.path.join(this_folder,opennlp_folder,'bin/opennlp')
token_model_nl = os.path.join(model_folder,'nl-token.bin')
sentence_model_nl = os.path.join(model_folder,'nl-sent.bin')
token_model_en = os.path.join(model_folder,'en-token.bin')
sentence_model_en = os.path.join(model_folder,'en-sent.bin')
token_model_de = os.path.join(model_folder,'de-token.bin')
sentence_model_de = os.path.join(model_folder,'de-sent.bin')
######################


if __name__ == '__main__':
  if sys.stdin.isatty():
      print>>sys.stderr,'Input stream required.'
      print>>sys.stderr,'Example usage: cat myUTF8file.txt |',sys.argv[0]
      sys.exit(-1)
  
  time_stamp = True
  my_lang = 'nl'
  try:
    opts, args = getopt.getopt(sys.argv[1:],"l:",["no-time","lang="])
    for opt, arg in opts:
      if opt == "--no-time":
        time_stamp = False
      elif opt in ['--lang','-l']:
        my_lang = arg
  except getopt.GetoptError:
    pass
    
  if my_lang == 'nl':
    token_model = token_model_nl
    sentence_model = sentence_model_nl
  elif my_lang == 'en':
    token_model = token_model_en
    sentence_model = sentence_model_en
  elif my_lang   == 'de':
    token_model = token_model_de
    sentence_model = sentence_model_de  
  else:
    token_model = token_model_nl
    sentence_model = sentence_model_nl
  ## To remove break lines from the input
  my_text = ''
  for line in sys.stdin:
    my_text += line.strip()+' '
  
  #my_text = sys.stdin.read().strip()
  
  ## CALL TO THE SENTENCE SPLITTER
  cmd = opennlp_exe+' SentenceDetector '+sentence_model
  sentence_pro = Popen(cmd,shell=True,stdin=PIPE,stdout=PIPE,stderr=PIPE)
  sentence_pro.stdin.write(my_text)
  sentence_pro.stdin.close()
  
  kafEle = EL('KAF')
  kafEle.set('{http://www.w3.org/XML/1998/namespace}lang',my_lang)
  kafEle.set('version','1.0')

  kaf_header = EL('kafHeader')
  kafEle.append(kaf_header)
  
  eleLPtext = EL('linguisticProcessors',attrib={'layer':'text'})
  kaf_header.append(eleLPtext)
  
  if time_stamp:
    my_time_stamp = time.strftime('%Y-%m-%dT%H:%M:%S%Z')
  else:
    my_time_stamp = '*'
  
  
  ele_lp1 = EL('lp',attrib={'name':'Open-nlp sentence splitter', 'version':'1.0','timestamp':my_time_stamp})
  eleLPtext.append(ele_lp1)
  
  ele_lp2 = EL('lp',attrib={'name':'Open-nlp tokenizer', 'version':'1.0','timestamp':my_time_stamp})
  eleLPtext.append(ele_lp2)
    
  kaf_text = EL('text')
  kafEle.append(kaf_text)
  
  num_token = 1
  for num_sent, sentence in enumerate(sentence_pro.stdout):
    #Sentence is basic type str
    sentence = sentence.strip()
    if len(sentence)!=0:
     
      token_cmd = opennlp_exe+' TokenizerME '+ token_model
      token_pro = Popen(token_cmd,shell=True, stdin=PIPE,stdout=PIPE,stderr=PIPE)
      token_pro.stdin.write(sentence)
      token_pro.stdin.close()
      
      
      tokens = token_pro.stdout.read().strip().decode('utf-8').split(' ')
      for token in tokens:
        kaf_wf = EL('wf',attrib={'wid':'w_'+str(num_token),
                                 'sent': ''+str(num_sent+1)})
        num_token += 1
        kaf_wf.text = token
        kaf_text.append(kaf_wf)
      
      token_pro.terminate()
  
      
  
    
  sentence_pro.terminate()
  ET(element=kafEle).write(sys.stdout,encoding='UTF-8',pretty_print=1, xml_declaration=1)
  import time
