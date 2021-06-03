# -*- coding: utf-8 -*-

import os, json
from json.decoder import JSONDecodeError
import pandas as pd
import spotipy
import spotipy.util as util

# load simple de-duped albums from excel
# os.chdir("C:\\Users\\btanen\Desktop\\Projects\\album-sequence")
os.chdir("/Users/ben-tanen/Desktop/Projects/album-sequence/")
albums_df = pd.read_excel("data/deduped-album-list.xlsx", sheet_name = "deduped", 
                          index_col = None, usecols = [0, 1], skiprows = 0)

# load in api keys
apikeys = json.load(open("data/api-keys.json"))

# init API for Spotify
os.environ["SPOTIPY_CLIENT_ID"]     = apikeys["spotipy_client_id"]
os.environ["SPOTIPY_CLIENT_SECRET"] = apikeys["spotipy_client_secret"]
os.environ["SPOTIPY_REDIRECT_URI"]  = apikeys["redirect_url"]

user_id = '129874447'

try:
    token = util.prompt_for_user_token(username = user_id)
except (AttributeError, JSONDecodeError):
    os.remove(f".cache-{user_id}")
    token = util.prompt_for_user_token(username = user_id)
sp = spotipy.Spotify(auth = token)

# for each album, search for name + artist, put results into DF
albums = [ ]
for ix, row in albums_df.iterrows():    
    q_artist = row['artist']
    q_title = row['title']    
    print("%s -- %s" % (q_artist, q_title))

    res = sp.search(q = "artist:%s album:%s" % (q_artist, q_title), type = "album", limit = 25)['albums']
    res_albums = res['items']
    while res['next']:
        res = sp.next(res)['albums']
        res_albums.extend(res['items'])
        
    albums.extend([{'query_artist': q_artist,
                    'query_title': q_title,
                    'id': a['id'],
                    'name': a['name'],
                    'artist': '|'.join([artist['name'] for artist in a['artists']]),
                    'artist_id': '|'.join([artist['id'] for artist in a['artists']]),
                    'n_artists': len(a['artists']),
                    'type': a['type'],
                    'release_date': a['release_date'], 
                    'total_tracks': a['total_tracks']} for a in res_albums])

spotify_albums_df = pd.DataFrame(albums)

# for each identified album, pull in the popularity and take the most popular when there are multiple matches
spotify_album_ids = list(set(spotify_albums_df['id'].tolist()))
spotify_albums_pop = [ ]
for ix in range(0, len(spotify_album_ids), 10):
    print("ids %d-%d" % (ix, ix + 9))
    res = sp.albums(spotify_album_ids[ix:ix+10])
    assert len(res['albums']) == 10 or ix + 10 > len(spotify_album_ids)
    spotify_albums_pop.extend([{'id': a['id'], 'popularity': a['popularity']} for a in res['albums']])
    
spotify_albums_df = spotify_albums_df.merge(pd.DataFrame(spotify_albums_pop), how = 'left', on = 'id')

# found XXX matches for YYY albums
print("found %d matches for %d albums" % (len(spotify_albums_df), 
                                          len(spotify_albums_df[['query_artist', 'query_title']].drop_duplicates())))

# export to identify correct match among duplicates
spotify_albums_df.to_csv("data/raw/full-spotify-album-id-matches.txt", sep = "|", index = False)



