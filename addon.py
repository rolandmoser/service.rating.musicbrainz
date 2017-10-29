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

import musicbrainz
import database

ADDON        = xbmcaddon.Addon()
ADDONID      = ADDON.getAddonInfo('id')
ADDONVERSION = ADDON.getAddonInfo('version')
LANGUAGE     = ADDON.getLocalizedString

# TODO query rating when song, album or artist is added
# TODO query periodically for updates on rating (No)
# TODO update rating on server if changed locally, revert on fail.
# TODO save queue to file similar to lastfm if submit of rating does not work immediately
# TODO handle non album tracks
# TODO show progress when querying database and musicbrainz

def log(txt):
    if isinstance (txt,str):
        txt = txt.decode("utf-8")
    message = u'%s: %s' % (ADDONID, txt)
    xbmc.log(msg=message.encode("utf-8"), level=xbmc.LOGDEBUG)

class Main:
    def __init__( self ):
        self._service_setup()
        while (not self.Monitor.abortRequested()) and (not self.Exit):
            xbmc.sleep(1000)

    def _service_setup( self ):
        self.MusicBrainzURL       = 'https://www.musicbrainz.org/'
        self.Monitor              = MyMonitor(action = self._get_settings)
        self.Exit                 = False
        self._get_settings()

    def _get_settings( self ):
        log('#DEBUG# reading settings')
        mbUser        = ADDON.getSetting('mbuser').lower()
        mbPass        = ADDON.getSetting('mbpass')

class MyMonitor(xbmc.Monitor):
    def __init__( self, *args, **kwargs ):
        xbmc.Monitor.__init__( self )
        self.action = kwargs['action']

    def onSettingsChanged( self ):
        log('#DEBUG# onSettingsChanged')
        self.action()

def refreshAllRatings():
    #TODO user and password
    mbUrl  = "https://musicbrainz.org"
    mbUser = "TBD"
    mbPass = "TBD"
    number=25
    dateadded="2017-10-14 10:59:13"

    albumitems = database.getAlbumRatings()
    for albumitem in albumitems:
        albumid            = albumitem['albumid']
        musicbrainzalbumid = albumitem['musicbrainzalbumid']
        albumtitle         = albumitem['label']
        albumuserrating    = albumitem['userrating']

        # Update album rating in Kodi
        newalbumuserrating = musicbrainz.getAlbumRating(mbUrl, mbUser, mbPass, musicbrainzalbumid)
        if albumuserrating <> newalbumuserrating:
            log("Update album rating for %d from %d to %d" % (albumid, albumuserrating, newalbumuserrating))
            database.setAlbumRating(albumid, newalbumuserrating)

        # Update song ratings in Kodi
        songitems = database.getSongRatingsByAlbum(albumid)
        songratings = musicbrainz.getSongRatings(mbUrl, mbUser, mbPass, musicbrainzalbumid)
        for songitem in songitems:
            songid             = songitem['songid']
            musicbrainztrackid = songitem['musicbrainztrackid']
            songtitle          = songitem['label']
            songuserrating     = songitem['userrating']

            newsonguserrating = songratings.get(musicbrainztrackid, None)

            if newsonguserrating == None:
                log("Song (%s) not found in Album (%s)" % (songtitle, albumtitle))
                newsonguserrating = musicbrainz.getSongRating(mbUrl, mbUser, mbPass, musicbrainztrackid)

            if (newsonguserrating <> None) and (songuserrating <> newsonguserrating):
                log("Update song rating for %d from %d to %d" % (songid, songuserrating, newsonguserrating))
                database.setSongRating(songid, newsonguserrating)

if ( __name__ == "__main__" ):
    if len(sys.argv) > 1 and sys.argv[1] == 'refreshAllRatings':
        refreshAllRatings()
    else:
        log('script version %s started' % ADDONVERSION)

        Main()

        log('script stopped')

