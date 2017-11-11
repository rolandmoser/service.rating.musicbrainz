# *  This Program is free software; you can redistribute it and/or modify
# *  it under the terms of the GNU General Public License as published by
# *  the Free Software Foundation; either version 2, or (at your option)
# *  any later version.
# *
# *  This Program is distributed in the hope that it will be useful,
# *  but WITHOUT ANY WARRANTY; without even the implied warranty of
# *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# *  GNU General Public License for more details.
# *
# *  You should have received a copy of the GNU General Public License
# *  along with Kodi; see the file COPYING.  If not, write to
# *  the Free Software Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.
# *  http://www.gnu.org/copyleft/gpl.html

import xbmc, xbmcgui, xbmcaddon
import time
import datetime

import musicbrainz
import database
import utils

ADDON        = xbmcaddon.Addon()
ADDONID      = ADDON.getAddonInfo('id')
ADDONVERSION = ADDON.getAddonInfo('version')
LANGUAGE     = ADDON.getLocalizedString

# TODO query rating when song, album or artist is added
# TODO query periodically for updates on rating (No)
# TODO update rating on server if changed locally, queue on fail.
# TODO save queue to file similar to lastfm addon if submit of rating does not work immediately
# TODO handle non album tracks
# TODO show progress when querying database and musicbrainz
# TODO check why some songs are not found in the musicbrainz.getSongRatingsByAlbum

def log(txt, level=xbmc.LOGDEBUG):
    if isinstance (txt,str):
        txt = txt.decode("utf-8")
    message = u'%s: %s' % (ADDONID, txt)
    xbmc.log(msg=message.encode("utf-8"), level=level)

class Main:
    def __init__(self, action):
        print action
        self._service_setup()
        if action == 'refreshAllRatings':
            try:
#                self._refresh_new()
                self._refresh_all_ratings()
            except musicbrainz.MusicbrainzException as error:
                log('Error: ' + repr(error))
            
        while (not self.Monitor.abortRequested()) and (not self.Exit):
            xbmc.sleep(1000)

    def _service_setup(self):
        self.MusicBrainzURL       = 'https://www.musicbrainz.org'
        self.fileLastScan         = 'lastscan'
        self.fileQueue            = 'queue'
        self.Monitor              = MyMonitor(action = self._get_settings)
        self.Exit                 = False
        self._get_settings()

    def _get_settings(self):
        log('#DEBUG# reading settings')
        mbUser        = ADDON.getSetting('username').lower()
        mbPass        = ADDON.getSetting('password')

    def _refresh_new(self):
        log('Rescan start')
        s = utils.read_file(self.fileLastScan)
        if not s:
            _refresh_all_ratings()
            return

        lastscan = utils.parseTime(s)

        mbUrl  = self.MusicBrainzURL
        mbUser = ADDON.getSetting('username').lower()
        mbPass = ADDON.getSetting('password')
        mbWait = 1

        albumitems = database.getAlbumRatings()
        for albumitem in albumitems:
            albumid            = albumitem['albumid']
            musicbrainzalbumid = albumitem['musicbrainzalbumid']
            albumtitle         = albumitem['label']
            albumuserrating    = albumitem['userrating']
            albumdateadded     = utils.parseTime(albumitem['dateadded'])

            # Update album rating in Kodi
            if albumdateadded >= lastscan:
                (newalbumuserrating, mbWait) = musicbrainz.getAlbumRating(mbUrl, mbWait, mbUser, mbPass, musicbrainzalbumid)
                if albumuserrating <> newalbumuserrating:
                    log("Update album rating for %d from %d to %d" % (albumid, albumuserrating, newalbumuserrating))
                    database.setAlbumRating(albumid, newalbumuserrating)

            # Update song ratings in Kodi
            songitems = database.getSongRatingsByAlbum(albumid)
            songitems = database.getSongsSince(songitems, lastscan)
            if songitems:
                (songratings, mbWait) = musicbrainz.getSongRatingsByAlbum(mbUrl, mbWait, mbUser, mbPass, musicbrainzalbumid)
                for songitem in songitems:
                    songid             = songitem['songid']
                    musicbrainztrackid = songitem['musicbrainztrackid']
                    songtitle          = songitem['label']
                    songuserrating     = songitem['userrating']

                    newsonguserrating = songratings.get(musicbrainztrackid, None)

                    if newsonguserrating == None:
                        log("Song (%s) not found in Album (%s)" % (songtitle, albumtitle))
                        (newsonguserrating, mbWait) = musicbrainz.getSongRating(mbUrl, mbWait, mbUser, mbPass, musicbrainztrackid)

                    if (newsonguserrating <> None) and (songuserrating <> newsonguserrating):
                        log("Update song rating for %d from %d to %d" % (songid, songuserrating, newsonguserrating))
                        database.setSongRating(songid, newsonguserrating)
        utils.write_file(self.fileLastScan, datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"))
        log('Rescan done')

    def _refresh_all_ratings(self):
        log('Full rescan start')
        mbUrl  = self.MusicBrainzURL
        mbUser = ADDON.getSetting('username').lower()
        mbPass = ADDON.getSetting('password')
        mbWait = 1

        albumitems = database.getAlbumRatings()
        for albumitem in albumitems:
            albumid            = albumitem['albumid']
            musicbrainzalbumid = albumitem['musicbrainzalbumid']
            albumtitle         = albumitem['label']
            albumuserrating    = albumitem['userrating']

            # Update album rating in Kodi
            (newalbumuserrating, mbWait) = musicbrainz.getAlbumRating(mbUrl, mbWait, mbUser, mbPass, musicbrainzalbumid)
            if albumuserrating <> newalbumuserrating:
                log("Update album rating for %d from %d to %d" % (albumid, albumuserrating, newalbumuserrating))
                database.setAlbumRating(albumid, newalbumuserrating)

            # Update song ratings in Kodi
            songitems = database.getSongRatingsByAlbum(albumid)
            (songratings, mbWait) = musicbrainz.getSongRatingsByAlbum(mbUrl, mbWait, mbUser, mbPass, musicbrainzalbumid)
            for songitem in songitems:
                songid             = songitem['songid']
                musicbrainztrackid = songitem['musicbrainztrackid']
                songtitle          = songitem['label']
                songuserrating     = songitem['userrating']

                newsonguserrating = songratings.get(musicbrainztrackid, None)

                if newsonguserrating == None:
                    log("Song (%s) not found in Album (%s)" % (songtitle, albumtitle))
                    (newsonguserrating, mbWait) = musicbrainz.getSongRating(mbUrl, mbWait, mbUser, mbPass, musicbrainztrackid)

                if (newsonguserrating <> None) and (songuserrating <> newsonguserrating):
                    log("Update song rating for %d from %d to %d" % (songid, songuserrating, newsonguserrating))
                    database.setSongRating(songid, newsonguserrating)
        utils.write_file(self.fileLastScan, datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"))
        log('Full rescan done')

class MyMonitor(xbmc.Monitor):
    def __init__( self, *args, **kwargs ):
        xbmc.Monitor.__init__( self )
        self.action = kwargs['action']

    def onSettingsChanged(self):
        log('#DEBUG# onSettingsChanged')
        self.action()

if ( __name__ == "__main__" ):
    log('script version %s started' % ADDONVERSION)
    if len(sys.argv) > 1:
        Main(sys.argv[1])
    else:
        Main(None)

    log('script stopped')

