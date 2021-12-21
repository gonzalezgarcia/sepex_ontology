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
import pandas as pd
from cognitiveatlas.api import get_concept


# Where are we?
#os.chdir(os.path.dirname(sys.argv[0])) # not working for me (carlos)
root = "/Users/carlos/Documents/GitHub/sepex_ontology/"
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
    irrelevant_list = list(("universidad","abstracts", "sepex", "sepneca", "congreso"))
    for i, val in enumerate(irrelevant_list):
        text = re.sub(val, "", text)
    return text


# Function to read in pdf page by page
def read_abstracts(year):
    pdf = pdfplumber.open(('../abstracts/sepex_' +  str(year) + '.pdf'))
    text = list() 
    #print("Parsing paragraph %s, %s of %s" %(pid,count,len(paragraphs)))
    for i, page in enumerate(pdf.pages):
        print("Reading page %s out of %s" %(i, len(pdf.pages)))
        words = processText(page.extract_text())
        page_text = " ".join(words)
        page_text = remove_irrelevant_words(page_text)
        text.append(page_text)
        
    # Concatenate pages
    text = " ".join(text)
    return text


# Prepare feature data frame
def search_cogat(input_text):
    features = pandas.DataFrame(columns=concepts.values())
    # search for each cognitive atlas term, take a count
    for concept in features.columns:
        processed_concept = " ".join(processText(str(concept)))
        features.loc[0,concept] = len(re.findall(processed_concept,input_text))
    #print("Found %s total occurrences for %s" %(features.loc[pid].sum(),pid))            
    return features.T



    
# Read in abstracts
abstracts = read_abstracts(2014)

# Get all cognitive atlas concepts
all_concepts = get_concept().json
concepts = dict()
for concept in all_concepts:
    concepts[concept["id"]] = str(concept["name"])
    
#get prevalence of cogat concepts in sepex 2018
prevalence = search_cogat(abstracts)
# remove rows with zeros (concepts that don't appear in WJ)
prevalence_any = prevalence[prevalence[0] != 0]

# compute overlap between cognitive atlas and william james
overlap = len(prevalence_any) / len(prevalence)

print("Overlap between CogAtlas and SEPEX 2014: " + (str(overlap)))

word_list = prevalence_any.index

text = str(' ')

for idx,word in enumerate(word_list):
    word = word + ' '
    text += word * int(prevalence_any[0][idx])
    #print(word, prevalence_any[idx])


wordcloud = WordCloud(background_color="white",
                      collocations=False).generate(text)

# Display the generated image:
# the matplotlib way:
plt.figure(figsize=(4,4), dpi=1200)
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis("off")
plt.savefig(root + 'figures/cogat_sepex14_cloud.png')