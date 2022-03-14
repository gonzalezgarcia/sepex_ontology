# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
# Import stuff
import os
import sys
# import numpy as np
import re
# import matplotlib.pyplot as plt
from nltk.corpus import stopwords
# from nltk.stem.porter import *
# from nltk.stem import *
import pandas
# import json
import nltk
import pdfplumber
from wordcloud import WordCloud, STOPWORDS
# import pandas as pd
from cognitiveatlas.api import get_concept
from googletrans import Translator
translator = Translator()
import matplotlib.pyplot as plt
import numpy as np

# Where are we?
# try:
#     os.chdir(os.path.dirname(sys.argv[0])) # not working for me (carlos)
# except:
    
root = "/home/javier/git_repos/sepex_ontology/"
root = "/Users/carlos/Documents/GitHub/sepex_ontology/"
    
###### Poldrack's functions
# Functions to parse text
def remove_nonenglish_chars(text):
    return re.sub("[^a-zA-Z]ñ", " ", text)
    
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

def en2es(input_text):
    temp = translator.translate(text = input_text, src = 'es', dest = 'en')
    return temp.text

# def do_stem(words,return_unique=False,remove_non_english_words=True):
#     '''do_stem
#     Parameters
#     ==========    
#     words: str/list
#         one or more words to be stemmed
#     return_unique: boolean (default True)
#         return unique terms
#     '''
#     stemmer = PorterStemmer()
#     if isinstance(words,str):
#         words = [words]
#     stems = []
#     for word in words:
#         if remove_non_english_words:
#             word = re.sub("[^a-zA-Z]", " ", word)
#         stems.append(stemmer.stem(word))
#     if return_unique:
#         return numpy.unique([s.lower() for s in stems]).tolist()
#     else:
#         return stems

######
# Remove unwanted words
# def remove_irrelevant_words(text):
#     irrelevant_list = list(("abstracts", "sepex", "sepneca", "congreso"))
#     for i, val in enumerate(irrelevant_list):
#         text = re.sub(val, "", text)
#     return text


# Function to read in pdf page by page
def read_abstracts(year):
    pdf = pdfplumber.open(('../abstracts/sepex_' +  str(year) + '.pdf'))
    text = list() 
    #print("Parsing paragraph %s, %s of %s" %(pid,count,len(paragraphs)))
    for i, page in enumerate(pdf.pages):
        # print("Reading page %s out of %s" %(i, len(pdf.pages)))
        words = processText(page.extract_text())
        page_text = " ".join(words)
        #page_text = remove_irrelevant_words(page_text)
        
        # Translate into English
        #page_text = en2es(page_text)
        text.append(page_text)
        
    # Concatenate pages
    text = " ".join(text)
    return text


# Prepare feature data frame
def search_cogat(input_text):
    # Get all cognitive atlas concepts
    all_concepts = get_concept().json
    concepts = dict()
    for concept in all_concepts:
        concepts[concept["id"]] = str(concept["name"])
    features = pandas.DataFrame(columns=concepts.values())
    # search for each cognitive atlas term, take a count
    for concept in features.columns:
        processed_concept = " ".join(processText(str(concept)))
        features.loc[0,concept] = len(re.findall(processed_concept,input_text))
    #print("Found %s total occurrences for %s" %(features.loc[pid].sum(),pid))            
    return features.T

def search_lexicon(input_text,lexicon):
    lex_txt = open("../data/" + lexicon + ".txt", "r").readlines()
    lex_txt = [x[:-1] for x in lex_txt] # remove blank space \n
    features = pandas.DataFrame(columns=lex_txt)
    # search for each dsm term, take a count
    for concept in features.columns:
        processed_concept = " ".join(processText(str(concept)))
        features.loc[0,concept] = len(re.findall(processed_concept,input_text))
    #print("Found %s total occurrences for %s" %(features.loc[pid].sum(),pid))            
    return features.T

# Word clouds
# I'm turning this into a function so we can easily plug it for each lexicon
def draw_wordclod(prevalence_data, fig_name):
    
    '''draw_wordclod
    Input
    ==========    
    prevalence_data: dataframe with words as 'index' (row names) and and 
    prevalence values in the first column
    fig_name: name of the resulting figure
    
    Output
    ==========    
    displays and prints figure
    
    '''
    
    x, y = np.ogrid[:1600, :1600]
    
    mask = (x - 800) ** 2 + (y - 800) ** 2 > 800 ** 2
    mask = 255 * mask.astype(int)
    # extract words
    prevalence_data["count"] = prevalence_data[0]
    prevalence_data["word"] = prevalence_data.index

    data = dict(zip(prevalence_data['word'].tolist(), prevalence_data['count'].tolist()))
    
    # create the wordcloud
    wordcloud = WordCloud(background_color="white",
                          width=1600,
                          height=1600, mask=mask).generate_from_frequencies(data)

    # Display the generated image:
    # the matplotlib way:
    plt.figure(figsize=(20,20), dpi=300)
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.tight_layout(pad=0)
    plt.axis("off")
    plt.savefig(root + 'figures/' + fig_name + '.png', bbox_inches='tight')


    
