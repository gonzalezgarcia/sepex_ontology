# forked and adapted from https://github.com/poldrack/william_james
# code updated to python 3 requirements

from bs4 import BeautifulSoup 
import requests
import json
import re

base_url = "http://psychclassics.yorku.ca/James/Principles"
response = requests.get(base_url).text
regexp = 'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
links = re.findall(regexp, response)
chapters = [x.replace('HREF="',"").strip('"') for x in re.findall('HREF=".*[.]htm"',response)]

# Chapters(0) is link back to index
chapters.pop(0)

# Function to parse a paragraph and return text
tag_regexp = re.compile(r'<[^>]+>')

def remove_tags(text):
    text = text.replace("<p>","").replace("</p>","").replace("&nbsp;","")
    text = text.replace("\r"," ").replace("\n","")
    return tag_regexp.sub('', text)

# Let's save a dictionary of raw text based on chapter_id, paragraph
raw = dict()
count = 0

for chapter in chapters:
    chapter_url = "%s/%s" %(base_url,chapter)
    chapter_id = "%s_%s" %(count,chapter.strip(".htm"))
    response = requests.get(chapter_url).text
    soup = BeautifulSoup(response)
    paragraphs = list(str(x) for x in soup.findAll('p'))
    for p in range(len(paragraphs)):
        paragraph = paragraphs[p]
        raw["%s_%s" %(chapter_id,p)] = remove_tags(paragraph)
    count+=1    

# Save as json
filey = open("william_james.json",'w')
filey.write(json.dumps(raw, sort_keys=True,indent=4, separators=(',', ': ')))
filey.close()
