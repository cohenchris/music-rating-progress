#!/bin/python3

from __future__ import division             # allows division to be float by default
import csv
from plexapi.myplex import MyPlexAccount
from plexapi.server import PlexServer
from pprint import pprint
import time

start_time = time.time()

baseurl = "http://192.168.24.3:32400"
token = ""

account = MyPlexAccount(token)
server = PlexServer(baseurl, token)

artists = server.library.section("Music").searchArtists()

artist_ratings = []

# For every artist in the library, check if all of their tracks on each album have been rated
for artist in artists:
    artist_rating = {"artistName": artist.title, "albums": []}
# Look through each album from the current artist
    for album in artist.albums():
        album_rating = {"albumName": album.title, "rated": True}

        # If, for any track on the album, there is no rating, the album has not been completed
        for tracks in album:
            for track in tracks:
                if track.userRating is None:
                    album_rating["rated"] = False

        # Append each album analysis to the album subarray
        artist_rating["albums"].append(album_rating)
    # Append each artist rating analysis to the master array
    artist_ratings.append(artist_rating)

headers = ["Artist", "Completeness"]
max_albums = len(max(artist_ratings, default=1, key=lambda x: len(x["albums"]))["albums"])

for i in range(1, max_albums + 1):
    headers.append(f"Album {i}")

# Create the overview .csv
with open("musicRatingProgress.csv", "w") as csvfile:
    filewriter = csv.writer(csvfile, delimiter=",", quoting=csv.QUOTE_ALL)
    filewriter.writerow(headers)

    total_albums = 0
    total_albums_rated = 0
    
    # Print albums/ratings for every artist
    for artist in artist_ratings:
        artist_rating_row = [artist["artistName"]]
        albums_rated = 0
        total_albums = total_albums + len(artist["albums"])
        for album in artist["albums"]:
            if album["rated"]:
                albums_rated = albums_rated + 1
                total_albums_rated = total_albums_rated + 1
            artist_rating_row.append(f"{album['albumName']} (rated = {str(album['rated'])})")
        percent_rated = f"{round(albums_rated/len(artist['albums']) * 100, 2)}% ({albums_rated}/{len(artist['albums'])})"
        artist_rating_row.insert(1, percent_rated)
        filewriter.writerow(artist_rating_row)

    filewriter.writerow(["TOTALS", f"{round(total_albums_rated/total_albums * 100, 2)}% ({total_albums_rated}/{total_albums})"])


print("--- %s seconds ---" % (time.time() - start_time))
