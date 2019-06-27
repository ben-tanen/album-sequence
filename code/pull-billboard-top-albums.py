# -*- coding: utf-8 -*-

import requests
import bs4 as BeautifulSoup
import pandas as pd

# define the billboard urls to pull from
urls = ["https://www.billboard.com/charts/year-end/%d/top-billboard-200-albums" % year for year in range(2002, 2019)]
urls = urls + ["https://www.billboard.com/charts/greatest-billboard-200-albums"]

# define src names for each source
srcs = ["billboard-ye%d" % year for year in range(2002, 2019)] + ["billboard-greatest200"]

# create empty list to store each list's df
dfs = [ ]

# for each list, parse out each items rank/title/artist and store in df
for i in range(len(urls)):
    url = urls[i]
    src = srcs[i]    
    print("%s -- %s" % (src, url))
        
    res = requests.get(url)
    soup = BeautifulSoup.BeautifulSoup(res.text, "lxml")
    
    if (src == "billboard-greatest200"):
        ranks_html = soup.find_all("div", {"class": "chart-list-item__rank"})
        titles_html = soup.find_all("span", {"class": "chart-list-item__title-text"})
        artists_html = soup.find_all("div", {"class": "chart-list-item__artist"})  
    else:
        ranks_html = soup.find_all("div", {"class": "ye-chart-item__rank"})
        titles_html = soup.find_all("div", {"class": "ye-chart-item__title"})
        artists_html = soup.find_all("div", {"class": "ye-chart-item__artist"})
    
    ranks = [rank.text.lstrip().replace("\n", "").replace(" ", "") for rank in ranks_html]
    titles = [title.text.lstrip().replace("\n", "") for title in titles_html]
    artists = [artist.text.lstrip().replace("\n", "") for artist in artists_html]
    
    # confirm that there are an equal number of titles/ranks/artists (didn't miss anything)
    assert len(ranks) == len(titles) and len(titles) == len(artists)
    
    dfs.append(pd.DataFrame({"rank": ranks, "title": titles, "artist": artists, "src": src}))

# concat all lists together
df = pd.concat(dfs)

# get breakdown of albums per list to confirm successful
df.groupby("src").agg("count")

# save
df.to_csv("~/Desktop/Projects/album-sequence/data/raw/album-lists/billboard-top-albums.txt", sep = "|", index = False)

