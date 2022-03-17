# forked and adapted from https://github.com/poldrack/william_james
# code updated to python 3 requirements

from cognitiveatlas.api import get_concept
from nltk.corpus import stopwords
from nltk.stem.porter import *
from nltk.stem import *
import pandas
import numpy
import json
import nltk
import re

root = "/Users/carlos/documents/GitHub/sepex_ontology/"

paragraphs = json.load(open(root + "wj/william_james.json","r"))

# Get all cognitive atlas concepts
all_concepts = get_concept().json
concepts = dict()
for concept in all_concepts:
    concepts[concept["id"]] = str(concept["name"])

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


# Prepare feature data frame
features = pandas.DataFrame(columns=concepts.values())

count = 1
for pid,paragraph in paragraphs.items():
    if len(paragraph) > 0:
        words = processText(paragraph)
        text = " ".join(words)
        print("Parsing paragraph %s, %s of %s" %(pid,count,len(paragraphs)))
        # search for each cognitive atlas term, take a count
        for concept in features.columns:
            processed_concept = " ".join(processText(str(concept)))
            features.loc[pid,concept] = len(re.findall(processed_concept,text))
        print("Found %s total occurrences for %s" %(features.loc[pid].sum(),pid))
        count +=1
    else:
        print("No text found for paragraph %s" %(pid))
        features.loc[pid] = numpy.zeros(len(concepts))

# Save to file
out_dir = root_dir + "data/"
features.to_csv(out_dir + "cogat_features.tsv",sep="\t")
