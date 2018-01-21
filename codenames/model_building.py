#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jan 20 21:09:28 2018

@author: aarontallman
"""
mport collections
import math
import os
# import io
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
import requests
from lxml import html
open_office_thes = "th_en_US_new2.dat"
ENC = 'latin_1'
ENC = 'UTF-8' #see if this breaks things???


def make_full_model():
    """ease of use function, returns dict model,
    model[0] is collocation data
    model[1] is a reverse dictionary for wordstrings from ints
    model[2] is a dictionary for ints from wordstrings
    runs using *best* thesauri and weighting 
    
    * best is subject to change, and this function must be updated 
    to reflect any changes
    """
    model={}
    best_data=['europarl-v6.enthes.txt','fulllist_appx.txt',open_office_thes,'wiki_full_2deg.txt']
    [model[0],model[1],model[2],count]=collocation(dataf=best_data,weights=[1,3,1,20],appb=True)
    return model


def collocation(dataf=[open_office_thes], weights=[1], voc_sz=120000, dim=100, min_co=0, appb=False):
    """appendix builder function set appb True to pass additional local data
    weight is list of ints, same len as dataf, controls the weight given 
        to each file in dataf
    """
    vocabulary_size = voc_sz
    # sentences = list()
    # sentences= vocabulary.split('\n')
    # batch_size = 256
    # colist_target = dim  # Dimension of the embedding vector.
    # skip_window = 2       # How many words to consider left and right.
    # num_skips = 1         # How many times to reuse an input to generate a label.
    # num_sampled = 128      # Number of negative examples to sample.
    # valid_size = 8
    # num_steps = 100001
    wordlist = []
    if len(weights)==1 and len(dataf)>1:
        weights = [1 for i in range(len(dataf))]
    for i in range(len(dataf)):  # now works with a list of datafiles as input
        wordlist.extend(read_data_dat(dataf[i],weight=weights[i]))
    groups = []
    vocabulary = []
    for wordentry in wordlist:
        word = wordentry.pop(0)
        if len(wordentry) == 1:
            vocabulary.append(word)
            vocabulary.extend(wordentry[0])  # leaving in part of speech (noun) for now
            temp = [word]
            temp.extend(wordentry[0])
            groups.append(temp)
        else:
            vocabulary.append(word)
            # for collocation model, wordsense disambig makes no difference
            temp = [word]
            for n, wordsense in enumerate(wordentry):
                vocabulary.extend(wordsense)
                # ws = word + "(%i)" % n
                # temp = [ws]
                temp.extend(wordsense)
            groups.append(temp)
    data, count, dictionary, reverse_dictionary = build_dataset(vocabulary, vocabulary_size)
    # let's try, for each word in vocab, have a dict. so: a list of dicts.
    coloc = list({} for i in range(voc_sz))
    ngr = list(list(dictionary.get(item, 0) for item in sublist) for sublist in groups)

    for ig in range(len(ngr)):  # group based approach, way faster
        if ig % 10000 == 0:
            print("collocating group %i of %i %s" % (ig, len(ngr), time.ctime()))
        for i in ngr[ig]:
            for i2 in ngr[ig]:
                if not i == i2:
                    coloc[i][i2] = coloc[i].get(i2, 0) + 1
 
    ##PRUNING FOR SPEED## optional...set min_co to 0
    # not working b/c dic changes size during iteration. change to do all after
    if not min_co == 0:
        for i in range(len(coloc)):
            if len(coloc[i]) > dim:
                for key in coloc[i]:
                    if coloc[i][key] < min_co:
                        del coloc[i][key]

    # conversion to probabilities from counts
    for i in range(len(coloc)):
        tot = sum(coloc[i].values())
        for key in coloc[i]:
            coloc[i][key] /= tot
    if appb == True:
        return coloc, reverse_dictionary, dictionary, count
    else:
        return coloc, reverse_dictionary
    
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

