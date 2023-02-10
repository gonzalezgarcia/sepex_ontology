#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# """
# Created on Wed Dec 22 14:40:45 2021

# @author: carlos
# """

import pandas as pd
import matplotlib.pyplot as plt
from parse_abstracts import *
import seaborn as sns
import numpy as np
import pingouin as pg
import getpass

'''SET ROOT FOLDER'''
username = getpass.getuser()
if username == "javierortiz":
    root_folder = "/Users/javierortiz/github_repos/sepex_ontology/"
else:
    root_folder = "/Users/carlos/Documents/GitHub/sepex_ontology/"

fig_folder = root_folder + "figures_revision"

''' SET UP AND PREALLOCATE ''' 
plot_wordlcouds = 0
sepex_editions = [2012,2014,2016,2018,2022]
lexicons = ["disorders","concepts","tasks","anatomy"]
overlap = pd.DataFrame(columns=lexicons)
overlap_new = pd.DataFrame(columns=lexicons)
overlap_weighted = pd.DataFrame(columns=lexicons)
overlap_weighted_new = pd.DataFrame(columns=lexicons)

''' PARSE AND COMPARE'''
if plot_wordlcouds:
    cnt = 0
    plt.figure(figsize=(20,20), dpi=300)

for idx,sepex_year in enumerate(sepex_editions):
    

    # Read in abstracts
    print('Reading abstracts ' + str(sepex_year))
    lexicons_length = [] # to compute weighted overlap
    abstracts = read_abstracts(sepex_year)
    
    # Loop through lexicons
    all_lexicons = ("cognitive-atlas_disorders", "cognitive-atlas_concepts", "cognitive-atlas_tasks", "NIF-GrossAnatomy_edited")
    for lex_ind, lex_name in (enumerate(all_lexicons)):
        
        # SEARCH IN COGNITIVE ATLAS sub-LEXICONS
        cogat_prevalence = search_lexicon(abstracts,lex_name) # get prevalence of cogat concepts in sepex abstracts
        cogat_prevalence_any = cogat_prevalence[cogat_prevalence[0] != 0] # remove rows with zeros (concepts that don't appear in SEPEX abstracts)
        cogat_overlap = len(cogat_prevalence_any) / len(cogat_prevalence) # compute overlap between cognitive atlas and SEPEX abstracts
        cogat_overlap_new = len(cogat_prevalence_any) / len(abstracts) # reviewer: proportion of SEPEX terms present in lexicon
        print("Overlap between " + lex_name + " and SEPEX" + str(sepex_year) + ": " )
        print("New computation: " + str(cogat_overlap_new))
        print("Old computation: " + str(cogat_overlap))
        overlap.loc[idx,lexicons[lex_ind]] = cogat_overlap
        overlap_new.loc[idx,lexicons[lex_ind]] = cogat_overlap_new
        lexicons_length.append(len(cogat_prevalence))
        if plot_wordlcouds:
            cnt += 1
            plt.subplot(5, 4, cnt)
            draw_wordclod(cogat_prevalence_any, 'sepex' + str(sepex_year) + lex_name + '_cloud')
    
    # normalize by corpus size  
    overlap_weighted.loc[idx,:] = overlap.loc[idx,:] / sum(lexicons_length)
    overlap_weighted_new.loc[idx,:] = overlap_new.loc[idx,:] / sum(lexicons_length)

if plot_wordlcouds:
    plt.savefig(root + 'figures/wordclouds_all.png', dpi=600, bbox_inches='tight')
    plt.figure(figsize=(20,20), dpi=300)
    draw_wordclod(cogat_prevalence_any, 'sepex' + str(sepex_year) + '_tasks_cloud')
    plt.savefig(root + fig_folder + '/tasks2022.png', dpi=600, bbox_inches='tight')


''' PLOT NON-WEIGHTED RESULTS'''
# average across editions
g = plt.figure()
sns.set_style("white")
sns.set_context("poster",font_scale=0.75,rc={"figure.figsize":(20, 20)})
g = sns.catplot(data=overlap,kind="bar")
g.despine(right=True)
g.set_axis_labels("", "prevalence across editions")
g.figure.savefig(root + fig_folder + '/prevalence_across_editions.png',dpi=600,bbox_inches="tight")

# split by editions
g = plt.figure()
sns.set_style("white")
sns.set_context("notebook",font_scale=1.5,rc={"figure.figsize":(20, 20)})
g = sns.lineplot(data=overlap)
g.set_xticks(range(len(sepex_editions))) # <--- set the ticks first
g.set_xticklabels(sepex_editions)
g.set_ylabel("prevalence")
g.figure.savefig(root + fig_folder + '/prevalence.png',dpi=600,bbox_inches="tight")

''' PLOT Reviewer's 'NON-WEIGHTED RESULTS'''
# average across editions
g = plt.figure()
sns.set_style("white")
sns.set_context("poster",font_scale=0.75,rc={"figure.figsize":(20, 20)})
g = sns.catplot(data=overlap_new,kind="bar")
g.despine(right=True)
g.set_axis_labels("", "prevalence across editions")
g.figure.savefig(root + fig_folder + '/reviewer_prevalence_across_editions.png',dpi=600,bbox_inches="tight")

# split by editions
g = plt.figure()
sns.set_style("white")
sns.set_context("notebook",font_scale=1.5,rc={"figure.figsize":(20, 20)})
g = sns.lineplot(data=overlap_new)
g.set_xticks(range(len(sepex_editions))) # <--- set the ticks first
g.set_xticklabels(sepex_editions)
g.set_ylabel("prevalence")
g.figure.savefig(root + fig_folder + '/reviewer_prevalence.png',dpi=600,bbox_inches="tight")


''' PLOT Reviewer's WEIGHTED RESULTS'''
# average across editions
g = plt.figure()
sns.set_style("white")
sns.set_context("poster",font_scale=0.75,rc={"figure.figsize":(20, 20)})
g = sns.catplot(data=overlap_weighted_new,kind="bar")
g.despine(right=True)
g.set_axis_labels("", "Reviewer weighting prevalence across editions")
g.figure.savefig(root + fig_folder + '/reviewer_w_prevalence_across_editions.png',dpi=600,bbox_inches="tight")

''' PLOT WEIGHTED RESULTS and do ANOVA'''
# average across editions
g = plt.figure()
sns.set_style("white")
sns.set_context("poster",font_scale=0.75,rc={"figure.figsize":(20, 20)})
g = sns.catplot(data=overlap_weighted,kind="bar")
g.despine(right=True)
g.set_axis_labels("", "weighted prevalence across editions")
g.figure.savefig(root + fig_folder + '/w_prevalence_across_editions.png',dpi=600,bbox_inches="tight")

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
g.figure.savefig(root + fig_folder + '/w_prevalence.png',dpi=600,bbox_inches="tight")


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
ax.set_ylabel(" relative prevalence (%)")
ax.figure.savefig(root + fig_folder + '/w_prevalence_stacked.png',dpi=600,bbox_inches="tight")