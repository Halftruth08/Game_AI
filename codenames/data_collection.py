#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jan 20 21:08:47 2018

@author: aarontallman
"""
import os
import random
import time
import string
import numpy as np
import requests
from lxml import html
LOCAL=os.path.dirname(os.path.dirname(__file__))
CDNM =LOCAL+'/data/wordslist.txt'
THES=LOCAL+'/data/thesauri'
RAW=LOCAL+'/data/raw'
open_office_thes = "th_en_US_new2.dat"
ENC = 'latin_1'
ENC = 'UTF-8' #see if this breaks things???
tr = open(CDNM, 'r',encoding=ENC)  # targets
TARGETS = tr.read().split('\n')
tr.close()

def build_appendix(targets,filena='PTsynonyms01.txt',model={}, mode='w', min_votes1=5, related=False):
    """using powerthesaurus.org, a group-sourced online database, build an additional
    thesaurus to supplement the open office
    Usage:
        targets: list of strings, indicating codenames, or other words.
                These become to focus of the new thesaurus.
        filena: string filename of the new thesaurus to be built in the 
                appropriate folder
        model: optional, if included, the web will only scrape for 
                target words not already present. See 
                codenames.model_building.make_full_model() for the structure
                of model
        mode: 'w' or 'a' to write or append to the file to be written
        min_votes1: int, determines the number of upvotes, for a word to be 
                included in the thesaurus (see powerthesaurus.com)
        related: NOT OPERATIONAL plans to include an additional category 
                of word entries which exist on the website, however they
                are much more sparse.
                
    """
    #coloc, rev_dc, dc, count = collocation(voc_sz=voc_sz1, appb=True)
    
#    tr = open(CDNM, 'r',encoding=ENC)  # targets
#    targets = tr.read().split('\n')
#    tr.close()

    missed = []
    
    if len(model.keys())== 0:
        missed.extend(targets)
    else:
        dc=model.get(2,0)
        common = [dc.get(i, 0) for i in targets]
        for i in range(len(common)):
            if common[i] == 0:
                missed.append(targets[i])
    to_look_up = []
    root_syns = []
    branch_syns = []
    for word in missed:
        newwords = scrape_power_thes(word, pass_on_words=True, write_here=False, min_upvotes=min_votes1)
        to_look_up.extend(newwords)
        root_syns.append(newwords)
    for word in to_look_up:
        newwords = scrape_power_thes(word, pass_on_words=True, write_here=False, min_upvotes=min_votes1)
        branch_syns.append(newwords)
    apx = open(THES+'/'+filena, mode, encoding=ENC)
    # apx.write(filena+'\n')
    for i in range(len(missed)):
        apx.write(missed[i] + '|1\n')
        apx.write('|'.join(root_syns[i]) + '\n')
    for i in range(len(to_look_up)):
        apx.write(to_look_up[i] + '|1\n')
        apx.write('|'.join(branch_syns[i]) + '\n')
    apx.close()
    print("Found %i words for appendix" % (len(missed) + len(to_look_up)))

def build_wiktionary(targets,iterations=1,out='wiktionary_thes01.txt'):
    """Builds a new ontologically associative thesaurus, pulling words from
    partially context sensitive parts of wiktionary pages.
    Usage:
        targets: list of strings, indicating codenames, or other words.
                These become to focus of the new thesaurus.
        iterations: int, 1 justs scrapes the targets, 2 scrapes the words 
                returned by the 1st iteration of scraping as well. Higher
                numbers haven't been tested.
        out: str, output file name 
    Generates:
        output file in /data/thesauri, log file in /logs
    
    need:
        condition when missing capitalization is not indicated by  
        default page-- leading to a retry with capitalized(word)
    """
    wiktionary={}
    opt=1
    #timer=[]
    misses=[out]
    #targetlist=targets
    for i in range(iterations):
        new_targets=[]
        for target in targets:
            try:
                temp=scrape_wiktionary(target,require_success=opt)
            except:
                temp=[]
            temp1 = list(map(lambda a: a.replace(' (page does not exist)',''),temp))
            temp2 = list(map(lambda a: a.replace('w:',''),temp1))
            if len(temp2)>0:
                wiktionary[target]=temp2
                print("got words for %s"%target)
            else:
                print("no words for %s"%target)
                misses.append(target)
            time.sleep(1+2*np.random.random())
            if len(wiktionary.keys())%100==0:
                #timer tracking here?
                pass
        opt=0
        for value in wiktionary.values():
            new_targets.extend(value)
        targets=new_targets
    h=open(LOCAL+'logs\wiki_misses.csv','w',encoding=ENC) 
    h.write('\n'.join(misses))
    h.close()
    dict_to_thes(wiktionary,THES+'/'+out)

    
def dict_to_thes(inp,out):
     file=open(out,'w',encoding=ENC)
     for key,value in inp.items():
         file.write(key.lower() + '|1\n')
         try:
             file.write('|'.join(value).lower() + '\n')
         except UnicodeEncodeError:
             temp=open(LOCAL+'\temp.txt','w',encoding='UTF-8')
             for item_n in range(len(value)):
                 try:
                     temp.write(value[item_n])
                 except UnicodeEncodeError:
                     value.pop(item_n)
             file.write('|'.join(value).lower() + '\n')
                     
     file.close()

def scrape_wiktionary(word,require_success=0):
    """
    """
    wiki='https://en.wiktionary.org/wiki/'
    root='https://en.wiktionary.org'
    h2='//body/div[@id="content"]/div[@id="bodyContent"]/div[@id="mw-content-text"]/div/h2'
    ol='//body/div[@id="content"]/div[@id="bodyContent"]/div[@id="mw-content-text"]/div/ol'
    seeother='//body/div[@id="content"]/div[@id="bodyContent"]/div[@id="mw-content-text"]/div/div/b/a'
    def find_correct_lang(tree):
        indicies=[]
        
        return indicies
    def follow_breadcrumbs(pocket):
        "look at this! functional programming!"
        more_words=[]
        breadcrumbs=pocket.xpath('span/i/a')[0].attrib#*******
        entry_words.append(breadcrumbs['title'])
        page2 = requests.get(root+breadcrumbs['href'])
        tree= html.fromstring(page2.content)
        olist=tree.xpath(ol)
        languages=tree.xpath(h2+'/span/text()')
        lang_entry=olist[languages.index('English')]
        bullets=lang_entry.xpath('li')
        if len(bullets)>1 or len(bullets[0].getchildren())>1:#if this is one, maybe do something special
            for bullet in bullets:
                temp = bullet.xpath('a')
                for a in temp:
                    more_words.append(a.attrib['title'])
        return more_words

    def gather_scraps(fridge):
        more_words=[]
        scraps = fridge.xpath('text()')
        for scrap in scraps:
            more_words.extend(list(filter(lambda x: len(x)>2,linewise_filter(scrap,rem_and=1,lower=0))))
        shelf = fridge.getchildren()
        while len(shelf)>0:
            new_shelf=[] 
            for item in shelf:
                lines=item.xpath('text()')
                for line in lines:
                    more_words.extend(list(filter(lambda x: len(x)>2,linewise_filter(line,rem_and=1,lower=0))))
                new_shelf.extend(item.getchildren())
            shelf=new_shelf
        return more_words
    word2=word.replace(' ','_')
    try:
        page = requests.get(wiki+word2,timeout=2)
    except:
        time.sleep(2+np.random.random())
        page = requests.get(wiki+word2,timeout=5)
        
    tree= html.fromstring(page.content)
    languages=tree.xpath(h2+'/span/text()')
    entry_words=[]
    if 'English' in languages:
        #read the stuff on the page
        olist=tree.xpath(ol)
        lang_entry=olist[languages.index('English')]
        bullets=lang_entry.xpath('li')
        if len(bullets)>1 or len(bullets[0].getchildren())>1:#if this is one, maybe do something special
            for bullet in bullets:
                temp = bullet.xpath('a')
                for a in temp:
                    entry_words.append(a.attrib['title'])
        else:
            bullet_content = bullets[0].getchildren()
            if len(bullet_content[0].xpath('span/i/a'))>0:
                entry_words.extend(follow_breadcrumbs(bullet_content[0]))
            else:#strategy 2
                new_words=gather_scraps(bullets[0])
                if len(new_words)==0:
                    if require_success==1:
                        raise IOError("no existing strategies worked for %s"%word)
                else:
                    entry_words.extend(new_words)
    else:
        #read list of "see also" pages
        pages=[]
        seealso=tree.xpath(seeother)
        for i in seealso:
            pages.append(i.attrib['href'])
            for page1 in pages:
                page = requests.get(root+page1)
                tree= html.fromstring(page.content)
                languages=tree.xpath(h2+'/span/text()')
                if 'English' in languages:
                    break
            olist=tree.xpath(ol)
            lang_entry=olist[languages.index('English')]
            bullets=lang_entry.xpath('li')
            if len(bullets)>1 or len(bullets[0].getchildren())>1:#if this is one, maybe do something special
                for bullet in bullets:
                    temp = bullet.xpath('a')
                    for a in temp:
                        entry_words.append(a.attrib['title'])
            else:
                bullet_content = bullets[0].getchildren()
                if len(bullet_content[0].xpath('span/i/a'))>0:
                    entry_words.extend(follow_breadcrumbs(bullet_content[0]))
                else:#strategy 2
                    new_words=gather_scraps(bullets[0])
                    if len(new_words)==0:
                        if require_success==1:
                            raise IOError("no existing strategies worked for %s"%word)
                    else:
                        entry_words.extend(new_words)
    return entry_words


def scrape_power_thes(word, filen="appendix01.txt", min_upvotes=5, 
                      pass_on_words=False, write_here=True, rel=False):
    """ go to power thesaurus website,
    scrape appropriate words from page (max 100 using cookies)
    options:

        write_here (True) function will add entry to doc at filename. for large batches of words,
                            more efficient is to pass up newwords and append file once
        pass_on_words (False)  gives return newwords for batch processing and tracking
    """
    import requests
    from lxml import html
    # xml paths
    jar = requests.cookies.RequestsCookieJar()
    jar.set('settings', '00400', domain='www.powerthesaurus.org', path='/')
    path1 = '//body/div[@class="container"]/div[@id="content"]/div[@id="main_side_container"]/div[@id="main"]/div[@id="topiccontent"]/div[@id="abb"]'
    table1 = '/table'  # /tbody/tr
    # begin operations
    pt = "https://www.powerthesaurus.org/"
    # additional pages are found pt + leaf + /synonyms/2 (or 3, etc.)
    leaf = word.replace(' ', '_')
    pagen = 1
    if rel == True:
        ext = '/related'
    else:
        ext = ''
    exitc = 0
    # print('debug')
    while exitc == 0:
        if pagen > 1:
            ext = "/synonyms/%i" % pagen
        rtry = 0
        while rtry < 12:
            try:
                rtry += 1
                page = requests.get(pt + leaf + ext, timeout=1, cookies=jar)
                print("scraping...%s/%i" % (word, pagen))
                if rtry > 0:
                    time.sleep(5 * rtry + 4 * random.random())
                tree = html.fromstring(page.content)
                entries = tree.xpath(path1 + table1)[0].getchildren()
                break
            except:
                print("didn't load")
        if rtry >= 12:
            exitc = 1
            entries = []

            # raise IOError("server is not cooperating")
        newwords = []
        pagen += 1
        if len(entries) < 200:
            exitc = 1
        for entry in entries:
            v, w = entry.xpath('td')
            if int(v.xpath('div/div[@class="rating"]/text()')[0]) < min_upvotes:
                exitc = 1
                # print(word)
                break
            newwords.append(w.xpath('a/text()')[0])
    if len(newwords) == 0:
        newwords.append(word)
        # print('plus')
        # return exitc

    # append will start at end of existing line, not auto newline! (duh)
    # for this version, appendix will be written in the style of the open office
    # thesaurus, using pipes, though word sense disambiguation will not be performed
    # and no part of speech specification will be included.
    # if it seems useful, perhaps develop these as options in this function
    # example:
    # beach|1
    # shore|seaside|coast|strand|bank|seashore|seaboard|ground|coastline|littoral|seacoast|foreshore|shoreline
    if write_here == True:
        apx = open(LOCAL+'/'+filen, 'a', encoding=ENC)
        apx.write(word + '|1\n')
        apx.write('|'.join(newwords) + '\n')
        apx.close()
    if pass_on_words == True:
        return newwords        
   
def prep_raw(inp, out, remove_and=1,dev=0,enc=ENC):
    """Usage:
        inp: str, input file absolute path (guide: *.txt in /data/raw)
        out: str, output file absolute path (guide: *prep.txt in /data/raw)
        remove_and: int, 1 to remove the word 'and' or 0 to keep it
        dev: int, number of lines to process, 0 to process full file
        enc: str, type of encoding used for raw data input file.
    
    the database is sentences, each separated by .\n
    preprocessing steps:
    replace '-' with ' '
    remove additional punctuation
    replace multiple spaces with a single space
    ??? should punctuation start a new line???
    this could be done easily at this stage. later, maybe
    """
    ip = open(inp, 'r', encoding=enc)
    ot = open(out, 'w', encoding=ENC)
    # for i in range(5000): #500 is the number of sentences to use during development
    lines = 0
    for line in ip:  # use this once done with dev
        lines += 1
        linel=linewise_filter(line,rem_and=remove_and)
        temp = ' '.join(linel)
        ot.write(temp+'\n')
        if dev > 0  and lines > dev:
            break
    ip.close()
    ot.close()
    
def linewise_filter(line,rem_and=1,lower=1):
    """
    """
    line = line.replace('\n','')
    line = line.replace('-', ' ')
    line = line.replace('“', '')
    line = line.replace('”', '')
    line = line.replace('•', '')
    line = line.replace('—', '')

    line = line.translate(str.maketrans({key: None for key in string.punctuation or string.digits}))
    if rem_and==1:
        line = line.replace(' and ',' ')
    if lower == 1:
        
        linel = line.lower().split(' ')
    else:
        linel = line.split(' ')
    linel = list(filter(lambda x: not x == '', linel))
    return linel

def prepped_to_colloc(seedlist, nldata='news2011procd_dev', iterations=2,
                      thesname="collocationthesaurus001.txt", nlevels=50, 
                      mincut=3,devmode=1):
    """take natural language passages, and isolate the most common ordered collocations
(as if they are tuples). Using the lead word as a label, establish a new thesaurus
that contains the most common collocations for every word in a target list.
the target list is updated to include the collocated words in the next iteration,
where the seedlist is the target list for the inital search.
targs1=wvc.prepped_to_colloc(targets, dictionary, reverse_dictionary, nldata='news2011procd',thesname='2011newsthes3.txt', iterations=2, nlevels=60, mincut=10)
needs: dictionary, reverse_dictionary

seedlist-- list of strings
devmode -- int (1 or 2) tries to optimize enty methods, in addition to leading to more insightful 
compression rules
iterations -- int, number of times to expand on findings from initial seed.
thesname -- string, what to name the thesaurus written to hold the findings.
"""
    # current plan
    # peek at top 50 lines of data in natural language corpus file
    # figure out necessary preprocessing. DO THIS IN SEPARATE func
    # call prepped raw data instead, since the proc is iterative
    # figure out a sneaky way to gather the info without mass translation
    # or expensive searching...
    # iterate the above
    # eventually, copy thesaurus formatting and writing from another func in
    # this module
    # test on smaller data set
    # use testing to establish useful threshholds.
    # seedlist

    targetlist = seedlist
    bigrams = {}
    #bigrams = {}
    targs = {}
    
    for i in range(iterations):
        bigrams=compress_to_targets(targetlist,RAW+'/'+nldata,bigrams)
        if devmode==1:
            targs,targetlist=targetlist_update(bigrams,targs,mincut)
        elif devmode==2:
            targs,targetlist=targetlist_update2(bigrams,targs,nlevels)
        ###### iteration reloads and rereads for new targets####
    ak = open(THES+'/'+thesname, 'w', encoding=ENC)
    for i in targs.keys():
        tempprob = []
        tempwords = []
        for i2 in targs[i]:
            tempprob.append(i2[0])
            tempwords.append(i2[1])
        odds = np.divide(tempprob, sum(tempprob))
        
        m = np.max(odds)
        n = nlevels
        wnum= list(map(lambda a: int(np.floor(a)),np.multiply(odds,(n+1.)/m)))
        #lvls = np.linspace(m * n / (n + 1), m / (n + 1), num=n)
        
        leveling=[[] for i5 in range(max(wnum))]
        for i3 in range(len(wnum)):
            if wnum[i3]==0:
                continue
            else:
                wd = tempwords[i3]
                if not len(wd) == 0:
                    leveling[wnum[i3]-1].append(wd)
        for i4 in range(1,max(wnum)+1):
            if not len(leveling[i4-1]) == 0:
                    ak.write(i + '|%i\n'%i4)
                    ak.write('|'.join(leveling[i4-1]) + '\n')
    ak.close()
    # leveling of associations is done linearly. although the data trends indicate
    # an exponential distribution of odds, the thesaurus building routine should
    # maintain the occurrence likelihoods for later odds ratio decision making.
    # the normalization performed here is relevant to the process of choosing word
    # specific clues.

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
    
def compress_to_targets(targetlist,data,bigrams):
    """called by prepped_to_colloc and is the bottleneck, at the moment
    let's sub functionalize this and use a profiler to speed up the slow bits
    
    """

    sp = list(filter(lambda x: x.find(' ') > 0, targetlist))
    spw = []
    tls=set(targetlist)
    for isp in sp:
        spw.extend(isp.split(' '))
    tlsw=set(spw)
    def add_bigram(temp,set):
        for i in set:
            lt=[temp.index(i)]
            for i3 in range(temp.count(i)-1):
                lt.append(temp.index(i,lt[len(lt)-1]))
            for i2 in [temp[ii] for ii in lt]:
                if i2 in tls:
                # get prev and next
                # save bigrams as numbers? sparseness precludes array or indicial storage
    
                    if temp.index(i2) == 0:
                        a = 0
                    else:
                        a = temp[temp.index(i2) - 1]
                    b = i2
                    if len(temp) - temp.index(i2) == 1:
                        c = 0
                    else:
                        c = temp[temp.index(i2) + 1]
    #                if hits.get(b, 0) == 0:
    #                    hits[b] = []
                    if not a == 0:
                        if not len(temp[temp.index(i2) - 1]) < 3:
                            # we are not interested in clues shorter than 3 letters long
                            #ab = '%i %i' % (a, b)
                            if b in bigrams.keys():
                                if a in bigrams[b].keys():
                                    bigrams[b][a][0] += 1
                                else:
                                    bigrams[b][a] = [1,0]
                            else:
                                bigrams[b] = {a:[1,0]}
    #                            hits[b].append(a)
                    if not c == 0:
                        if not len(temp[temp.index(i2) + 1]) < 3:
                            #bc = '%i %i' % (b, c)
                            if b in bigrams.keys():
                                if c in bigrams[b].keys():
                                    bigrams[b][c][1] += 1
                                else:
                                    bigrams[b][c] = [0,1]
                            else:
                                bigrams[b] = {c:[0,1]}
    #                            hits[b].append(c)
                elif i2 in tlsw:
                    mod = spw.index(i2) % 2
                    full = sp[spw.index(i2) // 2]
                    if min(len(temp) - temp.index(i2) - 2 + mod, temp.index(i2) - mod) > -1:
                        if temp[temp.index(i2) + 1 - 2 * mod] == spw[2 * (spw.index(i2) // 2) + 1 - mod]:
                            if temp.index(i2) == mod:
                                a = 0
                            else:
                                a = temp[temp.index(i2) - 1 - mod]
                            b = full
                            if len(temp) - temp.index(i2) == 2 - mod:
                                c = 0
                            else:
                                c = temp[temp.index(i2) + 2 - mod]
    #                        if hits.get(b, 0) == 0:
    #                            hits[b] = []
                            if not a == 0:
                                if not len(temp[temp.index(i2) - 1 - mod]) < 3:
                                    # we are not interested in clues shorter than 3 letters long
                                    #ab = '%i %i' % (a, b)
                                    if b in bigrams.keys():
                                        if a in bigrams[b].keys():
                                            bigrams[b][a][0] += 1
                                        else:
                                            bigrams[b][a] = [1,0]
                                    else:
                                        bigrams[b] = {a:[1,0]}
    #                                    hits[b].append(a)
                            if not c == 0:
                                if not len(temp[temp.index(i2) + 2 - mod]) < 3:
                                    #bc = '%i %i' % (b, c)
                                    if b in bigrams.keys():
                                        if c in bigrams[b].keys():
                                            bigrams[b][c][1] += 1
                                        else:
                                            bigrams[b][c] = [0,1]
                                    else:
                                        bigrams[b] = {c:[0,1]}
#                                    hits[b].append(c)
    # any codenames with spaces? clues can't contain spaces, so no need for support
    # beyond first iteration
    d = open(data, 'r', encoding=ENC)
    for line in d:
        temp = line.replace('\n', '').split(' ')
        ts=set(temp)
        if len(ts & tls)>0 or len(ts & tlsw)>1:
            add_bigram(temp,ts & (tls | tlsw))
    
    
    return bigrams

def targetlist_update(bigrams,targs,mincut):
    bg3 = {}
    #    bigs=[]
    #    nums=[]
    targetlist = []
    for i2 in bigrams.keys():
        bg3[i2]={}
        for i3 in bigrams[i2].keys():
            if max(bigrams[i2][i3]) > mincut:
                bg3[i2][i3] = bigrams[i2][i3]
    for i2 in bg3.keys():
        #        m=dc.get(i,0)
        #        if not m == 0:
        tl = []
        for i3 in bg3[i2]:  # get the number of times better collocation is found
            temp = max(bg3.get(i2,0).get(i3,0))
            if not temp == 0:
                tl.append((temp, i3))
                if not i3 in bg3.keys():
                    targetlist.append(i3)
        tl.sort(key=lambda x: x[0], reverse=True)
        if not len(tl) == 0:
            targs[i2] = tl
    return targs,targetlist
def targetlist_update2(bigrams,targs,nlevels):
    bg3 = {}
    #    bigs=[]
    #    nums=[]
    targetlist = []
    for i2 in bigrams.keys():
        bg3[i2]={}
        mincut= max([item for sublist in list(bigrams[i2].values()) for item in sublist])//(nlevels+1)
        for i3 in bigrams[i2].keys():
            if max(bigrams[i2][i3]) > mincut:
                bg3[i2][i3] = bigrams[i2][i3]
    for i2 in bg3.keys():
        #        m=dc.get(i,0)
        #        if not m == 0:
        tl = []
        for i3 in bg3[i2]:  # get the number of times better collocation is found
            temp = max(bg3.get(i2,0).get(i3,0))
            if not temp == 0:
                tl.append((temp, i3))
                if not i3 in bg3.keys():
                    targetlist.append(i3)
        tl.sort(key=lambda x: x[0], reverse=True)
        if not len(tl) == 0:
            targs[i2] = tl
    return targs,targetlist