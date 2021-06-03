# -*- coding: utf-8 -*-

import requests
import bs4 as BeautifulSoup
import pandas as pd
import re

# define the metacritic urls to pull from
urls = ["https://www.metacritic.com/feature/best-albums-of-2009", 
        "https://www.metacritic.com/feature/best-music-of-2010", 
        "https://www.metacritic.com/feature/best-albums-of-2011", 
        "https://www.metacritic.com/feature/best-albums-of-2012", 
        "https://www.metacritic.com/feature/best-albums-of-2013", 
        "https://www.metacritic.com/feature/best-albums-of-2014", 
        "https://www.metacritic.com/feature/best-albums-of-2015", 
        "https://www.metacritic.com/feature/best-albums-of-2016", 
        "https://www.metacritic.com/feature/best-albums-released-in-2017",
        "https://www.metacritic.com/feature/best-albums-released-in-2018"]

# define src names for each source
srcs = ["metacritic-ye%d" % year for year in range(2009, 2019)]

# create empty list to store each list's df
dfs = [ ]

# for each list, parse out each items rank/title/artist and store in df
for i in range(len(urls)):
    url = urls[i]
    src = srcs[i]    
    print("%s -- %s" % (src, url))
        
    res = requests.get(url, headers = {'User-Agent': 'Chrome/32.0.1700.76 m'})
    soup = BeautifulSoup.BeautifulSoup(res.text, "lxml")
    
    titles_html = soup.select("h3.special > a")
    artists_html = soup.select("h3.special > strong")
    
    if src > "metacritic-ye2010":
        titles_html = soup.select("h3.special > a")
        artists_html = soup.select("h3.special > strong")
        
        td_ix = 3 if src > "metacritic-ye2014" else 2
        
        titles_html = titles_html + soup.find("table", {"class": "listtable"}).select("tr > td:nth-of-type(%d) > a" % td_ix)
        artists_html = artists_html + soup.find("table", {"class": "listtable"}).select("tr > td:nth-of-type(%d) > strong" % td_ix)
        
        titles = [title.text.lstrip().replace("\n", "") for title in titles_html]
        artists = [artist.text.lstrip().replace("\n", "") for artist in artists_html]
    else:
        titles_html = soup.select("td.title > a")
        artists_html = soup.select("td.title")
        
        titles = [title.text.lstrip().replace("\n", "") for title in titles_html]
        artists = [re.sub(r".*(\n +)?by ", "", text.text).lstrip().replace("\n", "") for text in artists_html]
    
    # confirm that there are an equal number of titles/ranks/artists (didn't miss anything)
    assert (40 == len(titles) or src == "metacritic-ye2009") and len(titles) == len(artists)
    
    dfs.append(pd.DataFrame({"rank": range(1, len(titles) + 1), "title": titles, "artist": artists, "src": src}))

# concat all lists together
df = pd.concat(dfs)

# get breakdown of albums per list to confirm successful
df.groupby("src").agg("count")

# save
df.to_csv("~/Desktop/Projects/album-sequence/data/raw/album-lists/metacritic-top-albums.txt", sep = "|", index = False)

