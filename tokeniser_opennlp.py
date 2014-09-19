#!/usr/bin/env python
#-*- coding: utf8 *-*

import sys
import getopt
import argparse
from subprocess import Popen, PIPE
from lxml.etree import ElementTree as ET, Element as EL
import time
import os
from KafNafParserPy import *

__name = 'Open-nlp sentence splitter and tokeniser'
__version__ = '1.0'
__last_modified = '19sep2014'
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
  parser = argparse.ArgumentParser(description='Sentence splitter and tokeniser based on open-nlp')
  parser.add_argument('-l','-lang', dest='lang',help='Language of the input text', required=True)
  parser.add_argument('-notime',dest='time',action='store_true',help='Timestamp not included in header')
  parser.add_argument('-naf', dest='naf',action='store_true',help='Generate NAF output')
  args = parser.parse_args()

  if sys.stdin.isatty():
      print>>sys.stderr,'Input stream required.'
      print>>sys.stderr,'Example usage: cat myUTF8file.txt |',sys.argv[0]
      sys.exit(-1)

     
  if args.lang == 'nl':
    token_model = token_model_nl
    sentence_model = sentence_model_nl
  elif args.lang == 'en':
    token_model = token_model_en
    sentence_model = sentence_model_en
  elif args.lang   == 'de':
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
  
  # By default a KAF file will be generated. if -naf option is given will be NAF
  type_obj = 'KAF'
  if args.naf:
      type_obj = 'NAF'
      
  knaf_obj = KafNafParser(type=type_obj)
  knaf_obj.set_language(args.lang)
  knaf_obj.set_version('1.0')
  
  num_token = 1
  offset = 0
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
        token_obj = Cwf(type=type_obj)
        token_obj.set_id('w'+str(num_token))
        token_obj.set_sent(str(num_sent+1))
        token_obj.set_offset(str(offset))
        token_obj.set_text(token)
        offset+=(1+len(token))
        knaf_obj.add_wf(token_obj)
        
      
      token_pro.terminate()
  
      
  my_lp = Clp()
  my_lp.set_name(__name)
  my_lp.set_version(__version__+'#'+__last_modified)
  if args.time:
      my_lp.set_timestamp()
  else:
      my_lp.set_timestamp('*')
  knaf_obj.add_linguistic_processor ('text', my_lp)
  knaf_obj.dump()
    
  sentence_pro.terminate()

