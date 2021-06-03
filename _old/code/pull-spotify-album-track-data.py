# -*- coding: utf-8 -*-

import os, json
from json.decoder import JSONDecodeError
import pandas as pd
import spotipy
import spotipy.util as util

# load simple de-duped albums from excel
# os.chdir("C:\\Users\\btanen\Desktop\\Projects\\album-sequence")
os.chdir("/Users/ben-tanen/Desktop/Projects/album-sequence/")
album_ids_df = pd.read_excel("data/deduped-album-list-with-ids.xlsx", sheet_name = "ids")

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

# pull in spotify album information and store track ids (to parse later)
albums    = [ ]
album_ids = album_ids_df['id'].tolist()

_album_tracks = [ ]

for ix in range(0, len(album_ids), 10):
    print("pulling data for album ids %d-%d" % (ix, ix + 9))
    
    # query 10 ids at a time
    ix_ids = album_ids[ix:ix+10]
    res = sp.albums(ix_ids)
    
    # parse out album information
    albums.extend([{'album_id': a['id'],
                    'name': a['name'],
                    'artist': '|'.join([artist['name'] for artist in a['artists']]),
                    'artist_id': '|'.join([artist['id'] for artist in a['artists']]),
                    'n_artists': len(a['artists']),
                    'n_tracks': a['total_tracks'],
                    'release_date': a['release_date'],
                    'popularity': a['popularity'],
                    'album_type': a['album_type']} for a in res['albums']])
    
    # parse out track information
    # store associated album_id
    _album_tracks.extend([a['tracks'] for a in res['albums']])
    list(map(lambda t, i: t.update({'album_id': i}), _album_tracks[-len(ix_ids):], ix_ids))

albums_df = pd.DataFrame(albums)

# since result tracks are limited to 50 results, 
# go back and get tracks for albums with >50 tracks
for ix in albums_df[albums_df['n_tracks'] > 50].index.tolist():
    extra_res = sp.next(_album_tracks[ix])
    _album_tracks[ix]['items'].extend(extra_res['items'])
    while extra_res['next']:
        extra_res = sp.next(extra_res)
        _album_tracks[ix]['items'].extend(extra_res['items']) 

# update track items to have album_id
for ts in _album_tracks:
    [t.update({'album_id': ts['album_id']}) for t in ts['items']]

# flatten list of track lists
album_tracks = [t for ts in [ts['items'] for ts in _album_tracks] for t in ts]

# confirm that pulled as many tracks as expected
assert len(album_tracks) == sum(albums_df['n_tracks'])

# get list of track_ids (need to pull information seperately to get popularity)
track_ids = [t['id'] for t in album_tracks]

# pull in spotify track information
tracks = [ ]
for ix in range(0, len(track_ids), 50):
    print("pulling data for tracks ids %d-%d" % (ix, ix + 49))
    
    # query 50 ids at a time
    ix_ids = track_ids[ix:ix+50]
    res = sp.tracks(ix_ids)
    
    # parse out album information
    tracks.extend([{'track_id': t['id'],
                    'name': t['name'],
                    'artist': '|'.join([artist['name'] for artist in t['artists']]),
                    'artist_id': '|'.join([artist['id'] for artist in t['artists']]),
                    'album': t['album']['name'],
                    'album_id': t['album']['id'],
                    'popularity': t['popularity'],
                    'duration_ms': t['duration_ms'],
                    'preview_url': t['preview_url'],
                    'track_number': t['track_number'],
                    'type': t['type']} for t in res['tracks']])

tracks_df = pd.DataFrame(tracks)

# confirm that pulled as many tracks as expected
assert len(tracks_df) == sum(albums_df['n_tracks'])

# save albums_df and tracks_df
albums_df.to_csv("data/all-albums-spotify-data.txt", sep = "|", index = False, encoding = "utf-8")
tracks_df.to_csv("data/all-tracks-spotify-data.txt", sep = "|", index = False, encoding = "utf-8")




