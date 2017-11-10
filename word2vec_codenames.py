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
"""use word2vec on thesaurus and wikipedia data to establish meanings for the
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

import collections
import math
import os
import random
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

#filename = maybe_download('text8.zip', 31344016)
filename = os.path.join(os.getcwd(),local_dir)

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


def build(keep=False,voc_sz=100000,dim=128,scrape_all=False):
    global data_index1
    global data2
    global data
    global data_index
    vocabulary ,entries= read_data_txt(filename)
    print('Data size', len(vocabulary))
    groups=list()
    for i in range(len(entries)):
        groups.append(entries[i].split(','))
    
    # Step 2: Build the dictionary and replace rare words with UNK token.
    vocabulary_size = voc_sz
    #sentences = list()
    #sentences= vocabulary.split('\n')
    batch_size = 256
    embedding_size = dim  # Dimension of the embedding vector.
    #skip_window = 2       # How many words to consider left and right.
    num_skips = 4         # How many times to reuse an input to generate a label.
    num_sampled = 128      # Number of negative examples to sample.
    valid_size = 8
    num_steps = 100001
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
    
    tr = open("/Users/aarontallman/Downloads/cdnmswordlist.txt",'r')#targets
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
