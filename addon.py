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

# TODO update rating on server if changed locally
# TODO save to queue if submit of rating does not work
# TODO quit gracefully

def log(txt, level=xbmc.LOGDEBUG):
    if isinstance (txt,str):
        txt = txt.decode("utf-8")
    message = u'%s: %s' % (ADDONID, txt)
    xbmc.log(msg=message.encode("utf-8"), level=level)

class Main:
    def __init__(self, action):
        self._service_setup()
        if action == 'refreshAll':
            self.refresh_all()
        while (not self.Monitor.abortRequested()) and (not self.Exit):
            xbmc.sleep(1000)

    def _service_setup(self):
        self.MusicBrainzURL       = 'https://www.musicbrainz.org'
        self.fileQueue            = 'queue'
        self.Monitor              = MyMonitor(main = self)
        self.Exit                 = False
        self.get_settings()

    def get_settings(self):
        log('#DEBUG# reading settings')
        mbUser         = ADDON.getSetting('username').lower()
        mbPass         = ADDON.getSetting('password')
        mbAlbumRatings = ADDON.getSetting('albumRatings') == 'true'
        mbSongRatings  = ADDON.getSetting('songRatings') == 'true'

    def refresh_unrated(self):
        log('Rescan start')
        dialogprogress = xbmcgui.DialogProgressBG()
        dialogprogress.create(ADDONID + LANGUAGE(30004), "")
        dialogprogress.update(0, '%s' % (LANGUAGE(30005)))

        mbUrl          = self.MusicBrainzURL
        mbUser         = ADDON.getSetting('username').lower()
        mbPass         = ADDON.getSetting('password')
        mbAlbumRatings = ADDON.getSetting('albumRatings') == 'true'
        mbSongRatings  = ADDON.getSetting('songRatings') == 'true'
        mbWait         = 1

        try:
            log('%s, %s' % (mbAlbumRatings, mbSongRatings))
            if (not mbAlbumRatings) and (not mbSongRatings):
                return

            albumitems = database.getAlbumRatings()
            cnt = 0
            for albumitem in albumitems:
                albumid            = albumitem['albumid']
                musicbrainzalbumid = albumitem['musicbrainzalbumid']
                albumartist        = albumitem['displayartist']
                albumtitle         = albumitem['label']
                albumuserrating    = albumitem['userrating']

                dialogprogress.update((100*cnt)/len(albumitems), '%s: %s - %s' % (LANGUAGE(30005), albumartist, albumtitle))

                if mbAlbumRatings and musicbrainzalbumid <> '':
                    # Update album rating in Kodi
                    if albumuserrating == 0:
                        (newalbumuserrating, mbWait) = musicbrainz.getAlbumRating(mbUrl, mbWait, mbUser, mbPass, musicbrainzalbumid)
                        if albumuserrating <> newalbumuserrating:
                            log("Update album rating for %d from %d to %d" % (albumid, albumuserrating, newalbumuserrating))
                            database.setAlbumRating(albumid, newalbumuserrating)

                # Update song ratings in Kodi
                if mbSongRatings:
                    songitems = database.getSongRatingsByAlbum(albumid)
                    songitems = database.getSongsUnrated(songitems)
                    if songitems:
                        if musicbrainzalbumid <> '':
                            (songratings, mbWait) = musicbrainz.getSongRatingsByAlbum(mbUrl, mbWait, mbUser, mbPass, musicbrainzalbumid)
                        else:
                            songratings = {}

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

                cnt+=1
                dialogprogress.update((100*cnt)/len(albumitems))
        except musicbrainz.MusicbrainzException as error:
            log('Error: ' + repr(error), level=xbmc.LOGINFO)

        dialogprogress.close()
        log('Rescan done')

    def refresh_all(self):
        log('Full rescan start')
        dialogprogress = xbmcgui.DialogProgress()
        dialogprogress.create(ADDONID + LANGUAGE(30004), "")
        dialogprogress.update(0, '%s' % (LANGUAGE(30005)))

        mbUrl          = self.MusicBrainzURL
        mbUser         = ADDON.getSetting('username').lower()
        mbPass         = ADDON.getSetting('password')
        mbAlbumRatings = ADDON.getSetting('albumRatings') == 'true'
        mbSongRatings  = ADDON.getSetting('songRatings') == 'true'
        mbWait         = 1

	log('Password %s' % mbPass)

        try:
            log('%s, %s' % (mbAlbumRatings, mbSongRatings))
            if (not mbAlbumRatings) and (not mbSongRatings):
                return

            albumitems = database.getAlbumRatings()
            cnt = 0
            for albumitem in albumitems:
                albumid            = albumitem['albumid']
                musicbrainzalbumid = albumitem['musicbrainzalbumid']
                albumartist        = albumitem['displayartist']
                albumtitle         = albumitem['label']
                albumuserrating    = albumitem['userrating']

                dialogprogress.update((100*cnt)/len(albumitems), '%s: %s - %s' % (LANGUAGE(30005), albumartist, albumtitle))

                if mbAlbumRatings and musicbrainzalbumid <> '':
                    # Update album rating in Kodi
                    (newalbumuserrating, mbWait) = musicbrainz.getAlbumRating(mbUrl, mbWait, mbUser, mbPass, musicbrainzalbumid)
                    if albumuserrating <> newalbumuserrating:
                        log("Update album rating for %d from %d to %d" % (albumid, albumuserrating, newalbumuserrating))
                        database.setAlbumRating(albumid, newalbumuserrating)

                if dialogprogress.iscanceled():
                    break

                # Update song ratings in Kodi
                if mbSongRatings:
                    songitems = database.getSongRatingsByAlbum(albumid)
                    if musicbrainzalbumid <> '':
                        (songratings, mbWait) = musicbrainz.getSongRatingsByAlbum(mbUrl, mbWait, mbUser, mbPass, musicbrainzalbumid)
                    else:
                        songratings = {}

                    for songitem in songitems:
                        if dialogprogress.iscanceled():
                            break

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
                    cnt+=1
                    dialogprogress.update((100*cnt)/len(albumitems))

                if dialogprogress.iscanceled():
                    break

        except musicbrainz.MusicbrainzException as error:
            log('Error: ' + repr(error))

        dialogprogress.close()
        log('Full rescan done')

class MyMonitor(xbmc.Monitor):
    def __init__( self, *args, **kwargs ):
        xbmc.Monitor.__init__( self )
        self.main = kwargs['main']

    def onSettingsChanged(self):
        log('#DEBUG# onSettingsChanged')
        self.main.get_settings()

    def  onScanFinished(self, library):
        log('Finished Scan: %s' % (library))
        if library == 'music':
            self.main.refresh_unrated()
            

if ( __name__ == "__main__" ):
    log('script version %s started' % ADDONVERSION)
    if len(sys.argv) > 1:
        Main(sys.argv[1])
    else:
        Main(None)

    log('script stopped')

