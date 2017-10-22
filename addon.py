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

import urllib, urllib2, socket, hashlib, time
import json
import xbmc, xbmcgui, xbmcaddon

ADDON        = xbmcaddon.Addon()
ADDONID      = ADDON.getAddonInfo('id')
ADDONVERSION = ADDON.getAddonInfo('version')
LANGUAGE     = ADDON.getLocalizedString

# TODO query rating when song, album or artist is added
# TODO query periodically for updates on rating
# TODO update rating on server if changed locally, revert on fail.
# TODO save queue to file similar to lastfm if submit of rating does not work immediately

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
        self.MusicBrainzURL       = 'http://www.musicbrainz.org/'
        self.Monitor              = MyMonitor(action = self._get_settings)
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

if ( __name__ == "__main__" ):
    log('script version %s started' % ADDONVERSION)
    Main()

log('script stopped')

