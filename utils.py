import os, datetime, time
import xbmc, xbmcaddon, xbmcvfs

DATAPATH     = xbmc.translatePath(xbmcaddon.Addon().getAddonInfo('profile')).decode('utf-8')

def write_file( item, data ):
    # create the data dir if needed
    if not xbmcvfs.exists( DATAPATH ):
        xbmcvfs.mkdir( DATAPATH )
    # save data to file
    queue_file = os.path.join(DATAPATH, item)
    f = open(queue_file, 'w')
    f.write(repr(data))
    f.close()

def read_file( item ):
    # read the queue file if we have one
    path = os.path.join(DATAPATH, item)
    if xbmcvfs.exists( path ):
        f = open(path, 'r')
        data =  f.read()
        if data:
            data = eval(data)
        f.close()
        return data
    else:
        return None

def parseTime(s):
    # Workaround for Type error: https://bugs.python.org/issue27400
    try:
        return datetime.datetime.strptime(s, "%Y-%m-%d %H:%M:%S")
    except TypeError:
        return datetime.datetime(*(time.strptime(s, "%Y-%m-%d %H:%M:%S")[0:6]))

