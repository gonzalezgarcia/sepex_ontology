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
import json
import re
import nltk
from nltk.corpus import stopwords
import pingouin as pg




# get data directory (using getcwd() is needed to support running example in generated IPython notebook)
root = "/home/javier/git_repos/sepex_ontology/"
root = "/Users/carlos/documents/GitHub/sepex_ontology/"

def is_wj_here(year,lexicon):
    print(f"Analyzing {year} SEPEX {lexicon}...")
    #  create "SEPEX lexicon" by loading abstracts and checking overlap with specific lexicon
    abstracts = read_abstracts(year)
    prevalence = search_lexicon(abstracts,lexicon)
    prevalence_any = prevalence[prevalence[0] != 0]
    masked_concepts = list(prevalence_any.index)
    features = pd.DataFrame(columns=masked_concepts)
      
    # load raw wj
    paragraphs = json.load(open(root + "wj/william_james.json","r"))

    count = 1
    for pid,paragraph in paragraphs.items():
        if len(paragraph) > 0:
            words = processText(paragraph)
            text = " ".join(words)
            #print("Parsing paragraph %s, %s of %s" %(pid,count,len(paragraphs)))
            # search for each cognitive atlas term, take a count
            for concept in features.columns:
                processed_concept = " ".join(processText(str(concept)))
                features.loc[pid,concept] = len(re.findall(processed_concept,text))
            #print("Found %s total concept occurrences for %s" %(features.loc[pid].sum(),pid))
            count +=1
        else:
            #print("No text found for paragraph %s" %(pid))
            features.loc[pid] = np.zeros(len(masked_concepts))
    
    # Get concepts that overlap between WJ and SEPEX lexicon
    prevalence = features.sum()
    prevalence_any = prevalence.loc[~(prevalence==0)]
    departures = prevalence.loc[(prevalence==0)]
    overlap = (len(prevalence_any) / len(prevalence))*100
    overlap_length = len(prevalence_any) # to compute weighted overlap  
    
    print(f"Proportion of {year} SEPEX {lexicon} in WJ's principles:  {overlap}%.")
    print(f"Prevalence of {year} SEPEX {lexicon} in WJ's principles:  {overlap_length}.")
    return overlap, overlap_length

sepex_editions = [2012, 2014, 2016, 2018, 2022]
lexicons = ["cognitive-atlas_disorders",
            "cognitive-atlas_concepts",
            "cognitive-atlas_tasks",
            "NIF-GrossAnatomy_edited"]

overlap = pd.DataFrame(columns=lexicons)
overlap_weighted = pd.DataFrame(columns=lexicons)

for idx_sepex,sepex_year in enumerate(sepex_editions):
    overlap_length = pd.DataFrame(columns=lexicons)
    for idx_lexicon,lexicon in enumerate(lexicons):
        overlap.loc[idx_sepex,lexicon], overlap_length.loc[0,lexicon] = is_wj_here(sepex_year, lexicon)
    # normalize by corpus size  
    overlap_weighted.loc[idx_sepex,:] = np.array([(overlap_length.loc[0])]) / int(overlap_length.sum(axis=1))
    
''' PLOT WEIGHTED RESULTS and do ANOVA'''
# rename columns
overlap_weighted.columns = ['disorders', 'concepts', 'tasks', 'anatomy']
# average across editions
g = plt.figure()
sns.set_style("white")
sns.set_context("poster",font_scale=0.75,rc={"figure.figsize":(20, 20)})
g = sns.catplot(data=overlap_weighted,kind="bar")
g.despine(right=True)
g.set_axis_labels("", "weighted overlap with James")
g.figure.savefig(root + 'figures_nospanish/w_overlap_WJ_across_editions.png',dpi=600,bbox_inches="tight")


# transform to long for stats purposes
overlap_weighted_wide = overlap_weighted.copy()
overlap_weighted_wide["year"] = [2012, 2014, 2016, 2018, 2022]
overlap_weighted_wide = overlap_weighted_wide.apply(pd.to_numeric)

overlap_weighted_long = pd.melt(overlap_weighted_wide,
                                id_vars=['year'],
                                var_name = "lexicon",
                                value_name = "WPI")

# perform one-way anova
aov = pg.rm_anova(dv='WPI', within='lexicon',
                  subject='year', data=overlap_weighted_long, detailed=True,
                  effsize="np2", correction = True)
aov.round(3)
# and post hoc tests
post_hocs = pg.pairwise_ttests(dv='WPI',
                               within='lexicon',
                               subject='year', 
                               data=overlap_weighted_long,
                               padjust='bonf',
                               effsize = 'cohen')
post_hocs.round(3)

g = plt.figure()
sns.set_style("white")
sns.set_context("notebook",font_scale=1.5,rc={"figure.figsize":(20, 20)})
g = sns.lineplot(data=overlap_weighted)
g.set_xticks(range(len(sepex_editions))) # <--- set the ticks first
g.set_xticklabels(sepex_editions)
g.set_ylabel("weighted prevalence")
g.set_xlabel("year")
g.get_legend().remove()
g.figure.savefig(root + 'figures_nospanish/w_WJ_prevalence.png',dpi=600,bbox_inches="tight")

''' PLOT RELATIVE RESULTS'''
# convert to percentage
labels = ['disorders', 'concepts', 'tasks', 'anatomy']
overlap_percentage = overlap_weighted.copy()
overlap_percentage[labels] = overlap_percentage[labels].div(overlap_percentage[labels].sum(axis=1), axis=0).multiply(100)
overlap_percentage['year']= ['2012','2014','2016','2018','2022'] # add year column
# transform to long format
overlap_percentage_long = pd.melt(overlap_percentage,
                                  id_vars=['year'],
                                  value_vars=labels,
                                  var_name='lexicon',
                                  value_name='percentage')

# plot stacked bar plot
g = plt.figure()
sns.set_style("white")
sns.set_context("notebook",font_scale=1.5,rc={"figure.figsize":(20, 20)})
ax = sns.histplot(overlap_percentage_long,
                  x='year', hue='lexicon', weights='percentage', multiple='stack', shrink=0.8)
legend = ax.get_legend()
legend.set_bbox_to_anchor((1, 1))
ax.set_ylabel(" relative overlap with James (%)")
ax.figure.savefig(root + 'figures_nospanish/w_WJ_prevalence_stacked.png',dpi=600,bbox_inches="tight")

#  create "SEPEX lexicon" by loading abstracts and checking overlap with cogat
abstracts = read_abstracts(2018)

cogneuro_prevalence = search_lexicon(abstracts,"cognitive-atlas_concepts") # get prevalence of cogat concepts in sepex abstracts
cogneuro_prevalence_any = cogneuro_prevalence[cogneuro_prevalence[0] != 0]
masked_sepex_concepts = list(cogneuro_prevalence_any.index)
features_concepts = pd.DataFrame(columns=masked_sepex_concepts)

disorders_prevalence = search_lexicon(abstracts,"cognitive-atlas_disorders") # get prevalence of cogat concepts in sepex abstracts
disorders_prevalence_any = disorders_prevalence[disorders_prevalence[0] != 0]
masked_sepex_disorders = list(disorders_prevalence_any.index)
features_disorders = pd.DataFrame(columns=masked_sepex_disorders)


# load raw wj
paragraphs = json.load(open(root + "wj/william_james.json","r"))

count = 1

for pid,paragraph in paragraphs.items():
    if len(paragraph) > 0:
        words = processText(paragraph)
        text = " ".join(words)
        print("Parsing paragraph %s, %s of %s" %(pid,count,len(paragraphs)))
        # search for each cognitive atlas term, take a count
        for concept in features_concepts.columns:
            processed_concept = " ".join(processText(str(concept)))
            features_concepts.loc[pid,concept] = len(re.findall(processed_concept,text))
        print("Found %s total concept occurrences for %s" %(features_concepts.loc[pid].sum(),pid))
        for concept in features_disorders.columns:
            processed_concept = " ".join(processText(str(concept)))
            features_disorders.loc[pid,concept] = len(re.findall(processed_concept,text))
        print("Found %s total disorders occurrences for %s" %(features_concepts.loc[pid].sum(),pid))
        count +=1
    else:
        print("No text found for paragraph %s" %(pid))
        features_concepts.loc[pid] = np.zeros(len(masked_sepex_concepts))
        features_disorders.loc[pid] = np.zeros(len(masked_sepex_disorders))

features.to_csv(root + 'data/sepex_features.csv')
# features= pd.read_csv(root + 'data/sepex_features.csv')

# Get concepts that overlap between WJ and SEPEX lexicon
prevalence_concepts = features_concepts.sum()
prevalence_concepts_any = prevalence_concepts.loc[~(prevalence_concepts==0)]
departures_concepts = prevalence_concepts.loc[(prevalence_concepts==0)]
overlap_concepts = (len(prevalence_concepts_any) / len(prevalence_concepts))*100
print("Proportion of SEPEX concepts presents in WJ's principles: " + (str(overlap_concepts)))

# Get disorders that overlap between WJ and SEPEX lexicon
prevalence_disorders = features_disorders.sum()
prevalence_disorders_any = prevalence_disorders.loc[~(prevalence_disorders==0)]
departures_disorders = prevalence_disorders.loc[(prevalence_disorders==0)]
overlap_disorders = (len(prevalence_disorders_any) / len(prevalence_disorders))*100
print("Proportion of SEPEX disorders presents in WJ's principles: " + (str(overlap_disorders)))


# df = pd.read_csv(root + 'data/sepex_features.csv',sep='\t')
# df = df.drop('Unnamed: 0', 1) # clean up
# prevalence = df.sum()
# prevalence_any = prevalence.loc[~(prevalence==0)]

# # compute overlap between cognitive atlas and william james
# overlap = len(prevalence_any) / len(prevalence)
# print("Overlap between CogAtlas and WJ's principles: " + (str(overlap)))

overlap_bio  = 0.09
overlap_cell = 1.05

crossdisciplines = np.array([overlap*100,overlap_bio,overlap_cell])

cross_df = pd.DataFrame()
cross_df["overlap"] = crossdisciplines
cross_df["discipline"] = ["SEPEX\n(psychology)", "biology", "cellular"]

g = plt.figure()
sns.set_style("white")
sns.set_context("notebook",font_scale=1.5,rc={"figure.figsize":(20, 20)})
g = sns.barplot(x=cross_df["discipline"], y=cross_df["overlap"], palette="rocket")
g.set_ylabel("overlap with pre-scientific terms(%)")
g.figure.savefig(root + 'figures_nospanish/crossdiscipline.png',dpi=600,bbox_inches="tight")

# get all words that appear in WJ
word_list = prevalence_any.index



# compute proportion of sepex-cogat words that are shared with WJ-cogat

sepex_editions = [2012,2014,2016,2018,2022]
lexicons = ["concepts", "disorders", "tasks", "anatomy"]

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
    # SEARCH IN COGNITIVE ATLAS sub-LEXICONS
    cogat_prevalence = search_lexicon(abstracts,"cognitive-atlas_disorders") # get prevalence of cogat concepts in sepex abstracts
    cogat_prevalence_any = cogat_prevalence[cogat_prevalence[0] != 0]
    word_list_sepex = cogat_prevalence_any.index
    intersection = set(word_list) & set(word_list_sepex)
    overlap.loc[idx,"disorders"] = (len(intersection) / len(word_list_sepex)) * 100
    # SEARCH IN COGNITIVE ATLAS sub-LEXICONS
    cogat_prevalence = search_lexicon(abstracts,"cognitive-atlas_tasks") # get prevalence of cogat concepts in sepex abstracts
    cogat_prevalence_any = cogat_prevalence[cogat_prevalence[0] != 0]
    word_list_sepex = cogat_prevalence_any.index
    intersection = set(word_list) & set(word_list_sepex)
    overlap.loc[idx,"tasks"] = (len(intersection) / len(word_list_sepex)) * 100
    # SEARCH IN COGNITIVE ATLAS sub-LEXICONS
    cogat_prevalence = search_lexicon(abstracts,"NIF-GrossAnatomy_edited") # get prevalence of cogat concepts in sepex abstracts
    cogat_prevalence_any = cogat_prevalence[cogat_prevalence[0] != 0]
    word_list_sepex = cogat_prevalence_any.index
    intersection = set(word_list) & set(word_list_sepex)
    overlap.loc[idx,"anatomy"] = (len(intersection) / len(word_list_sepex)) * 100


# plot overlap between WJ and sepex

sns.set_style("white")
sns.set_context("poster",font_scale=1,rc={"figure.figsize":(20, 20)})
g = sns.lineplot(data=overlap)
g.set_xticks(range(len(sepex_editions))) # <--- set the ticks first
g.set_xticklabels(sepex_editions)
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

draw_wordclod(shared, 'sepex22_shared_WJ_cloud')
draw_wordclod(unique, 'sepex22_unique_WJ_cloud')

# # extract words
# word_list = prevalence_data.index

# unique["count"] = unique[0]
# unique["word"] = unique.index

# data = dict(zip(unique['word'].tolist(), unique['count'].tolist()))

# wc = WordCloud(width=800, height=400, max_words=200).generate_from_frequencies(data)

# plt.figure(figsize=(10, 10))
# plt.imshow(wc, interpolation='bilinear')
# plt.axis('off')
# plt.show()

# shared["count"] = shared[0]
# shared["word"] = shared.index

# data = dict(zip(shared['word'].tolist(), shared['count'].tolist()))

# wc = WordCloud(width=800, height=400, max_words=200).generate_from_frequencies(data)

# plt.figure(figsize=(10, 10))
# plt.imshow(wc, interpolation='bilinear')
# plt.axis('off')
# plt.show()


