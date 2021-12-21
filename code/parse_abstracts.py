# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
# Import stuff
import os
import sys
import numpy as np
import re
import matplotlib.pyplot as plt
from nltk.corpus import stopwords
from nltk.stem.porter import *
from nltk.stem import *
import pandas
import json
import nltk
import pdfplumber
from wordcloud import WordCloud, STOPWORDS

# Where are we?
os.chdir(os.path.dirname(sys.argv[0]))

###### Poldrack's functions
# Functions to parse text
def remove_nonenglish_chars(text):
    return re.sub("[^a-zA-Z]", " ", text)
    
def text2sentences(text,remove_non_english_chars=True):
    tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')    
    if remove_non_english_chars:
        text = remove_nonenglish_chars(text)
    for s in tokenizer.tokenize(text):
        yield s

def processText(text):
    '''combines text2sentences and sentence2words'''
    vector = []
    for line in text2sentences(text):            
        words = sentence2words(line)
        vector = vector + words
    return vector

def sentence2words(sentence,remove_stop_words=True,lower=True):
    if isinstance(sentence,list): sentence = sentence[0]
    re_white_space = re.compile("\s+")
    stop_words = set(stopwords.words("english"))
    if lower: sentence = sentence.lower()
    words = re_white_space.split(sentence.strip())
    if remove_stop_words:
        words = [w for w in words if w not in stop_words]
    return words

def do_stem(words,return_unique=False,remove_non_english_words=True):
    '''do_stem
    Parameters
    ==========    
    words: str/list
        one or more words to be stemmed
    return_unique: boolean (default True)
        return unique terms
    '''
    stemmer = PorterStemmer()
    if isinstance(words,str):
        words = [words]
    stems = []
    for word in words:
        if remove_non_english_words:
            word = re.sub("[^a-zA-Z]", " ", word)
        stems.append(stemmer.stem(word))
    if return_unique:
        return numpy.unique([s.lower() for s in stems]).tolist()
    else:
        return stems

######
# Remove unwanted words
def remove_irrelevant_words(text):
    irrelevant_list = list(("abstracts", "sepex", "sepneca", "congreso"))
    for i, val in enumerate(irrelevant_list):
        text = re.sub(val, "", text)
    return text


# Function to read in pdf page by page
def read_abstracts(year):
    pdf = pdfplumber.open(('../abstracts/sepex_' +  str(year) + '.pdf'))
    page = pdf.pages[3]
    words = processText(page.extract_text())
    text = " ".join(words)
    text = remove_irrelevant_words(text)
    return text
    
words = read_abstracts(2014)

print(words)
#wordcloud = WordCloud(width = 800, height = 800,
                background_color ='white',
                stopwords = stopwords,
                min_font_size = 10).generate(words)
 
# plot the WordCloud image                      
#plt.figure(figsize = (8, 8), facecolor = None)
#plt.imshow(wordcloud)
#plt.axis("off")
#plt.tight_layout(pad = 0)
 
#plt.show()