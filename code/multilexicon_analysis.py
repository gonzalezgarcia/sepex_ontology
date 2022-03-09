#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 22 14:40:45 2021

@author: carlos
"""

import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import parse_abstracts
from parse_abstracts import *
import seaborn as sns

# root = "/Users/carlos/Documents/GitHub/sepex_ontology/"

sepex_editions = [2012,2014,2016,2018]
lexicons = ["disorders","concepts","tasks","anatomy"]

overlap = pd.DataFrame(columns=lexicons)
overlap_weighted = pd.DataFrame(columns=lexicons)


for idx,sepex_year in enumerate(sepex_editions):

    # Read in abstracts
    print('Reading abstracts ' + str(sepex_year))
    lexicons_length = [] # to compute weighted overlap
    abstracts = read_abstracts(sepex_year)
    
    # # SEARCH IN COGNITIVE ATLAS LEXICON
    # cogat_prevalence = search_cogat(abstracts) # get prevalence of cogat concepts in sepex abstracts
    # cogat_prevalence_any = cogat_prevalence[cogat_prevalence[0] != 0] # remove rows with zeros (concepts that don't appear in SEPEX abstracts)
    # cogat_overlap = len(cogat_prevalence_any) / len(cogat_prevalence) # compute overlap between cognitive atlas and SEPEX abstracts
    # print("Overlap between CogAtlas and SEPEX" + str(sepex_year) + ": " + (str(cogat_overlap)))
    
    # # SEARCH IN DSM LEXICON
    # dsm_prevalence = search_lexicon(abstracts,"lexicon_dsm") # get prevalence of cogat concepts in sepex abstracts
    # dsm_prevalence_any = dsm_prevalence[dsm_prevalence[0] != 0] # remove rows with zeros (concepts that don't appear in SEPEX abstracts)
    # dsm_overlap = len(dsm_prevalence_any) / len(dsm_prevalence) # compute overlap between cognitive atlas and SEPEX abstracts
    # print("Overlap between DSM and SEPEX" + str(sepex_year) + ": " + (str(dsm_overlap)))
    
    # # SEARCH IN RDOC LEXICON
    # rdoc_prevalence = search_lexicon(abstracts,"lexicon_rdoc") # get prevalence of cogat concepts in sepex abstracts
    # rdoc_prevalence_any = rdoc_prevalence[rdoc_prevalence[0] != 0] # remove rows with zeros (concepts that don't appear in SEPEX abstracts)
    # rdoc_overlap = len(rdoc_prevalence_any) / len(rdoc_prevalence) # compute overlap between cognitive atlas and SEPEX abstracts
    # print("Overlap between RDoc and SEPEX" + str(sepex_year) + ": " + (str(rdoc_overlap)))
    
    
    
    # SEARCH IN COGNITIVE ATLAS sub-LEXICONS
    cogat_prevalence = search_lexicon(abstracts,"cognitive-atlas_disorders") # get prevalence of cogat concepts in sepex abstracts
    cogat_prevalence_any = cogat_prevalence[cogat_prevalence[0] != 0] # remove rows with zeros (concepts that don't appear in SEPEX abstracts)
    cogat_overlap = len(cogat_prevalence_any) / len(cogat_prevalence) # compute overlap between cognitive atlas and SEPEX abstracts
    print("Overlap between CogAtlas-DISORDERS and SEPEX" + str(sepex_year) + ": " + (str(cogat_overlap)))
    overlap.loc[idx,"disorders"] = cogat_overlap
    lexicons_length.append(len(cogat_prevalence))
    
    cogat_prevalence = search_lexicon(abstracts,"cognitive-atlas_concepts") # get prevalence of cogat concepts in sepex abstracts
    cogat_prevalence_any = cogat_prevalence[cogat_prevalence[0] != 0] # remove rows with zeros (concepts that don't appear in SEPEX abstracts)
    cogat_overlap = len(cogat_prevalence_any) / len(cogat_prevalence) # compute overlap between cognitive atlas and SEPEX abstracts
    print("Overlap between CogAtlas-CONCEPTS and SEPEX" + str(sepex_year) + ": " + (str(cogat_overlap)))
    overlap.loc[idx,"concepts"] = cogat_overlap
    lexicons_length.append(len(cogat_prevalence))
    
    cogat_prevalence = search_lexicon(abstracts,"cognitive-atlas_tasks") # get prevalence of cogat concepts in sepex abstracts
    cogat_prevalence_any = cogat_prevalence[cogat_prevalence[0] != 0] # remove rows with zeros (concepts that don't appear in SEPEX abstracts)
    cogat_overlap = len(cogat_prevalence_any) / len(cogat_prevalence) # compute overlap between cognitive atlas and SEPEX abstracts
    print("Overlap between CogAtlas-TASKS and SEPEX" + str(sepex_year) + ": " + (str(cogat_overlap)))
    overlap.loc[idx,"tasks"] = cogat_overlap
    lexicons_length.append(len(cogat_prevalence))
    
    # SEARCH IN MD ANATOMY LEXICON
    cogat_prevalence = search_lexicon(abstracts,"NIF-GrossAnatomy") # get prevalence of cogat concepts in sepex abstracts
    cogat_prevalence_any = cogat_prevalence[cogat_prevalence[0] != 0] # remove rows with zeros (concepts that don't appear in SEPEX abstracts)
    cogat_overlap = len(cogat_prevalence_any) / len(cogat_prevalence) # compute overlap between cognitive atlas and SEPEX abstracts
    print("Overlap between NIF-GrossAnatomy and SEPEX" + str(sepex_year) + ": " + (str(cogat_overlap)))
    overlap.loc[idx,"anatomy"] = cogat_overlap
    lexicons_length.append(len(cogat_prevalence))
    
    # normalize by corpus size
    weights = [x/sum(lexicons_length) for x in lexicons_length]
    
    overlap_weighted.loc[idx,:] = overlap.loc[idx,:] * weights

# plot non-weighted results
g = sns.catplot(data=overlap,kind="bar")
# g.set_xticks(range(len(sepex_editions))) # <--- set the ticks first
# g.set_xticklabels(sepex_editions)
g.despine(right=True)
g.set_axis_labels("", "prevalence across editions")
plt.savefig(root + 'figures_nospanish/prevalence_across_editions.png')

g = sns.lineplot(data=overlap)
g.set_xticks(range(len(sepex_editions))) # <--- set the ticks first
g.set_xticklabels(sepex_editions)
g.set_ylabel("prevalence")
plt.savefig(root + 'figures_nospanish/prevalence.png')


# plot weighted results
g = sns.catplot(data=overlap_weighted,kind="bar")
# g.set_xticks(range(len(sepex_editions))) # <--- set the ticks first
# g.set_xticklabels(sepex_editions)
g.despine(right=True)
g.set_axis_labels("", "weighted prevalence across editions")
plt.savefig(root + 'figures_nospanish/w_prevalence_across_editions.png')


g = sns.lineplot(data=overlap_weighted)
g.set_xticks(range(len(sepex_editions))) # <--- set the ticks first
g.set_xticklabels(sepex_editions)
g.set_ylabel("weighted prevalence")
plt.savefig(root + 'figures_nospanish/w_prevalence.png')


# # TAG CLOUDS


# word_list = cogat_prevalence_any.index

# text = str(' ')

# for idx,word in enumerate(word_list):
#     word = word + ' '
#     text += word * int(cogat_prevalence_any[0][idx])
#     #print(word, prevalence_any[idx])


# wordcloud = WordCloud(background_color="white",
#                       collocations=False).generate(text)

# # Display the generated image:
# # the matplotlib way:
# plt.figure(figsize=(4,4), dpi=1200)
# plt.imshow(wordcloud, interpolation='bilinear')
# plt.axis("off")
# plt.savefig(root + 'figures/cogat_sepex12_cloud.png')