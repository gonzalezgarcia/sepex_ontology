#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 21 11:14:57 2021

@author: carlos
"""
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from parse_abstracts import *
import seaborn as sns
import numpy as np

# get data directory (using getcwd() is needed to support running example in generated IPython notebook)
root = "/home/javier/git_repos/sepex_ontology/"
root = "/Users/carlos/documents/GitHub/sepex_ontology/"


# Get concepts that overlap between WJ and cogat
df = pd.read_csv(root + 'data/cogat_features.tsv',sep='\t')
df = df.drop('Unnamed: 0', 1) # clean up
prevalence = df.sum()
prevalence_any = prevalence.loc[~(prevalence==0)]

# compute overlap between cognitive atlas and william james
overlap = len(prevalence_any) / len(prevalence)
print("Overlap between CogAtlas and WJ's principles: " + (str(overlap)))

# get all words that appear in WJ
word_list = prevalence_any.index



# compute proportion of sepex-cogat words that are shared with WJ-cogat

sepex_editions = [2012,2014,2016,2018]
lexicons = ["concepts"]

overlap = pd.DataFrame(columns=lexicons)

for idx,sepex_year in enumerate(sepex_editions):

    # Read in abstracts
    print('Reading abstracts ' + str(sepex_year))
    lexicons_length = [] # to compute weighted overlap
    abstracts = read_abstracts(sepex_year)
    # SEARCH IN COGNITIVE ATLAS sub-LEXICONS
    cogat_prevalence = search_lexicon(abstracts,"cognitive-atlas_concepts") # get prevalence of cogat concepts in sepex abstracts
    cogat_prevalence_any = cogat_prevalence[cogat_prevalence[0] != 0]

    word_list_sepex = cogat_prevalence_any.index
    
    intersection = set(word_list) & set(word_list_sepex)

    overlap.loc[idx,"concepts"] = (len(intersection) / len(word_list_sepex)) * 100


# plot overlap between WJ and sepex

sns.set_style("white")
sns.set_context("poster",font_scale=1.5,rc={"figure.figsize":(20, 20)})
g = sns.lineplot(data=overlap)
g.set_xticks(range(len(sepex_editions))) # <--- set the ticks first
g.set_xticklabels(sepex_editions)
g.set_ylabel("overlap (%)")
g.set_ylabel("overlap (%)")
g.set_ylim(0,100)
g.get_legend().remove()
g.figure.savefig(root + 'figures_nospanish/wj_sepex_overlap.png',dpi=600,bbox_inches="tight")

## plot intersection and not intersection word clouds (for SEPEX 2018)

# find words shared and unique
intersection = list(set(word_list) & set(word_list_sepex))
sepex_remainder = set(word_list_sepex) - set(word_list)
wj_remainder = set(word_list) - set(word_list_sepex)

# filter previous series to get at frequency for shared and unique

shared = cogat_prevalence_any[cogat_prevalence_any.index.isin(intersection)]

unique = cogat_prevalence_any[cogat_prevalence_any.index.isin(sepex_remainder)]

draw_wordclod(shared, 'sepex18_shared_WJ_cloud')
draw_wordclod(unique, 'sepex18_unique_WJ_cloud')

# extract words
word_list = prevalence_data.index

unique["count"] = unique[0]
unique["word"] = unique.index

data = dict(zip(unique['word'].tolist(), unique['count'].tolist()))

wc = WordCloud(width=800, height=400, max_words=200).generate_from_frequencies(data)

plt.figure(figsize=(10, 10))
plt.imshow(wc, interpolation='bilinear')
plt.axis('off')
plt.show()

shared["count"] = shared[0]
shared["word"] = shared.index

data = dict(zip(shared['word'].tolist(), shared['count'].tolist()))

wc = WordCloud(width=800, height=400, max_words=200).generate_from_frequencies(data)

plt.figure(figsize=(10, 10))
plt.imshow(wc, interpolation='bilinear')
plt.axis('off')
plt.show()


