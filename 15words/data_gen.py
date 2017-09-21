# -*- coding: utf-8 -*-
"""
Created on Tue Sep 19 15:48:21 2017
Input data for Codenames very small vocabulary
separately stored values for key word, key number, word group, and up group(lbl)
let's have seperate sets of observations for different people

starting vocab~15 words?

@author: Aaron
"""
Dictionary=["apple","cook","star","ocean","tool","shower","year","anchor","north"
            ,"mouse","song","house","diamond","orange","steam"]


import os
import subprocess
LOCAL_REPO=os.getcwd()
#LOCAL_REPO="C:\Users\Aaron\Documents\GitHub\Game_AI"

def new_human_player_entry():
    """Starts session to gather data from human user
    Asks for: 
        name -- the name of the human/data dict will be stored under
        
    shows a key word and presents the remaining words in the dictionary
    one by one, user selects the most related word, which removes it from those 
    displayed. this repeats until all the words are ranked in relation to the 
    key word. this process is performed for every word in the dictionary
    
    if the vocab is 15 words, the user is asked to return 15*13 = 195 answers
    """
    h=open('indicies.txt','w')
    gui=subprocess.Popen("python GUI.py",stdout=h)
    gui.wait()
    h.close()
    h2=open('indicies.txt','r')
    strindicies=""
    for line in h2:
        strindicies=strindicies+line
    strindicies=strindicies.replace('{','')
    strindicies=strindicies.replace(']}\n','')
    strlist=strindicies.split('], ')
    ind={}
    for i in range(len(strlist)):
        strlist[i]=strlist[i].split(': [')
        strlist[i][1]=strlist[i][1].split(', ')
        ind[int(strlist[i][0])]=[int(i2)for i2 in strlist[i][1]]
    n=len(ind)#number of words is n
    

def create_obs_from_human_entry(name,size):
    """Generates a set of answers for combinations of key words and numbers,
    based off of a human-ranking-tensor 
    
    """
    pass