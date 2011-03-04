#   This file is part of Indexor.
#
#    Indexor is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Indexor is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Indexor.  If not, see <http://www.gnu.org/licenses/>.

"""Module for the handling of settings

This module consists of two classses: one is the Settings class, which stores
all the settings (no pun intended). The other is the loader, which manages the
saving and restoring of the Settings object. This is because a class cannot
pickle itself and keep a reference to it, without having the fabric of space
time continuum bend and break (at least in my space time continuum :-p).
If SETTSFILE does not exist, it will be created. Beware that settings changes
between versions can render the SETTSFILE obsolete, because Pickle is used
to store it. If such is the case, a simple removing of the directory where
the HOMEDIR variable points to, should suffice.
"""

import os
import cPickle as pickle
import pango

HOMEDIR = os.path.expanduser("~") + "/.indexor"
SETTSFILE = HOMEDIR + "/settings"
CATALOGDIR = HOMEDIR + "/catalogs/"

class SettingsLoader(object):

    """Class that loads and saves the settings"""

    def __init__(self):
        self._settings = Settings()
        if os.path.exists(HOMEDIR) and os.path.exists(SETTSFILE):
            self._load_settings()
        else:
            try:
                os.mkdir(HOMEDIR, 0700)
                settsfile = open(SETTSFILE, "w")
                settsfile.close()
            except Exception as exc:
                print exc
            self._load_default_settings()
        if not os.path.exists(CATALOGDIR):
            try:
                os.mkdir(CATALOGDIR, 0700)
            except Exception as exc:
                print exc


    #################################
    #Properties
    #################################  
    def get_settings(self):
        """Property"""
        return self._settings

    settings = property(get_settings)

    #################################
    #Methods
    #################################
    def save_settings(self):
        """Save settings to disk"""
        self._settsfile = open(SETTSFILE, "w")
        pickle.dump(self._settings, self._settsfile, pickle.HIGHEST_PROTOCOL)
        self._settsfile.close()

    def _load_settings(self):
        """Load settings from disk"""
        self._settsfile = open(SETTSFILE, "r")
        self._settings = pickle.load(self._settsfile)
        self._settsfile.close()

    def _load_default_settings(self):
        """Create a settings object with default settings, and save it"""
        self._settings.load_default_settings()
        self.save_settings()


class Settings(object):

    """Class that keeps track of all settings in a program instance"""

    def __init__(self):
        pass

    #################################
    #Properties
    #################################
    #Filters
    def get_gnuhidden(self):
        """Property"""
        return self._gnuhidden

    def set_gnuhidden(self, gnuhidden):
        """Property"""
        self._gnuhidden = gnuhidden

    def get_savebackup(self):
        """Property"""
        return self._savebackup

    def set_savebackup(self, savebackup):
        """Property"""
        self._savebackup = savebackup

    gnuhidden = property(get_gnuhidden, set_gnuhidden)
    savebackup = property(get_savebackup, set_savebackup)

    #Logs
    def get_debug(self):
        """Property"""
        return self._debug

    def set_debug(self, debug):
        """Property"""
        self._debug = debug

    def get_missingmime(self):
        """Property"""
        return self._missingmime

    def set_missingmime(self, missingmime):
        """Property"""
        self._missingmime = missingmime

    def get_ioerror(self):
        """Property"""
        return self._ioerror

    def set_ioerror(self, ioerror):
        """Property"""
        self._ioerror = ioerror

    def get_metadataerror(self):
        """Property"""
        return self._metadataerror

    def set_metadataerror(self, metadataerror):
        """Property"""
        self._metadataerror = metadataerror

    def get_missingicon(self):
        """Property"""
        return self._missingicon

    def set_missingicon(self, missingicon):
        """Property"""
        self._missingicon = missingicon

    def get_thumberror(self):
        """Property"""
        return self._thumberror

    def set_thumberror(self, thumberror):
        """Property"""
        self._thumberror = thumberror

    debug = property(get_debug, set_debug)
    missingmime = property(get_missingmime, set_missingmime)
    ioerror = property(get_ioerror, set_ioerror)
    metadataerror = property(get_metadataerror, set_metadataerror)
    missingicon = property(get_missingicon, set_missingicon)
    thumberror = property(get_thumberror, set_thumberror)

    #Window
    def get_windowmax(self):
        """Property"""
        return self._windowmax

    def set_windowmax(self, windowmax):
        """Property"""
        self._windowmax = windowmax

    def get_windowsize(self):
        """Property"""
        return self._windowsize

    def set_windowsize(self, windowsize):
        """Property"""
        self._windowsize = windowsize

    def get_logwindowmax(self):
        """Property"""
        return self._logwindowmax

    def set_logwindowmax(self, logwindowmax):
        """Property"""
        self._logwindowmax = logwindowmax

    def get_logwindowsize(self):
        """Property"""
        return self._logwindowsize

    def set_logwindowsize(self, logwindowsize):
        """Property"""
        self._logwindowsize = logwindowsize

    def get_infopanesize(self):
        """Property"""
        return self._infopanesize

    def set_infopanesize(self, infopanesize):
        """Property"""
        self._infopanesize = infopanesize

    windowmax = property(get_windowmax, set_windowmax)
    windowsize = property(get_windowsize, set_windowsize)
    logwindowmax = property(get_logwindowmax, set_logwindowmax)
    logwindowsize = property(get_logwindowsize, set_logwindowsize)
    infopanesize = property(get_infopanesize, set_infopanesize)

    #Interface
    def get_iconlistsize(self):
        """Property"""
        return self._iconlistsize

    def set_iconlistsize(self, iconlistsize):
        """Property"""
        self._iconlistsize = iconlistsize

    def get_iconpanesize(self):
        """Property"""
        return self._iconpanesize

    def set_iconpanesize(self, iconpanesize):
        """Property"""
        self._iconpanesize = iconpanesize

    def get_thumblistsize(self):
        """Property"""
        return self._thumblistsize

    def set_thumblistsize(self, thumblistsize):
        """Property"""
        self._thumblistsize = thumblistsize

    def get_thumbpanesize(self):
        """Property"""
        return self._thumbpanesize

    def set_thumbpanesize(self, thumbpanesize):
        """Property"""
        self._thumbpanesize = thumbpanesize

    def get_geninfo(self):
        """Property"""
        return self._geninfo

    def set_geninfo(self, geninfo):
        """Property"""
        self._geninfo = geninfo

    def get_abspath(self):
        """Property"""
        return self._abspath

    def set_abspath(self, abspath):
        """Property"""
        self._abspath = abspath

    def get_relpath(self):
        """Property"""
        return self._relpath

    def set_relpath(self, relpath):
        """Property"""
        self._relpath = relpath

    def get_size(self):
        """Property"""
        return self._size

    def set_size(self, size):
        """Property"""
        self._size = size

    def get_mime(self):
        """Property"""
        return self._mime

    def set_mime(self, mime):
        """Property"""
        self._mime = mime

    def get_atime(self):
        """Property"""
        return self._atime

    def set_atime(self, atime):
        """Property"""
        self._atime = atime

    def get_mtime(self):
        """Property"""
        return self._mtime

    def set_mtime(self, mtime):
        """Property"""
        self._mtime = mtime

    def get_mediainfo(self):
        """Property"""
        return self._tblmediainfo

    def set_mediainfo(self, value):
        """Property"""
        self._tblmediainfo = value

    def get_medialength(self):
        """Property"""
        return self._medialength

    def set_medialength(self, value):
        """Property"""
        self._medialength = value

    def get_videoinfo(self):
        """Property"""
        return self._tblvideoinfo

    def set_videoinfo(self, videoinfo):
        """Property"""
        self._tblvideoinfo = videoinfo

    def get_videocodec(self):
        """Property"""
        return self._videocodec

    def set_videocodec(self, value):
        """Property"""
        self._videocodec = value

    def get_videobitrate(self):
        """Property"""
        return self._videobitrate

    def set_videobitrate(self, videobitrate):
        """Property"""
        self._videobitrate = videobitrate

    def get_videores(self):
        """Property"""
        return self._videores

    def set_videores(self, value):
        """Property"""
        self._videores = value

    def get_videofps(self):
        """Property"""
        return self._videofps

    def set_videofps(self, value):
        """Property"""
        self._videofps = value

    def get_videoar(self):
        """Property"""
        return self._videoar

    def set_videoar(self, value):
        """Property"""
        self._videoar = value

    def get_audioinfo(self):
        """Property"""
        return self._tblaudioinfo

    def set_audioinfo(self, value):
        """Property"""
        self._tblaudioinfo = value

    def get_audiobitrate(self):
        """Property"""
        return self._audiobitrate

    def set_audiobitrate(self, value):
        """Property"""
        self._audiobitrate = value

    def get_audiosample(self):
        """Property"""
        return self._audiosample

    def set_audiosample(self, value):
        """Property"""
        self._audiosample = value

    def get_audiocodec(self):
        """Property"""
        return self._audiocodec

    def set_audiocodec(self, value):
        """Property"""
        self._audiocodec = value

    def get_audiochan(self):
        """Property"""
        return self._audiochan

    def set_audiochan(self, value):
        """Property"""
        self._audiochan = value

    def get_subinfo(self):
        """Property"""
        return self._tblsubinfo

    def set_subinfo(self, value):
        """Property"""
        self._tblsubinfo = value

    def get_sublangs(self):
        """Property"""
        return self._sublangs

    def set_sublangs(self, value):
        """Property"""
        self._sublangs = value

    def get_imginfo(self):
        """Property"""
        return self._tblimginfo

    def set_imginfo(self, value):
        """Property"""
        self._tblimginfo = value

    def get_imgres(self):
        """Property"""
        return self._imgres

    def set_imgres(self, value):
        """Property"""
        self._imgres = value

    def get_imgdate(self):
        """Property"""
        return self._imgdate

    def set_imgdate(self, value):
        """Property"""
        self._imgdate = value

    def get_imgauthor(self):
        """Property"""
        return self._imgauthor

    def set_imgauthor(self, value):
        """Property"""
        self._imgauthor = value

    def get_imgsoft(self):
        """Property"""
        return self._imgsoft

    def set_imgsoft(self, value):
        """Property"""
        self._imgsoft = value

    iconlistsize = property(get_iconlistsize, set_iconlistsize)
    iconpanesize = property(get_iconpanesize, set_iconpanesize)
    thumblistsize = property(get_thumblistsize, set_thumblistsize)
    thumbpanesize = property(get_thumbpanesize, set_thumbpanesize)
    geninfo = property(get_geninfo, set_geninfo)
    abspath = property(get_abspath, set_abspath)
    relpath = property(get_relpath, set_relpath)
    size = property(get_size, set_size)
    mime = property(get_mime, set_mime)
    atime = property(get_atime, set_atime)
    mtime = property(get_mtime, set_mtime)
    mediainfo = property(get_mediainfo, set_mediainfo)
    medialength = property(get_medialength, set_medialength)
    videoinfo = property(get_videoinfo, set_videoinfo)
    videocodec = property(get_videocodec, set_videocodec)
    videobitrate = property(get_videobitrate, set_videobitrate)
    videores = property(get_videores, set_videores)
    videofps = property(get_videofps, set_videofps)
    videoar = property(get_videoar, set_videoar)
    audioinfo = property(get_audioinfo, set_audioinfo)
    audiobitrate = property(get_audiobitrate, set_audiobitrate)
    audiosample = property(get_audiosample, set_audiosample)
    audiocodec = property(get_audiocodec, set_audiocodec)
    audiochan = property(get_audiochan, set_audiochan)
    subinfo = property(get_subinfo, set_subinfo)
    sublangs = property(get_sublangs, set_sublangs)
    imginfo = property(get_imginfo, set_imginfo)
    imgres = property(get_imgres, set_imgres)
    imgdate = property(get_imgdate, set_imgdate)
    imgauthor = property(get_imgauthor, set_imgauthor)
    imgsoft = property(get_imgsoft, set_imgsoft)

    #Tabs
    def get_tabellipsize(self):
        return self._tabellipsize

    def set_tabellipsize(self, value):
        self._tabellipsize = value

    def get_tablength(self):
        return self._tablength

    def set_tablength(self, value):
        self._tablength = value

    def get_tabellipplace(self):
        return self._tabellipplace

    def set_tabellipplace(self, value):
        self._tabellipplace = value

    tabellipsize = property(get_tabellipsize, set_tabellipsize)
    tablength = property(get_tablength, set_tablength)
    tabellipplace = property(get_tabellipplace, set_tabellipplace)

    def load_default_settings(self):
        """Load default settings (cuac)"""
        #Window size/state
        self._windowmax = False
        self._windowsize = (1000, 600)
        self._logwindowmax = False
        self._logwindowsize = (960, 500)
        self._infopanesize = 500

        #Icon/thumb size
        self._iconlistsize = 32
        self._iconpanesize = 64
        self._thumblistsize = 64
        self._thumbpanesize = 128

        #Info pane attrs.
        self._geninfo = True
        self._abspath = True
        self._relpath = True
        self._size = True
        self._mime = True
        self._atime = True
        self._mtime = True
        self._tblmediainfo = True
        self._medialength = True
        self._tblvideoinfo = True
        self._videocodec = True
        self._videobitrate = True
        self._videores = True
        self._videofps = True
        self._videoar = True
        self._tblaudioinfo = True
        self._audiobitrate = True
        self._audiosample = True
        self._audiocodec = True
        self._audiochan = True
        self._tblsubinfo = True
        self._sublangs = True
        self._tblimginfo = True
        self._imgres = True
        self._imgdate = True
        self._imgauthor = True
        self._imgsoft = True

        #Events
        self._debug = False
        self._missingmime = True
        self._ioerror = True
        self._metadataerror = True
        self._missingicon = True
        self._thumberror = True

        #Filters
        self._gnuhidden = True
        self._savebackup = True

        #Tabs
        self._tabellipsize = True
        self._tablength = 30
        self._tabellipplace = pango.ELLIPSIZE_MIDDLE
