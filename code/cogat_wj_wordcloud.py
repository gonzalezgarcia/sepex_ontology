#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 21 11:14:57 2021

@author: carlos
"""
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt


# get data directory (using getcwd() is needed to support running example in generated IPython notebook)
root = "/Users/carlos/documents/GitHub/sepex_ontology/"

# Read the whole text.
df = pd.read_csv(root + 'data/cogat_features.tsv',sep='\t')
df = df.drop('Unnamed: 0', 1) # clean up

prevalence = df.sum()

# remove rows with zeros (concepts that don't appear in WJ)
prevalence_any = prevalence.loc[~(prevalence==0)]

# compute overlap between cognitive atlas and william james
overlap = len(prevalence_any) / len(prevalence)

print("Overlap between CogAtlas and WJ's principles: " + (str(overlap)))


word_list = prevalence_any.index

text = str(' ')

for idx,word in enumerate(word_list):
    word = word + ' '
    text += word * int(prevalence_any[idx])
    #print(word, prevalence_any[idx])


wordcloud = WordCloud(background_color="white",
                      collocations=False).generate(text)

# Display the generated image:
# the matplotlib way:
plt.figure(figsize=(4,4), dpi=1200)
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis("off")
plt.savefig(root +'figures/cogat_wj_cloud.png')
