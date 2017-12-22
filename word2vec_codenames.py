# Copyright 2015 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
"""
for right now 12/21/17

use collocation() to make a dictionary and reverse_dictionary

use prepped_to_colloc() to convert natural language to a thesaurus-type data 
source

create a new collocation that includes the new thesaurus in the input data.





use word2vec on thesaurus and wikipedia data to establish meanings for the
 words to be used in Codenames. 
 Open issues:
     wikipedia scraper doesn't always pick an optimal page when disambiguation 
     pages are hit
     
     a good strategy for picking clues is not yet obvious. need to experiment.
     
     need to save model and use a new function to test decision making.
     """

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

#import operator
import collections
import math
import os
#import io
import random
import time
from tempfile import gettempdir
import zipfile
import string
import numpy as np
from six.moves import urllib
from six.moves import xrange  # pylint: disable=redefined-builtin
import tensorflow as tf
from sklearn.manifold import TSNE
import matplotlib.pyplot as plt
# Step 1: Download the data.
url = 'http://mattmahoney.net/dc/'
local_dir = "/mthes/mobythes.txt"
open_office_thes= "th_en_US_new1.dat"
ENC='latin_1'
#filename = maybe_download('text8.zip', 31344016)
filename = os.path.join(os.getcwd(),local_dir)

def scrape_power_thes(word,filen="appendix01.txt",min_upvotes=5,pass_on_words=False,write_here=True,rel=False):
    """ go to power thesaurus website,
    scrape appropriate words from page (max 20 without link taking)
    options:
        
        write_here (True) function will add entry to doc at filename. for large batches of words,
                            more efficient is to pass up newwords and append file once
        pass_on_words (False)  gives return newwords for batch processing and tracking
    """
    import requests
    from lxml import html
    #xml paths
    jar = requests.cookies.RequestsCookieJar()
    jar.set('settings','00400',domain='www.powerthesaurus.org',path='/')
    path1='//body/div[@class="container"]/div[@id="content"]/div[@id="main_side_container"]/div[@id="main"]/div[@id="topiccontent"]/div[@id="abb"]'
    table1='/table' #/tbody/tr
    #begin operations
    pt="https://www.powerthesaurus.org/"
    # additional pages are found pt + leaf + /synonyms/2 (or 3, etc.)
    leaf = word.replace(' ','_')
    pagen=1
    if rel==True:
        ext='/related'
    else:
        ext=''
    exitc=0
    #print('debug')
    while exitc==0:
        if pagen>1:
            ext="/synonyms/%i"%pagen
        rtry=0
        while rtry <12:
            try:
                rtry+=1
                page = requests.get(pt+leaf+ext,timeout=1,cookies=jar)
                print("scraping...%s/%i"%(word,pagen))
                if rtry>0:
                    time.sleep(5*rtry+4*random.random())
                tree = html.fromstring(page.content)
                entries = tree.xpath(path1+table1)[0].getchildren()
                break
            except:
                print("didn't load")
        if rtry>=12:
            exitc=1
            entries=[]
            
                #raise IOError("server is not cooperating")
        newwords=[]
        pagen+=1
        if len(entries)<200:
            exitc=1
        for entry in entries:
            v,w=entry.xpath('td')
            if int(v.xpath('div/div[@class="rating"]/text()')[0])<min_upvotes:
                exitc=1
                #print(word)
                break
            newwords.append(w.xpath('a/text()')[0])
    if len(newwords)==0:
        newwords.append(word)
            #print('plus')
        #return exitc

#append will start at end of existing line, not auto newline! (duh)
#for this version, appendix will be written in the style of the open office
#thesaurus, using pipes, though word sense disambiguation will not be performed
# and no part of speech specification will be included. 
# if it seems useful, perhaps develop these as options in this function
#example:
# beach|1
# shore|seaside|coast|strand|bank|seashore|seaboard|ground|coastline|littoral|seacoast|foreshore|shoreline
    if write_here== True:
        apx=open(filen,'a',encoding=ENC)
        apx.write(word+'|1\n')
        apx.write('|'.join(newwords)+'\n')
        apx.close()
    if pass_on_words == True:
        return newwords

def scrape_wiki(word):
    import requests
    from lxml import html
    wiki = "https://en.wikipedia.org/wiki/"
    listpath='//body/div[@id="content"]/div[@id="bodyContent"]/div[@id="mw-content-text"]/div[@class="mw-parser-output"]/ul/li/a/text()'
    docpath='//body/div[@id="content"]/div[@id="bodyContent"]/div[@id="mw-content-text"]/div[@class="mw-parser-output"]/p/text()'
    links='//body/div[@id="content"]/div[@id="bodyContent"]/div[@id="mw-content-text"]/div[@class="mw-parser-output"]/p/a/text()'
    cats ='//body/div[@id="content"]/div[@id="bodyContent"]/div[@id="catlinks"]/div[@id="mw-normal-catlinks"]/ul/li' 
    print("scraping...")
    leaf = word.replace(' ','_')
    page = requests.get(wiki+leaf)
    tree = html.fromstring(page.content)
    doc = tree.xpath(links)
    flat=[]
    new_leaf='n/a'
    disamb=0
    if tree.xpath(cats)[0].xpath('a')[0].get('href').find("Disambiguation")>0:
        disamb=1
    for i in doc:
        temp = i.translate(str.maketrans({key: " " for key in ['/','-']}))
        temp = temp.replace(r'\xa0',' ')
        temp = temp.translate(str.maketrans({key: None for key in string.punctuation or string.digits}))
        flat.extend(temp.lower().split(' '))
    flat=list(filter(lambda x: not x=='',flat))
    if len(flat)<=8 or disamb==1:
        #raise IOError("wikipedia disambiguation page was hit")
        path1 = 'body//div[@id="content"]/div[@id="bodyContent"]/div[@id="mw-content-text"]/div[@class="mw-parser-output"]/ul'
        path2 = 'body//div[@id="content"]/div[@id="bodyContent"]/div[@id="mw-content-text"]/div[@class="mw-parser-output"]/p'
        if disamb==1:
            #disambiguation page
            if len(tree.xpath(path2)[0].xpath('a'))==0:
                branches = tree.xpath(path1)
                buds = branches[0].xpath('li')
            else:
                buds = tree.xpath(path2)
        
            link = buds[0].xpath('a')[0].get('href')
            new_leaf = link.replace('/wiki/','')
        else:
            #stub
            doc2 = tree.xpath(docpath)
            for i in doc2:
                temp = i.translate(str.maketrans({key: " " for key in ['/','-']}))
                temp = temp.replace(r'\xa0',' ')
                temp = temp.translate(str.maketrans({key: None for key in string.punctuation or string.digits}))
                flat.extend(temp.lower().split(' '))
            flat=list(filter(lambda x: not x=='',flat))
            if len(flat)<=8:
                doc3 = tree.xpath(listpath)
                for i in doc3:
                    temp = i.translate(str.maketrans({key: " " for key in ['/','-']}))
                    temp = temp.replace(r'\xa0',' ')
                    temp = temp.translate(str.maketrans({key: None for key in string.punctuation or string.digits}))
                    flat.extend(temp.lower().split(' '))
                flat=list(filter(lambda x: not x=='',flat))
        
        
        #link = buds[0].xpath('a')[0].get('href')
        #new_leaf = link.replace('/wiki/','')
        
    return flat,new_leaf
# pylint: disable=redefined-outer-name
def maybe_download(filename, expected_bytes):
  """Download a file if not present, and make sure it's the right size."""
  local_filename = os.path.join(gettempdir(), filename)
  if not os.path.exists(local_filename):
    local_filename, _ = urllib.request.urlretrieve(url + filename,
                                                   local_filename)
  statinfo = os.stat(local_filename)
  if statinfo.st_size == expected_bytes:
    print('Found and verified', filename)
  else:
    print(statinfo.st_size)
    raise Exception('Failed to verify ' + local_filename +
                    '. Can you get to it with a browser?')
  return local_filename

# Read the data into a list of strings.
def read_data(filename):
  """Extract the first file enclosed in a zip file as a list of words."""
  with zipfile.ZipFile(filename) as f:
    data = tf.compat.as_str(f.read(f.namelist()[0])).split(',')
  return data

def read_data_txt(filename):
  """Extract the first file enclosed in a zip file as a list of words."""
  f=open(filename,'r')
  entries = tf.compat.as_str(f.read()).split('\n')
  data=list()
  for i in entries:
      data.extend(i.lower().split(','))
  f.close()
  return data, entries

def read_data_dat(filename):
    """Extract data from Open Office Thesaurus , separating word senses 
    format is as follows:
abel janszoon tasman|1
(noun)|Tasman|Abel Tasman|Abel Janszoon Tasman|navigator
abel tasman|1
(noun)|Tasman|Abel Tasman|Abel Janszoon Tasman|navigator
abelard|1
(noun)|Abelard|Peter Abelard|Pierre Abelard|philosopher|theologian|theologist|theologizer|theologiser
abele|1
(noun)|white poplar|white aspen|aspen poplar|silver-leaved poplar|Populus alba|poplar|poplar tree
abelia|1
(noun)|shrub|bush

    
    """
    th = open(filename,'r',encoding=ENC)
    #th.readline()#first line is not an entry
    data=[]
    try:
        while True:
            word,num=th.readline().replace('\n','').split('|')#num is the number of senses for a word
            entry=[word]
            for i in range(int(num)):
                temp=th.readline().replace('\n','').lower()
                if temp.find("                                                                         ")<0:
                    entry.append(temp.split('|'))
            data.append(entry)
    except ValueError:
        th.close()
    print("%i entries found" %len(data))
    #data is stored as [["abel janszoon tasman",["(noun)","tasman","abel tasman","abel janszoon tasman","navigator"]]...]
    return data
def prep_raw(inp, out):
    """the database is sentences, each separated by .\n
    preprocessing steps:
    replace '-' with ' '
    remove additional punctuation
    replace multiple spaces with a single space
    ??? should punctuation start a new line???
    this could be done easily at this stage. later, maybe
    """
    ip = open(inp,'r',encoding='UTF-8')
    ot = open(out,'w',encoding='UTF-8')
    for i in range(5000): #500 is the number of sentences to use during development
    #for line in ip:  #use this once done with dev
        temp = ip.readline()
        temp = temp.replace('-',' ')
        temp = temp.replace('“','')
        temp = temp.replace('”','')
        temp = temp.replace('•','')
        temp = temp.replace('—','')
        temp = temp.translate(str.maketrans({key: None for key in string.punctuation or string.digits}))
        
        templ = temp.lower().split(' ')
        templ = list(filter(lambda x: not x=='',templ))
        temp = ' '.join(templ)
        ot.write(temp)
    ip.close()
    ot.close()
    
def prepped_to_colloc(seedlist,dc,rd,nldata='news2011procd_dev',iterations=2,
                      thesname="collocationthesaurus001.txt",nlevels=3,mincut=3):
    """take natural language passages, and isolate the most common ordered collocations
(as if they are tuples). Using the lead word as a label, establish a new thesaurus
that contains the most common collocations for every word in a target list.
the target list is updated to include the collocated words in the next iteration, 
where the seedlist is the target list for the inital search.

needs: dictionary, reverse_dictionary

seedlist-- list of strings

dc -- dictionary, keys are strings, entries are ints
rd -- reverse dictionary, keys are ints, entries are strings
iterations -- int, number of times to expand on findings from initial seed.
thesname -- string, what to name the thesaurus written to hold the findings.
""" 
    #current plan
    #peek at top 50 lines of data in natural language corpus file
    #figure out necessary preprocessing. DO THIS IN SEPARATE func
    #call prepped raw data instead, since the proc is iterative
    #figure out a sneaky way to gather the info without mass translation
    # or expensive searching...
    #iterate the above
    #eventually, copy thesaurus formatting and writing from another func in
    # this module
    # test on smaller data set
    # use testing to establish useful threshholds.
    #seedlist
    
    targetlist=seedlist
    bigrams={}
    hits={}
    targs={}
    for i in range(iterations):
        sp = list(filter(lambda x: x.find(' ')>0,targetlist))
        spw=[]
        for isp in sp:
            spw.extend(isp.split(' '))
        #any codenames with spaces? clues can't contain spaces, so no need for support
        #beyond first iteration
        d =open(nldata,'r',encoding='UTF-8')
        for line in d:
            temp = line.replace('\n','').split(' ')
            for i2 in temp:
                if i2 in targetlist:
                    #get prev and next 
                    #save bigrams as numbers? sparseness precludes array or indicial storage
                  
                    if temp.index(i2)==0:
                        a=0
                    else:
                        a=dc.get(temp[temp.index(i2)-1],0)
                    b=dc.get(i2,0)
                    if len(temp)-temp.index(i2)==1:
                        c=0
                    else:
                        c=dc.get(temp[temp.index(i2)+1],0)
                    if hits.get(b,0) == 0:
                        hits[b]=[]
                    if not a == 0:
                        if not len(temp[temp.index(i2)-1]) < 3: 
                            #we are not interested in clues shorter than 3 letters long
                            ab = '%i %i'%(a,b)
                            if ab in bigrams.keys():
                                bigrams[ab]+=1
                            else:
                                bigrams[ab]=1
                                hits[b].append(a)
                    if not c == 0:
                        if not len(temp[temp.index(i2)+1]) < 3: 
                            bc = '%i %i'%(b,c)
                            if bc in bigrams.keys():
                                bigrams[bc]+=1
                            else:
                                bigrams[bc]=1
                                hits[b].append(c)
                elif i2 in spw:
                    mod= spw.index(i2)%2
                    full = sp[spw.index(i2)//2]
                    if min(len(temp)-temp.index(i2)-2+mod,temp.index(i2)-mod)>-1:
                        if temp[temp.index(i2)+1-2*mod] == spw[2*(spw.index(i2)//2)+1-mod]:
                            if temp.index(i2)==mod:
                                a=0
                            else:
                                a= dc.get(temp[temp.index(i2)-1-mod],0)
                            b= dc.get(full,0)
                            if len(temp)-temp.index(i2)==2-mod:
                                c=0
                            else:
                                c= dc.get(temp[temp.index(i2)+2-mod],0)
                            if hits.get(b,0) == 0:
                                hits[b]=[]
                            if not a == 0:
                                if not len(temp[temp.index(i2)-1-mod]) < 3: 
                                    #we are not interested in clues shorter than 3 letters long
                                    ab = '%i %i'%(a,b)
                                    if ab in bigrams.keys():
                                        bigrams[ab]+=1
                                    else:
                                        bigrams[ab]=1
                                        hits[b].append(a)
                            if not c == 0:
                                if not len(temp[temp.index(i2)+2-mod]) < 3: 
                                    bc = '%i %i'%(b,c)
                                    if bc in bigrams.keys():
                                        bigrams[bc]+=1
                                    else:
                                        bigrams[bc]=1
                                        hits[b].append(c)
    #return bigrams
        bg3={}
    #    bigs=[]
    #    nums=[]
        next_targetlist=[]
        for i in bigrams.keys():
            if bigrams[i] > mincut:
                bg3[i]=bigrams[i]
        for i in hits.keys():
    #        m=dc.get(i,0)
    #        if not m == 0:
            tl=[]
            for i2 in hits[i]:#get the number of times better collocation is found
                temp = max(bg3.get('%i %i'%(i,i2),0),bg3.get('%i %i'%(i2,i),0))
                if not temp ==0:
                    tl.append((temp,i2))
                    if not i2 in hits.keys():
                        word = rd.get(i2,0)
                        if not word == 0:
                            next_targetlist.append(word)
            tl.sort(key=lambda x: x[0], reverse=True)
            if not len(tl) == 0:
                targs[i]=tl
        targetlist=next_targetlist 
        ###### iteration reloads and rereads for new targets####
    ak = open(thesname,'w',encoding=ENC)
    for i in targs.keys():
        tempprob=[]
        tempwords=[]
        for i2 in targs[i]:
            tempprob.append(i2[0])
            tempwords.append(i2[1])
        odds=np.divide(tempprob,sum(tempprob))
        m = np.max(odds)
        n = nlevels
        lvls=np.linspace(m*n/(n+1),m/(n+1),num=n)
        for il in lvls:
            temp=[]
            for i3 in range(len(odds)):
                if odds[i3]>il:
                    wd = rd.get(tempwords[i3],'')
                    if not len(wd)==0:
                        if not wd in temp:
                            temp.append(wd)
            if not len(temp) == 0:
                ak.write(rd[i]+'|1\n')
                ak.write('|'.join(temp)+'\n')
    ak.close()          
    #leveling of associations is done linearly. although the data trends indicate
    #an exponential distribution of odds, the thesaurus building routine should
    #maintain the occurrence likelihoods for later odds ratio decision making.
    #the normalization performed here is relevant to the process of choosing word
    #specific clues.
    
#    for key in bg3.keys():
#        temp = key.split(' ')
#        #ts=''
#        for i in range(len(temp)):
#           temp[i]= rd[int(temp[i])]
#        #temp.append('%i'%(bg3[key]))
#        ts=' '.join(temp)
#        bigs.append(ts)
#        nums.append(bg3[key])
    return targs
    
def wsd(filen="wsd_thes.csv"):
    """Takes the thesaurus data from open office and finds and replaces words
    with word senses where possible.
    
    """
    wordlist=read_data_dat(open_office_thes)
    groups=[]
    vocabulary=[]
    for wordentry in wordlist:
        word=wordentry.pop(0)
        if len(wordentry)==1:
            vocabulary.append(word)
            vocabulary.extend(wordentry[0])#leaving in part of speech (noun) for now
            temp = [word]
            temp.extend(wordentry[0])
            groups.append(temp)
        else:
            vocabulary.append(word)
            for n,wordsense in enumerate(wordentry):
                vocabulary.extend(wordsense)
                ws = word + "(%i)" % n
                temp = [ws]
                temp.extend(wordsense)
                groups.append(temp)
    senselist=[]
    mlist=[]
    for group in groups:
        mlist.append(group[0])
        if group[0].find('(')>0:
        #only words with multiple senses    
            senselist.append(group[0])
    wsl2=list(filter(lambda x: x.find('(0)')>-1,senselist))
    ldex=list(map(lambda x: senselist.index(x),wsl2))
    ldex.append(len(senselist))
    nsenses= [ldex[i+1]-ldex[i] for i in range(len(ldex)-1)]
    wsl2=list(map(lambda x: x.replace('(0)',''),wsl2))
    
    for i1 in range(len(groups)):#add a progress indicator
        for i2 in range(2,len(groups[i1])):
            if groups[i1][i2] in wsl2:
                n=nsenses[wsl2.index(groups[i1][i2])]
                temp=[]
                for i3 in range(n):
                    temp.append(groups[mlist.index(groups[i1][i2]+'(%i)'%i3)])
                    #get the groups pertaining to the word sense
                temp = list(filter(lambda x: groups[i1][1] in x,temp))
                if len(temp)==1:
                    pass
                
        
def build_dataset(words, n_words):
  """Process raw inputs into a dataset."""
  count = [['UNK', -1]]
  count.extend(collections.Counter(words).most_common(n_words - 1))
  dictionary = dict()
  for word, _ in count:
    dictionary[word] = len(dictionary)
  data = list()
  unk_count = 0
  for word in words:
    index = dictionary.get(word, 0)
    if index == 0:  # dictionary['UNK']
      unk_count += 1
    data.append(index)
  count[0][1] = unk_count
  reversed_dictionary = dict(zip(dictionary.values(), dictionary.keys()))
  return data, count, dictionary, reversed_dictionary

def build_dataset2(groups, n_words):
  """Process raw inputs into a dataset."""
  fg = [item for sublist in groups for item in sublist]
  count = [['UNK', -1]]
  count.extend(collections.Counter(fg).most_common(n_words - 1))
  dictionary = dict()
  for word, _ in count:
    dictionary[word] = len(dictionary)
  data = list()
  unk_count = 0
  for group in groups:
      temp=[]
      for word in group:
        index = dictionary.get(word, 0)
        if index == 0:  # dictionary['UNK']
          unk_count += 1
        temp.append(index)
      data.append(temp)
  count[0][1] = unk_count
  reversed_dictionary = dict(zip(dictionary.values(), dictionary.keys()))
  return data, count, dictionary, reversed_dictionary

def generate_batch2(batch_size, num_skips, plus_rev = True):
  global data_index1
  global data_index2
  if plus_rev==True:
      fac=4
  else:
      fac=2
  assert batch_size % fac*num_skips == 0
  #assert num_skips <= 2 * skip_window
  batch = np.ndarray(shape=(batch_size), dtype=np.int32)
  labels = np.ndarray(shape=(batch_size, 1), dtype=np.int32)
  #span = 2 * skip_window + 1  # [ skip_window target skip_window ]
  #buffer = collections.deque()
  hf=int(fac/2)
  if data_index1 + 1 > len(data2):
    data_index1 = 0
  buffer=data2[data_index1]
  data_index1 += 1
  for i in range(batch_size // (fac*num_skips)):
    context_words = [w for w in range(1,len(buffer))]
    words_to_use = random.sample(context_words, num_skips)
    for j, context_word in enumerate(words_to_use):
      batch[fac*i * num_skips + hf*j] = buffer[0]
      labels[fac*i * num_skips + hf*j, 0] = buffer[context_word]
      if plus_rev == True:
          batch[fac*i * num_skips + hf*j+1] = buffer[context_word]#to get here, fac=4
          labels[fac*i * num_skips + hf*j+1, 0] = buffer[0]
    spokes = random.sample(range(len(buffer)),num_skips*2)
    for i2 in range(0,len(spokes),2):
      it=int(i2/2)
      batch[fac*i * num_skips + hf*num_skips+it*hf]=buffer[spokes[i2]]
      labels[fac*i * num_skips + hf*num_skips+it*hf, 0]=buffer[spokes[i2+1]]  
      if plus_rev == True:
          batch[fac*i * num_skips + hf*num_skips+it*hf+1]=buffer[spokes[i2+1]]
          labels[fac*i * num_skips + hf*num_skips+it*hf+1, 0]=buffer[spokes[i2]]
    if data_index1 == len(data2):
      buffer = data2[0]
      data_index1 = 1
    else:
      buffer = data2[data_index1]
      data_index1 += 1
  # Backtrack a little bit to avoid skipping words in the end of a batch
  data_index1 = (data_index1 + len(data2) - 1) % len(data2)
  return batch, labels

def generate_batch(batch_size, num_skips, skip_window):
  global data_index
  assert batch_size % num_skips == 0
  assert num_skips <= 2 * skip_window
  batch = np.ndarray(shape=(batch_size), dtype=np.int32)
  labels = np.ndarray(shape=(batch_size, 1), dtype=np.int32)
  span = 2 * skip_window + 1  # [ skip_window target skip_window ]
  buffer = collections.deque(maxlen=span)
  if data_index + span > len(data):
    data_index = 0
  buffer.extend(data[data_index:data_index + span])
  data_index += span
  for i in range(batch_size // num_skips):
    context_words = [w for w in range(span) if w != skip_window]
    words_to_use = random.sample(context_words, num_skips)
    for j, context_word in enumerate(words_to_use):
      batch[i * num_skips + j] = buffer[skip_window]
      labels[i * num_skips + j, 0] = buffer[context_word]
    if data_index == len(data):
      buffer[:] = data[:span]
      data_index = span
    else:
      buffer.append(data[data_index])
      data_index += 1
  # Backtrack a little bit to avoid skipping words in the end of a batch
  data_index = (data_index + len(data) - span) % len(data)
  return batch, labels

def plot_with_labels(low_dim_embs, labels, filename):
  assert low_dim_embs.shape[0] >= len(labels), 'More labels than embeddings'
  plt.figure(figsize=(18, 18))  # in inches
  for i, label in enumerate(labels):
    x, y = low_dim_embs[i, :]
    plt.scatter(x, y)
    plt.annotate(label,
                 xy=(x, y),
                 xytext=(5, 2),
                 textcoords='offset points',
                 ha='right',
                 va='bottom')

  plt.savefig(filename)
  
def collocation(dataf=[open_office_thes],voc_sz=120000,dim=100,min_co=0,appb=False):
    """appendix builder function set appb True to pass additional local data
    """
    vocabulary_size = voc_sz
    #sentences = list()
    #sentences= vocabulary.split('\n')
    #batch_size = 256
    #colist_target = dim  # Dimension of the embedding vector.
    #skip_window = 2       # How many words to consider left and right.
    #num_skips = 1         # How many times to reuse an input to generate a label.
    #num_sampled = 128      # Number of negative examples to sample.
    #valid_size = 8
    #num_steps = 100001
    wordlist=[]
    for dat in dataf: #now works with a list of datafiles as input
        wordlist.extend(read_data_dat(dat))
    groups=[]
    vocabulary=[]
    for wordentry in wordlist:
        word=wordentry.pop(0)
        if len(wordentry)==1:
            vocabulary.append(word)
            vocabulary.extend(wordentry[0])#leaving in part of speech (noun) for now
            temp = [word]
            temp.extend(wordentry[0])
            groups.append(temp)
        else:
            vocabulary.append(word)
            #for collocation model, wordsense disambig makes no difference
            temp=[word]
            for n,wordsense in enumerate(wordentry):
                vocabulary.extend(wordsense)
                #ws = word + "(%i)" % n
                #temp = [ws]
                temp.extend(wordsense)
            groups.append(temp)
    data, count, dictionary, reverse_dictionary = build_dataset(vocabulary, vocabulary_size)
    #let's try, for each word in vocab, have a dict. so: a list of dicts.
    coloc=list({} for i in range(voc_sz))
    ngr = list(list(dictionary.get(item,0) for item in sublist) for sublist in groups)
#    for i in range(1,voc_sz): WAAAY SLOWER THAN ALTERNATIVE
#        if i%1000==0:
#            print("collocating word %i of %i %s"%(i,voc_sz,time.ctime()))
#        #temp=list(filter(lambda x: i in ngr[x], range(len(ngr)))) #1:13*100
#        for i2,gr in enumerate(ngr):  #1:06
#            if i in gr:
#                temp.append(i2)
#        #temp = list(i2 for gr in ngr if i in gr)
#        for i2 in temp:
#            ntemp = ngr[i2].count(i)
#            for wn in ngr[i2]:
#                if wn == i:
#                    continue
#                else:
#                    coloc[i][wn]=coloc[i].get(wn,0)+ntemp
    for ig in range(len(ngr)): #group based approach, way faster
        if ig%10000==0:
            print("collocating group %i of %i %s"%(ig,len(ngr),time.ctime()))
        for i in ngr[ig]:
            for i2 in ngr[ig]:
                if not i == i2:
                        coloc[i][i2]=coloc[i].get(i2,0) + 1
        #coloc[i]
    #tcol=[]
    # reject key:value pairs where value < minimum? if >100 keys
    ##PRUNING FOR SPEED## optional...set min_co to 0
    #not working b/c dic changes size during iteration. change to do all after
    if not min_co==0:
        for i in range(len(coloc)):
            if len(coloc[i])>dim:
                for key in coloc[i]:
                    if coloc[i][key]<min_co:
                        del coloc[i][key]
    
    #conversion to probabilities from counts
    for i in range(len(coloc)):
        tot = sum(coloc[i].values())
        for key in coloc[i]:
            coloc[i][key]/=tot
    if appb==True:
        return coloc,reverse_dictionary,dictionary,count
    else:
        return coloc,reverse_dictionary

def test_coloc(coloc,rev_dic,dc,set_n=12,n_clues=20,wordl=[],mode=0,wmode=0,test_log="test_1to1_sets.txt"):
    """pass out test results
    will pad wordl to make len = set_n
    
    wmode = 0 wordl drawn from common (targets)
            1 wordl drawn from most frequent fifth of vocab in dictionary
            can also set wordl ahead of call 
    mode 0 pick the first clue in list
         1 pick a clue from clues at random
         2 tbd
    """
    tr = open("cdnmswordlist.txt",'r')#targets
    targets = tf.compat.as_str(tr.read()).split('\n')
    tr.close()
    missed=[]
    common=[dc.get(i,0) for i in targets]
    if wmode==0:
        wordlpre = random.sample(common,set_n)
        i=0
        while len(wordl)<set_n:
            wordl.append(wordlpre[i])
            i+=1
    else:
        wordlpre = random.sample(range(4,len(coloc)//5),set_n*100)
    #4 is to reject PoS and UNK. may change to different part of code
    #if wordl==[]:
        i=0
        while len(wordl)<set_n:
            if rev_dic[wordlpre[i]].find(' ')<0 and 1 in coloc[wordlpre[i]] and rev_dic[wordlpre[i]].find('-')<0:
                wordl.append(wordlpre[i])
            i+=1
    small=[]
    for i in range(set_n):
        temp = list((value, key) for key, value in coloc[wordl[i]].items())
        temp.sort(key=lambda x: x[0], reverse=True)
        small.append(temp)
    clu=[]
    #combo=[]
    #this section finds 1 to 1 clues. anything more complicated is experimental
    
    for w in range(set_n):
        candidates=[]
        pro=[]
        prob=[]
        odds=[]
        for i in range(len(small[w])):
            candidates.append(small[w][i][1])#word
            pro.append(small[w][i][0])#values
            odd = coloc[small[w][i][1]][wordl[w]]
            other= sum([coloc[small[w][i][1]].get(wordl[i2],0) for i2 in range(len(wordl)) if not i2 == w])
            prob.append(coloc[small[w][i][1]][wordl[w]])
            odds.append(odd/(other+odd))
        #what makes a good clue?
        #odds ratio is high
        #word is well-known
        #word has no spaces or hyphens
        #clue doesn't contain target
        combo=[(candidates[i],odds[i],prob[i],pro[i]) for i in range(len(small[w]))]
        combo.sort(key=lambda x: x[1],reverse=True)
        combo2=list(filter(lambda x: rev_dic[x[0]].find(' ')<0 and rev_dic[x[0]].find('-')<0 and rev_dic[x[0]].find(rev_dic[wordl[w]])<0 and len(rev_dic[x[0]])>=3,combo))
        oddslim=0.8*max([combo2[i][1] for i in range(len(combo2))])
        cluelist=list(filter(lambda x: x[1]>=oddslim,combo2))
        #cluelist.sort(key=lambda x: x[1]+x[2]+min(x[2],x[3]),reverse=True)
        cluelist.sort(key=lambda x: x[0])
        cutoff=max(len(cluelist)//4,min(n_clues,len(cluelist)))
        cluelist2=list(cluelist[i] for i in range(cutoff))
        cluelist2.sort(key=lambda x: x[2], reverse=True)
        clues=[(rev_dic[cluelist2[i][0]],cluelist2[i][0],cluelist2[i][1],cluelist2[i][2],cluelist2[i][3]) for i in range(min(n_clues,len(cluelist2)))]
        clu.append(clues)
    if mode==0:
        clu2=[clu[i][0] for i in range(len(clu))]
    elif mode==1:
        clu2=[clu[i][random.choice(range(len(clu[i])))] for i in range(len(clu))]
    else:
        pass
    #adding: output clues and words as 
    clu2f=[clu2[i][0] for i in range(len(clu2))]
    random.shuffle(clu2f)
    wordsl=[rev_dic[i] for i in wordl]
    
    n='1'
    for i in range(2,set_n+1):
        n=n+', %i'%i
    out=open(test_log,'a')
    out.write(','.join(clu2f)+'\n\n')
    out.write(n+'\n')
    out.write(','.join(wordsl)+'\n')
    out.close()
 
    return clu, wordl
def test2_coloc(coloc,rev_dic,Wset_n=12,Bset_n=12,n_clues=20):
    """pass out test results
    
    """    
    # for a two-word clue, search would include the candidates for all whitelist words.
    # let's assume we see full word list (blacklist and whitelist)
    # our goal is to find any clues that give higher odds of selecting both
    # included words than anything else
    # define confidence as Min(odds(incl words))-max(odds(other words))
    
    
def build_appendix(filena='appendix01.txt',voc_sz1=120000,mode='w',all_targets=False,min_votes1=5,related=False):
    """using powerthesaurus.org, a group-sourced online database, build an additional
    thesaurus to supplement the open office 
    """
    coloc,rev_dc,dc,count=collocation(voc_sz=voc_sz1,appb=True)
    tr = open("cdnmswordlist.txt",'r')#targets
    targets = tf.compat.as_str(tr.read()).split('\n')
    tr.close()

    missed=[]
    common=[dc.get(i,0) for i in targets]
    if all_targets==True:
        missed.extend(targets)
    else:
        for i in range(len(common)):
            if common[i]==0:
                missed.append(targets[i])
    to_look_up=[]
    root_syns=[]
    branch_syns=[]
    for word in missed:
        newwords = scrape_power_thes(word,pass_on_words=True,write_here=False,min_upvotes=min_votes1)
        to_look_up.extend(newwords)
        root_syns.append(newwords)
    for word in to_look_up:
        newwords = scrape_power_thes(word,pass_on_words=True,write_here=False,min_upvotes=min_votes1)
        branch_syns.append(newwords)
    apx=open(filena,mode,encoding=ENC)
    #apx.write(filena+'\n')
    for i in range(len(missed)):
        apx.write(missed[i]+'|1\n')
        apx.write('|'.join(root_syns[i])+'\n')
    for i in range(len(to_look_up)):
        apx.write(to_look_up[i]+'|1\n')
        apx.write('|'.join(branch_syns[i])+'\n')
    apx.close()
    print("Found %i words for appendix"%(len(missed)+len(to_look_up)))
    
    
        #if newwords has only one word in the list...

def build(keep=False,voc_sz=100000,dim=128,scrape_all=False,use_new_th=True):
    global data_index1
    global data2
    global data
    global data_index
    vocabulary_size = voc_sz
    #sentences = list()
    #sentences= vocabulary.split('\n')
    batch_size = 256
    embedding_size = dim  # Dimension of the embedding vector.
    #skip_window = 2       # How many words to consider left and right.
    num_skips = 1         # How many times to reuse an input to generate a label.
    num_sampled = 128      # Number of negative examples to sample.
    valid_size = 8
    num_steps = 100001
    if use_new_th == True:
        wordlist=read_data_dat(open_office_thes)
        groups=[]
        vocabulary=[]
        for wordentry in wordlist:
            word=wordentry.pop(0)
            if len(wordentry)==1:
                vocabulary.append(word)
                vocabulary.extend(wordentry[0])#leaving in part of speech (noun) for now
                temp = [word]
                temp.extend(wordentry[0])
                groups.append(temp)
            else:
                vocabulary.append(word)
                for n,wordsense in enumerate(wordentry):
                    vocabulary.extend(wordsense)
                    ws = word + "(%i)" % n
                    temp = [ws]
                    temp.extend(wordsense)
                    groups.append(temp)
        data, count, dictionary, reverse_dictionary = build_dataset(vocabulary, vocabulary_size)
        #above call is separated for future specification        
    else:
        vocabulary ,entries= read_data_txt(filename)
        print('Data size', len(vocabulary))
        groups=list()
        for i in range(len(entries)):
            groups.append(entries[i].split(','))
    
    # Step 2: Build the dictionary and replace rare words with UNK token.

    # Filling 4 global variables:
    # data - list of codes (integers from 0 to vocabulary_size-1).
    #   This is the original text but words are replaced by their codes
    # count - map of words(strings) to count of occurrences
    # dictionary - map of words(strings) to their codes(integers)
    # reverse_dictionary - maps codes(integers) to words(strings)
        data, count, dictionary, reverse_dictionary = build_dataset(vocabulary,
                                                                vocabulary_size)
    del vocabulary  # Hint to reduce memory.
    print('Most common words (+UNK)', count[:12])
    print('Sample data', data[:10], [reverse_dictionary[i] for i in data[:10]])
    

    data_index1 = 0
    #data_index2 = 0
    
    tr = open("cdnmswordlist.txt",'r')#targets
    targets = tf.compat.as_str(tr.read()).split('\n')
    tr.close()
    missed=[]
    common=[dictionary.get(i,0) for i in targets]
    for i in range(len(common)):
        if common[i]==0:
            missed.append(targets[i])
    #for words not in thesaurus, get related words from wikipedia
    
    wgroups=[] 
    if scrape_all == True:
        missed = targets
    for word in missed:
        flat,new_leaf = scrape_wiki(word)
        print(len(flat))
        if not new_leaf=='n/a':
            print("Disambiguated %s to %s"%(word,new_leaf))
            flat,new_leaf = scrape_wiki(new_leaf)
            print(len(flat))
        #new = list(filter(lambda x: x in dictionary.keys(),flat))
        enter = [word]
        enter.extend(flat)#or new
        wgroups.append(enter)
        
    groups.extend(wgroups)
    
    
    wg = [item for sublist in wgroups for item in sublist]
    wgf=list(filter(lambda x: dictionary.get(x,0)==0,wg))
    vocabulary_size2 = vocabulary_size + len(collections.Counter(wgf))
    print("vocabulary size after scraping: %i"%vocabulary_size2)
    data2, count2, dictionary2, reverse_dictionary2 = build_dataset2(groups,
                                                                vocabulary_size2)
    common2=[dictionary2.get(i,0) for i in targets]
    # Step 3: Function to generate a training batch for the skip-gram model.
    #completely rework to sample entries and then randomly pair a word from the entry with the first word
    
    
    batch, labels = generate_batch2(batch_size=8, num_skips=2)
    for i in range(8):
      print(batch[i], reverse_dictionary2[batch[i]],
            '->', labels[i, 0], reverse_dictionary2[labels[i, 0]])
    
    # Step 4: Build and train a skip-gram model.
    common2f = list(filter(lambda x: not x==0, common2))
    print(common2f[:])
    
    # We pick a random validation set to sample nearest neighbors. Here we limit the
    # validation samples to the words that have a low numeric ID, which by
    # construction are also the most frequent. These 3 variables are used only for
    # displaying model accuracy, they don't affect calculation.
         # Random set of words to evaluate similarity on.
    #valid_window = 100  # Only pick dev samples in the head of the distribution.
    #valid_examples = np.random.choice(common2f, valid_size, replace=False)
    valid_examples = common2f[:valid_size]#deterministic to check changes
    
    graph = tf.Graph()
    
    with graph.as_default():
    
      # Input data.
      train_inputs = tf.placeholder(tf.int32, shape=[batch_size])
      train_labels = tf.placeholder(tf.int32, shape=[batch_size, 1])
      valid_dataset = tf.constant(valid_examples, dtype=tf.int32)
    
      # Ops and variables pinned to the CPU because of missing GPU implementation
      with tf.device('/cpu:0'):
        # Look up embeddings for inputs.
        embeddings = tf.Variable(
            tf.random_uniform([vocabulary_size2, embedding_size], -1.0, 1.0))
        embed = tf.nn.embedding_lookup(embeddings, train_inputs)
    
        # Construct the variables for the NCE loss
        nce_weights = tf.Variable(
            tf.truncated_normal([vocabulary_size2, embedding_size],
                                stddev=1.0 / math.sqrt(embedding_size)))
        nce_biases = tf.Variable(tf.zeros([vocabulary_size2]))
    
      # Compute the average NCE loss for the batch.
      # tf.nce_loss automatically draws a new sample of the negative labels each
      # time we evaluate the loss.
      # Explanation of the meaning of NCE loss:
      #   http://mccormickml.com/2016/04/19/word2vec-tutorial-the-skip-gram-model/
      loss = tf.reduce_mean(
          tf.nn.nce_loss(weights=nce_weights,
                         biases=nce_biases,
                         labels=train_labels,
                         inputs=embed,
                         num_sampled=num_sampled,
                         num_classes=vocabulary_size2))
    
      # Construct the SGD optimizer using a learning rate of 1.0.
      optimizer = tf.train.GradientDescentOptimizer(1.0).minimize(loss)
    
      # Compute the cosine similarity between minibatch examples and all embeddings.
      norm = tf.sqrt(tf.reduce_sum(tf.square(embeddings), 1, keep_dims=True))
      normalized_embeddings = embeddings / norm
      valid_embeddings = tf.nn.embedding_lookup(
          normalized_embeddings, valid_dataset)
      similarity = tf.matmul(
          valid_embeddings, normalized_embeddings, transpose_b=True)
    
      # Add variable initializer.
      init = tf.global_variables_initializer()
    
    # Step 5: Begin training.

    
    with tf.Session(graph=graph) as session:
      # We must initialize all variables before we use them.
      init.run()
      print('Initialized')
    
      average_loss = 0
      for step in xrange(num_steps):
        batch_inputs, batch_labels = generate_batch2(
            batch_size, num_skips)
        feed_dict = {train_inputs: batch_inputs, train_labels: batch_labels}
    
        # We perform one update step by evaluating the optimizer op (including it
        # in the list of returned values for session.run()
        _, loss_val = session.run([optimizer, loss], feed_dict=feed_dict)
        average_loss += loss_val
    
        if step % 2000 == 0:
          if step > 0:
            average_loss /= 2000
          # The average loss is an estimate of the loss over the last 2000 batches.
          print('Average loss at step ', step, ': ', average_loss)
          average_loss = 0
    
        # Note that this is expensive (~20% slowdown if computed every 500 steps)
        if step % 10000 == 0:
          sim = similarity.eval()
          for i in xrange(valid_size):
            valid_word = reverse_dictionary2[valid_examples[i]]
            top_k = 80  # number of nearest neighbors
            nearest = (-sim[i, :]).argsort()[1:top_k + 1]
            log_str = 'Nearest to %s:' % valid_word
            nearest.sort()
            keep = 8
            best = nearest[:keep]
            for k in xrange(keep):
              close_word = reverse_dictionary2[best[k]]
              log_str = '%s %s %f,' % (log_str, close_word, sim[i,best[k]])
            
            print(log_str)
          for i in xrange(3):
              for i2 in range(i+1,valid_size):
                  valid_word = reverse_dictionary2[valid_examples[i]]
                  vw2 = reverse_dictionary2[valid_examples[i2]]
                  top_k = 80  # number of nearest neighbors
                  nearest = (-sim[i, :]-sim[i2,:]).argsort()[2:top_k + 2]
                  log_str = 'Nearest to %s and %s:' %(valid_word,vw2)
                  nearest.sort()
                  keep = 8
                  best = nearest[:keep]
                  for k in xrange(keep):
                    close_word = reverse_dictionary2[best[k]]
                    log_str = '%s %s %f %f,' % (log_str, close_word, sim[i,best[k]], sim[i2,best[k]])
                  print(log_str)
      final_embeddings = normalized_embeddings.eval()
      sim =similarity.eval()
      #best clues for valid_size words to select each from out of set
      log_str ='Word List:'+ ' '.join([reverse_dictionary2[valid_examples[i]] for i in range(valid_size)])
      print(log_str)
      top_k = 80  # number of nearest neighbors
      baseline=sim[0,:]
      for i in range(1,valid_size):
          baseline=baseline+sim[i,:]
      baseline = baseline/valid_size
      for i in xrange(valid_size):
          nearest = (baseline[:]-sim[i, :]).argsort()[1:top_k + 1]
          log_str = 'clues for %s:' % reverse_dictionary2[valid_examples[i]]
          nearest.sort()
          keep = 4
          best = nearest[:keep]
          for k in xrange(keep):
            close_word = reverse_dictionary2[best[k]]
            log_str = '%s %s %f,' % (log_str, close_word, sim[i,best[k]]-baseline[best[k]])
          print(log_str)
    # Step 6: Visualize the embeddings.
    
    
    # pylint: disable=missing-docstring
    # Function to draw visualization of distance between embeddings.
    
    
    try:
      # pylint: disable=g-import-not-at-top

      #plt.figure()
      tsne = TSNE(perplexity=30, n_components=2, init='pca', n_iter=5000, method='exact')
      plot_only = 500
      low_dim_embs = tsne.fit_transform(final_embeddings[:plot_only, :])
      labels = [reverse_dictionary[i] for i in xrange(plot_only)]
      plot_with_labels(low_dim_embs, labels, os.path.join(os.getcwd(), 'tsne.png'))
    
    except ImportError as ex:
      print('Please install sklearn, matplotlib, and scipy to show embeddings.')
      print(ex)
    if keep==True:
        return final_embeddings, count2, dictionary2, reverse_dictionary2, targets

if __name__ is "__main__":
    build()
