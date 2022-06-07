#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# """
# Created on Wed Dec 22 14:40:45 2021

# @author: carlos
# """

import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from parse_abstracts import *
import seaborn as sns
import numpy as np

''' SET UP AND PREALLOCATE ''' 
#root = "/home/javier/git_repos/sepex_ontology/"
root = "/Users/carlos/Documents/GitHub/sepex_ontology/"

sepex_editions = [2012,2014,2016,2018,2022]
lexicons = ["disorders","concepts","tasks","anatomy"]
overlap = pd.DataFrame(columns=lexicons)
overlap_weighted = pd.DataFrame(columns=lexicons)

''' PARSE AND COMPARE'''
for idx,sepex_year in enumerate(sepex_editions):

    # Read in abstracts
    print('Reading abstracts ' + str(sepex_year))
    lexicons_length = [] # to compute weighted overlap
    abstracts = read_abstracts(sepex_year)
    
    
    # SEARCH IN COGNITIVE ATLAS sub-LEXICONS
    cogat_prevalence = search_lexicon(abstracts,"cognitive-atlas_disorders") # get prevalence of cogat concepts in sepex abstracts
    cogat_prevalence_any = cogat_prevalence[cogat_prevalence[0] != 0] # remove rows with zeros (concepts that don't appear in SEPEX abstracts)
    cogat_overlap = len(cogat_prevalence_any) / len(cogat_prevalence) # compute overlap between cognitive atlas and SEPEX abstracts
    print("Overlap between CogAtlas-DISORDERS and SEPEX" + str(sepex_year) + ": " + (str(cogat_overlap)))
    overlap.loc[idx,"disorders"] = cogat_overlap
    lexicons_length.append(len(cogat_prevalence))
    draw_wordclod(cogat_prevalence_any, 'sepex' + str(sepex_year) + '_disorders_cloud')
    
    cogat_prevalence = search_lexicon(abstracts,"cognitive-atlas_concepts") # get prevalence of cogat concepts in sepex abstracts
    cogat_prevalence_any = cogat_prevalence[cogat_prevalence[0] != 0] # remove rows with zeros (concepts that don't appear in SEPEX abstracts)
    cogat_overlap = len(cogat_prevalence_any) / len(cogat_prevalence) # compute overlap between cognitive atlas and SEPEX abstracts
    print("Overlap between CogAtlas-CONCEPTS and SEPEX" + str(sepex_year) + ": " + (str(cogat_overlap)))
    overlap.loc[idx,"concepts"] = cogat_overlap
    lexicons_length.append(len(cogat_prevalence))
    draw_wordclod(cogat_prevalence_any, 'sepex' + str(sepex_year) + '_concepts_cloud')
    
    cogat_prevalence = search_lexicon(abstracts,"cognitive-atlas_tasks") # get prevalence of cogat concepts in sepex abstracts
    cogat_prevalence_any = cogat_prevalence[cogat_prevalence[0] != 0] # remove rows with zeros (concepts that don't appear in SEPEX abstracts)
    cogat_overlap = len(cogat_prevalence_any) / len(cogat_prevalence) # compute overlap between cognitive atlas and SEPEX abstracts
    print("Overlap between CogAtlas-TASKS and SEPEX" + str(sepex_year) + ": " + (str(cogat_overlap)))
    overlap.loc[idx,"tasks"] = cogat_overlap
    lexicons_length.append(len(cogat_prevalence))
    draw_wordclod(cogat_prevalence_any, 'sepex' + str(sepex_year) + '_tasks_cloud')
    
    # SEARCH IN MD ANATOMY LEXICON
    cogat_prevalence = search_lexicon(abstracts,"NIF-GrossAnatomy_edited") # get prevalence of cogat concepts in sepex abstracts
    cogat_prevalence_any = cogat_prevalence[cogat_prevalence[0] != 0] # remove rows with zeros (concepts that don't appear in SEPEX abstracts)
    cogat_overlap = len(cogat_prevalence_any) / len(cogat_prevalence) # compute overlap between cognitive atlas and SEPEX abstracts
    print("Overlap between NIF-GrossAnatomy and SEPEX" + str(sepex_year) + ": " + (str(cogat_overlap)))
    overlap.loc[idx,"anatomy"] = cogat_overlap
    lexicons_length.append(len(cogat_prevalence))
    draw_wordclod(cogat_prevalence_any, 'sepex' + str(sepex_year) + '_anatomy_cloud')
    
    # normalize by corpus size
    weights = [x/sum(lexicons_length) for x in lexicons_length]
    
    overlap_weighted.loc[idx,:] = overlap.loc[idx,:] * weights

''' PLOT NON-WEIGHTED RESULTS'''

# average across editions
g = plt.figure()
sns.set_style("white")
sns.set_context("poster",font_scale=0.75,rc={"figure.figsize":(20, 20)})
g = sns.catplot(data=overlap,kind="bar")
g.despine(right=True)
g.set_axis_labels("", "prevalence across editions")
g.figure.savefig(root + 'figures_nospanish/prevalence_across_editions.png',dpi=600,bbox_inches="tight")

# split by editions
g = plt.figure()
sns.set_style("white")
sns.set_context("notebook",font_scale=1.5,rc={"figure.figsize":(20, 20)})
g = sns.lineplot(data=overlap)
g.set_xticks(range(len(sepex_editions))) # <--- set the ticks first
g.set_xticklabels(sepex_editions)
g.set_ylabel("prevalence")
g.figure.savefig(root + 'figures_nospanish/prevalence.png',dpi=600,bbox_inches="tight")

''' PLOT WEIGHTED RESULTS'''

# average across editions
g = plt.figure()
sns.set_style("white")
sns.set_context("poster",font_scale=0.75,rc={"figure.figsize":(20, 20)})
g = sns.catplot(data=overlap_weighted,kind="bar")
g.despine(right=True)
g.set_axis_labels("", "weighted prevalence across editions")
g.figure.savefig(root + 'figures_nospanish/w_prevalence_across_editions.png',dpi=600,bbox_inches="tight")

# split by editions
g = plt.figure()
sns.set_style("white")
sns.set_context("notebook",font_scale=1.5,rc={"figure.figsize":(20, 20)})
g = sns.lineplot(data=overlap_weighted)
g.set_xticks(range(len(sepex_editions))) # <--- set the ticks first
g.set_xticklabels(sepex_editions)
g.set_ylabel("weighted prevalence")
g.set_xlabel("year")
g.get_legend().remove()
g.figure.savefig(root + 'figures_nospanish/w_prevalence.png',dpi=600,bbox_inches="tight")

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
ax.figure.savefig(root + 'figures_nospanish/w_prevalence_stacked.png',dpi=600,bbox_inches="tight")

# # polar plot
# overlap_weighted['year']= ['2012','2014','2016','2018'] #year
# overlap_weighted.set_index('year', inplace=True)
# # Each attribute we'll plot in the radar chart.
# labels = ['disorders', 'concepts', 'tasks', 'anatomy']

# # Let's look at the 2012 sepex and plot it.
# values = overlap_weighted.loc['2012'].tolist()
# # Number of variables we're plotting.
# num_vars = len(labels)
# # Split the circle into even parts and save the angles
# # so we know where to put each axis.
# angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()

# # The plot is a circle, so we need to "complete the loop"
# # and append the start value to the end.
# values += values[:1]
# angles += angles[:1]

# # ax = plt.subplot(polar=True)
# fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))

# # Helper function to plot each car on the radar chart.
# def add_to_radar(year, color):
#   values = overlap_weighted.loc[year].tolist()
#   values += values[:1]
#   values = [i/sum(values) for i in values] # Make it a proportion
#   ax.plot(angles, values, color=color, linewidth=1, label=year)
#   ax.fill(angles, values, color=color, alpha=0.25)

# add_to_radar('2012', '#1aaf6c')
# add_to_radar('2014', '#429bf4')
# add_to_radar('2016', '#d42cea')
# add_to_radar('2018', 'lightsalmon')
# # Fix axis to go in the right order and start at 12 o'clock.
# ax.set_theta_offset(np.pi / 2)
# ax.set_theta_direction(-1)

# # Draw axis lines for each angle and label.
# ax.set_thetagrids(np.degrees(angles[:-1]), labels)

# # Go through labels and adjust alignment based on where
# # it is in the circle.
# for label, angle in zip(ax.get_xticklabels(), angles):
#   if angle in (0, np.pi):
#     label.set_horizontalalignment('center')
#   elif 0 < angle < np.pi:
#     label.set_horizontalalignment('left')
#   else:
#     label.set_horizontalalignment('right')

# # Set position of y-labels (0-100) to be in the middle
# # of the first two axes.
# ax.set_rlabel_position(180 / num_vars)
# # Add some custom styling.
# # Change the color of the tick labels.
# ax.tick_params(colors='#222222')
# # Make the y-axis (0-100) labels smaller.
# ax.tick_params(axis='y', labelsize=20)
# # Change the color of the circular gridlines.
# ax.grid(color='#AAAAAA')
# # Change the color of the outermost gridline (the spine).
# ax.spines['polar'].set_color('#222222')
# # Change the background color inside the circle itself.
# ax.set_facecolor('#FAFAFA')
# # Add a legend as well.
# ax.legend(bbox_to_anchor=(1.75, 1.45),title="SEPEX year")
# ax.figure.savefig(root + 'figures_nospanish/w_prevalence_polar2.png',dpi=600,bbox_inches="tight")
