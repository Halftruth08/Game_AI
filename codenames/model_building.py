#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jan 20 21:09:28 2018

@author: aarontallman
"""
import os
import collections
import time
import pickle
LOCAL=os.path.dirname(os.path.dirname(__file__))
CDNM =LOCAL+'/data/wordslist.txt'
MODELS=LOCAL+'/data/models'
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
    for i in range(len(best_data)):
        best_data[i] = LOCAL+'/data/thesauri/'+best_data[i]
    [model[0],model[1],model[2],count]=collocation(dataf=best_data,weights=[1,3,1,20],appb=True)
    return model

def store_model(model):
    """docstring goes here
    
    Usage:
        stored_name = store_model(model)
        model - model as returned by make_full_model()
    """
    existing_models=list(filter(lambda a: a.find('model')>-1,os.listdir(MODELS)))
    model_numbers=list(map(lambda a: int(a.replace('model','')),existing_models))
    model_numbers.append(0)
    stored_name='model'+'{:02d}'.format(max(model_numbers)+1)
    h=open(MODELS+'/'+stored_name,'wb')
    pickle.dump(model,h,protocol=pickle.HIGHEST_PROTOCOL)
    h.close()
    return stored_name

def load_model(stored_name):
    h=open(MODELS+'/'+stored_name,'rb')
    model=pickle.load(h)
    return model

def collocation(dataf=[LOCAL+'/data/thesauri/'+open_office_thes], weights=[1], voc_sz=120000, dim=100, min_co=0, appb=False):
    """appendix builder function set appb True to pass additional local data
    weight is list of ints, same len as dataf, controls the weight given 
        to each file in dataf
    """
    vocabulary_size = voc_sz
    wordlist = []
    if len(weights)==1 and len(dataf)>1:
        weights = [1 for i in range(len(dataf))]
    for i in range(len(dataf)):  # now works with a list of datafiles as input
        wordlist.extend(read_data_dat(dataf[i],weight=weights[i]))
    groups = []
    groupweights=[]
    vocabulary = []
    for wordentry in wordlist:
        word = wordentry.pop(0)
        wnum = int(wordentry.pop(0))
        groupweights.append(wnum)
        if len(wordentry) == 1:
            for rep in range(wnum):
                vocabulary.append(word)
                vocabulary.extend(wordentry[0])  # leaving in part of speech (noun) for now
            temp = [word]
            temp.extend(wordentry[0])
            groups.append(temp)
        else:
            for rep in range(wnum):
                vocabulary.append(word)
            # for collocation model, wordsense disambig makes no difference
            temp = [word]
            for n, wordsense in enumerate(wordentry):
                for rep in range(wnum):
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
                    coloc[i][i2] = coloc[i].get(i2, 0) + groupweights[ig]
 
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

def read_data_dat(filename,weight=1):
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
    th = open(filename, 'r', encoding=ENC)
    # th.readline()#first line is not an entry
    data = []
    try:
        while True:
            word, num = th.readline().replace('\n', '').split('|')  # num is the number of senses for a word
            num=int(num)*weight
            entry = [word,str(num)]
            temp = th.readline().replace('\n', '').lower()
            if temp.find("                                                                         ") < 0:
                entry.append(temp.split('|'))
            data.append(entry)
    except ValueError:
        th.close()
    print("%i entries found, given weight = %i" %(len(data),weight))
    # data is stored as [["abel janszoon tasman",["(noun)","tasman","abel tasman","abel janszoon tasman","navigator"]]...]
    return data