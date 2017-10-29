import time
import requests
from requests.auth import HTTPDigestAuth

import xbmcaddon
ADDON        = xbmcaddon.Addon()
useragent = '%s/%s (https://github.com/rolandmoser/service.rating.musicbrainz)' % (ADDON.getAddonInfo('id'), ADDON.getAddonInfo('version'))

# TODO: only sleep if less than 1 second passed since last request

def getAlbumRating(mbUrl, mbUser, mbPass, mbAlbumId):
    # Get album rating (MusicBrainz)
    url = "%s/ws/2/release/%s?inc=release-groups+user-ratings&fmt=json" % (mbUrl, mbAlbumId)
    time.sleep(2)
    resp = requests.get(url, auth=HTTPDigestAuth(mbUser, mbPass), headers={'User-Agent': useragent})
    if resp.status_code == 401:
        # TODO: throw
        return 0
    mbAlbum=resp.json()

    if ("release-group" in mbAlbum) and ("user-rating" in mbAlbum['release-group']) and ("value" in mbAlbum['release-group']['user-rating']) and (mbAlbum['release-group']['user-rating']['value'] is not None):
        return int(mbAlbum['release-group']['user-rating']['value']*2)

    return 0

def getSongRating(mbUrl, mbUser, mbPass, mbSongId):
    # Get song rating (MusicBrainz)
    url = "%s/ws/2/recording/%s?inc=user-ratings&fmt=json" % (mbUrl, mbSongId)
    time.sleep(2)
    resp = requests.get(url, auth=HTTPDigestAuth(mbUser, mbPass), headers={'User-Agent': useragent})
    if resp.status_code == 401:
        # TODO: throw
        return {}
    mbSong=resp.json()

    if ("user-rating" in mbSong) and ("value" in mbSong['user-rating']) and (mbSong['user-rating']['value'] is not None):
        return int(mbSong['user-rating']['value']*2)

    return 0

def getSongRatings(mbUrl, mbUser, mbPass, mbAlbumId):
    # Get all song ratings from an album (MusicBrainz)
    url = "%s/ws/2/recording/?release=%s&inc=user-ratings&fmt=json" % (mbUrl, mbAlbumId)
    time.sleep(2)
    resp = requests.get(url, auth=HTTPDigestAuth(mbUser, mbPass), headers={'User-Agent': useragent})
    if resp.status_code == 401:
        # TODO: throw
        return {}
    mbSongs=resp.json()

    ratingdict = {}
    if ("recordings" in mbSongs):
        for mbSong in mbSongs['recordings']:
            if ("id" in mbSong):
                if ("user-rating" in mbSong) and ("value" in mbSong['user-rating']) and (mbSong['user-rating']['value'] is not None):
                    ratingdict[mbSong['id']] = int(mbSong['user-rating']['value']*2)
                else:
                    ratingdict[mbSong['id']] = 0

    return ratingdict

