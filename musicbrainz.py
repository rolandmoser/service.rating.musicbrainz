import time
import requests
from requests.auth import HTTPDigestAuth

import xbmcaddon
ADDON        = xbmcaddon.Addon()
useragent    = '%s/%s (https://github.com/rolandmoser/service.rating.musicbrainz)' % (ADDON.getAddonInfo('id'), ADDON.getAddonInfo('version'))

class MusicbrainzException(Exception):
    pass

def getAlbumRating(mbUrl, mbWait, mbUser, mbPass, mbAlbumId):
    # Get album rating (MusicBrainz)
    url = "%s/ws/2/release/%s?inc=release-groups+user-ratings&fmt=json" % (mbUrl, mbAlbumId)

    while mbWait < 10:
        time.sleep(mbWait)
        resp = requests.get(url, auth=HTTPDigestAuth(mbUser, mbPass), headers={'User-Agent': useragent})
        if resp.status_code == 503:
            mbWait+=1
            continue
        if resp.status_code == 401:
            raise MusicbrainzException('Unauthorized')

        mbAlbum=resp.json()

        if ("release-group" in mbAlbum) and ("user-rating" in mbAlbum['release-group']) and ("value" in mbAlbum['release-group']['user-rating']) and (mbAlbum['release-group']['user-rating']['value'] is not None):
            return (int(mbAlbum['release-group']['user-rating']['value']*2), mbWait)

        return (0, mbWait)

    raise MusicbrainzException('Throttling failed')

def getSongRating(mbUrl, mbWait, mbUser, mbPass, mbSongId):
    # Get song rating (MusicBrainz)
    url = "%s/ws/2/recording/%s?inc=user-ratings&fmt=json" % (mbUrl, mbSongId)

    while mbWait < 10:
        time.sleep(mbWait)
        resp = requests.get(url, auth=HTTPDigestAuth(mbUser, mbPass), headers={'User-Agent': useragent})
        if resp.status_code == 503:
            mbWait+=1
            continue
        if resp.status_code == 401:
            raise MusicbrainzException('Unauthorized')

        mbSong=resp.json()

        if ("user-rating" in mbSong) and ("value" in mbSong['user-rating']) and (mbSong['user-rating']['value'] is not None):
            return (int(mbSong['user-rating']['value']*2), mbWait)

        return (0, mbWait)

    raise MusicbrainzException('Throttling failed')

def getSongRatingsByAlbum(mbUrl, mbWait, mbUser, mbPass, mbAlbumId):
    offset=0
    limit=100

    ratingdict = {}
    while True:
        (ratingdict2, mbWait, count) = getSongRatingsByAlbumPart(mbUrl, mbWait, mbUser, mbPass, mbAlbumId, offset, limit)
        ratingdict.update(ratingdict2)
        offset+=limit
        if offset > count:
            return (ratingdict, mbWait)

def getSongRatingsByAlbumPart(mbUrl, mbWait, mbUser, mbPass, mbAlbumId, offset, limit):
    # Get all song ratings from an album (MusicBrainz)
    url = "%s/ws/2/recording/?release=%s&offset=%d&limit=%d&inc=user-ratings&fmt=json" % (mbUrl, mbAlbumId, offset, limit)

    while mbWait < 10:
        time.sleep(mbWait)
        resp = requests.get(url, auth=HTTPDigestAuth(mbUser, mbPass), headers={'User-Agent': useragent})
        if resp.status_code == 503:
            mbWait+=1
            continue
        if resp.status_code == 401:
            raise MusicbrainzException('Unauthorized')

        mbSongs=resp.json()

        if ("recording-count" in mbSongs):
            count=int(mbSongs['recording-count'])
        else:
            count=limit

        ratingdict = {}
        if ("recordings" in mbSongs):
            for mbSong in mbSongs['recordings']:
                if ("id" in mbSong):
                    if ("user-rating" in mbSong) and ("value" in mbSong['user-rating']) and (mbSong['user-rating']['value'] is not None):
                        ratingdict[mbSong['id']] = int(mbSong['user-rating']['value']*2)
                    else:
                        ratingdict[mbSong['id']] = 0

        return (ratingdict, mbWait, count)

    raise MusicbrainzException('Throttling failed')

