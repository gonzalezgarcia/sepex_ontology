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
import stanza 
#stanza.download('es') 
nlp = stanza.Pipeline(lang='es')
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
    for line in text2sentences(text, remove_non_english_chars = False):            
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
    irrelevant_list = list(("abstracts", "sepex", "sepneca", "congreso", "poster", "july", "word", "ac", "uk",
                            "participants", "participant", "university", "result", "results", "showed", "whether",
                            "experiments", "task", "effect", "group", "different", "condition", "s", "experiment",
                            "2013", "2014", "2015", "2016", "2017", "2018", "using", "one", "study", "difference",
                            "1", "2", "3", "4", "5", "6", "7", "8", "9"))
    for i, val in enumerate(irrelevant_list):
        text = re.sub(val, "", text)
    return text

def central_words(text):
    doc = nlp(text) 
    central_words = list()
    for sent in doc.sentences: 
        for tok in sent.tokens: 
            for word in tok.words:
                if word.upos == 'NOUN': 
                    central_words.append(word.text)
    return central_words

# Function to read in pdf page by page
def read_abstracts(year):
    pdf = pdfplumber.open(('../abstracts/sepex_' +  str(year) + '.pdf'))
    text = list() 
    #print("Parsing paragraph %s, %s of %s" %(pid,count,len(paragraphs)))
    for i, page in enumerate(pdf.pages):
        print("Reading page %s out of %s" %(i, len(pdf.pages)))
        words = processText(page.extract_text())
        page_text = " ".join(words)
        # page_text = remove_irrelevant_words(page_text)
        # Use NLP to locate relevant words
        #page_text = central_words(page_text)
        temp = central_words(page_text)
        text = text + temp
        
    # Concatenate pages
    text = " ".join(text)
    return text

# Read in abstracts
words = read_abstracts(2016)

words = remove_irrelevant_words(words)
# Create word cloud
wordcloud = WordCloud().generate(words)

#plot the WordCloud image                      
plt.figure(figsize = (8, 8), facecolor = None)
plt.imshow(wordcloud)
plt.axis("off")
plt.tight_layout(pad = 0)
 
plt.show()
