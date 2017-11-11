import xbmc
import json

import utils

def getAlbumRatings():
    json_query = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "AudioLibrary.GetAlbums", "params": { "properties": ["musicbrainzalbumid", "userrating", "dateadded"]}, "id": "libAlbums"}')
    json_response = json.loads(json_query)

    if ("result" in json_response) and ("albums" in json_response['result']):
        return json_response['result']['albums']
    else:
        return []

#def getAlbumsSince(albums, date):
#    filteredList = []
#    for album in albums:
#        if album["dateadded"] >= date:
#            filteredList.add(album)
#    return filteredList

def getSongRatingsByAlbum(albumid):
    json_query = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "AudioLibrary.GetSongs", "params": { "filter": {"albumid": %d}, "properties": [ "albumid", "musicbrainztrackid", "userrating", "dateadded" ]}, "id": "libSongs"}' % (albumid))
    json_response = json.loads(json_query)

    if ("result" in json_response) and ("songs" in json_response['result']):
        return json_response['result']['songs']
    else:
        return None

def getSongsSince(songs, date):
    filteredList = []
    for song in songs:
        if utils.parseTime(song['dateadded']) >= date:
            filteredList.add(song)

    return filteredList

def setSongRating(songid, newsonguserrating):
    json_query = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "id": 1, "method": "AudioLibrary.SetSongDetails", "params": {"songid" : %d, "userrating": %d}}' % (songid, newsonguserrating))

def setAlbumRating(albumid, newalbumuserrating):
    json_query = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "id": 1, "method": "AudioLibrary.SetAlbumDetails", "params": {"albumid" : %d, "userrating": %d}}' % (albumid, newalbumuserrating))

