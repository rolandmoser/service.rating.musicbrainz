import xbmc
import json

def getAlbumRatings():
    json_query = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "AudioLibrary.GetAlbums", "params": { "properties": ["musicbrainzalbumid", "userrating", "displayartist"]}, "id": "libAlbums"}')
    json_response = json.loads(json_query)

    if ("result" in json_response) and ("albums" in json_response['result']):
        return json_response['result']['albums']
    else:
        return []

def getSongRatingsByAlbum(albumid):
    json_query = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "AudioLibrary.GetSongs", "params": { "filter": {"albumid": %d}, "properties": [ "albumid", "musicbrainztrackid", "userrating" ]}, "id": "libSongs"}' % (albumid))
    json_response = json.loads(json_query)

    if ("result" in json_response) and ("songs" in json_response['result']):
        return json_response['result']['songs']
    else:
        return None

def getSongsUnrated(songs):
    filteredList = []
    for song in songs:
        if song['userrating'] == 0:
            filteredList.append(song)

    return filteredList

def setSongRating(songid, newsonguserrating):
    json_query = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "id": 1, "method": "AudioLibrary.SetSongDetails", "params": {"songid" : %d, "userrating": %d}}' % (songid, newsonguserrating))

def setAlbumRating(albumid, newalbumuserrating):
    json_query = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "id": 1, "method": "AudioLibrary.SetAlbumDetails", "params": {"albumid" : %d, "userrating": %d}}' % (albumid, newalbumuserrating))

