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

import os
import cPickle as pickle

HOMEDIR = os.path.expanduser("~") + "/.indexor"
SETTSFILE = HOMEDIR + "/settings"

class SettingsLoader(object):
    
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
         
    def get_settings(self):
        return self._settings

    settings = property(get_settings)
    
    def save_settings(self):
        self._settsfile = open(SETTSFILE, "w")
        pickle.dump(self._settings, self._settsfile, pickle.HIGHEST_PROTOCOL)
        self._settsfile.close()
           
    def _load_settings(self):
        self._settsfile = open(SETTSFILE, "r")
        self._settings = pickle.load(self._settsfile)
        self._settsfile.close()

    def _load_default_settings(self):
        self._settings.load_default_settings()
        self.save_settings()

    
class Settings(object):

    
    def __init__(self):
        pass



    #################################
    #Properties
    #################################
    #Filters
    def get_gnuhidden(self):
        return self._gnuhidden
    
    def set_gnuhidden(self, gnuhidden):
        self._gnuhidden = gnuhidden
        
    def get_savebackup(self):
        return self._savebackup
    
    def set_savebackup(self, savebackup):
        self._savebackup = savebackup
    
    gnuhidden = property(get_gnuhidden, set_gnuhidden)
    savebackup = property(get_savebackup, set_savebackup)
    
    #Logs
    def get_missingmime(self):
        return self._missingmime
    
    def set_missingmime(self, missingmime):
        self._missingmime = missingmime
        
    def get_ioerror(self):
        return self._ioerror
    
    def set_ioerror(self, ioerror):
        self._ioerror = ioerror
        
    def get_metadataerror(self):
        return self._metadataerror
    
    def set_metadataerror(self, metadataerror):
        self._metadataerror = metadataerror
        
    def get_missingicon(self):
        return self._missingicon
    
    def set_missingicon(self, missingicon):
        self._missingicon = missingicon
        
    def get_thumberror(self):
        return self._thumberror
    
    def set_thumberror(self, thumberror):
        self._thumberror = thumberror
    
    missingmime = property(get_missingmime, set_missingmime)
    ioerror = property(get_ioerror, set_ioerror)
    metadataerror = property(get_metadataerror, set_metadataerror)
    missingicon = property(get_missingicon, set_missingicon)
    thumberror = property(get_thumberror, set_thumberror)

    #Window
    def get_windowmax(self):
        return self._windowmax
    
    def set_windowmax(self, windowmax):
        self._windowmax = windowmax
        
    def get_windowsize(self):
        return self._windowsize
    
    def set_windowsize(self, windowsize):
        self._windowsize = windowsize
    
    def get_logwindowmax(self):
        return self._logwindowmax
    
    def set_logwindowmax(self, logwindowmax):
        self._logwindowmax = logwindowmax
        
    def get_logwindowsize(self):
        return self._logwindowsize
    
    def set_logwindowsize(self, logwindowsize):
        self._logwindowsize = logwindowsize
    
    def get_infopanesize(self):
        return self._infopanesize
    
    def set_infopanesize(self, infopanesize):
        self._infopanesize = infopanesize
        
    windowmax = property(get_windowmax, set_windowmax)
    windowsize = property(get_windowsize, set_windowsize)
    logwindowmax = property(get_logwindowmax, set_logwindowmax)
    logwindowsize = property(get_logwindowsize, set_logwindowsize)
    infopanesize = property(get_infopanesize, set_infopanesize)

    #Interface
    def get_iconlistsize(self):
        return self._iconlistsize
    
    def set_iconlistsize(self, iconlistsize):
        self._iconlistsize = iconlistsize
        
    def get_iconpanesize(self):
        return self._iconpanesize
    
    def set_iconpanesize(self, iconpanesize):
        self._iconpanesize = iconpanesize
    
    def get_thumblistsize(self):
        return self._thumblistsize
    
    def set_thumblistsize(self, thumblistsize):
        self._thumblistsize = thumblistsize

    def get_thumbpanesize(self):
        return self._thumbpanesize
    
    def set_thumbpanesize(self, thumbpanesize):
        self._thumbpanesize = thumbpanesize

    def get_geninfo(self):
        return self._geninfo
    
    def set_geninfo(self, geninfo):
        self._geninfo = geninfo
    
    def get_abspath(self):
        return self._abspath
    
    def set_abspath(self, abspath):
        self._abspath = abspath
    
    def get_relpath(self):
        return self._relpath
    
    def set_relpath(self, relpath):
        self._relpath = relpath
        
    def get_size(self):
        return self._size
    
    def set_size(self, size):
        self._size = size
        
    def get_mime(self):
        return self._mime
    
    def set_mime(self, mime):
        self._mime = mime
        
    def get_atime(self):
        return self._atime
    
    def set_atime(self, atime):
        self._atime = atime
        
    def get_mtime(self):
        return self._mtime
    
    def set_mtime(self, mtime):
        self._mtime = mtime
        
    def get_mediainfo(self):
        return self._tblmediainfo

    def set_mediainfo(self, value):
        self._tblmediainfo = value
        
    def get_medialength(self):
        return self._medialength

    def set_medialength(self, value):
        self._medialength = value
        
    def get_videoinfo(self):
        return self._tblvideoinfo

    def set_videoinfo(self, videoinfo):
        self._tblvideoinfo = videoinfo

    def get_videocodec(self):
        return self._videocodec

    def set_videocodec(self, value):
        self._videocodec = value
        
    def get_videobitrate(self):
        return self._videobitrate

    def set_videobitrate(self, videobitrate):
        self._videobitrate = videobitrate

    def get_videores(self):
        return self._videores

    def set_videores(self, value):
        self._videores = value

    def get_videofps(self):
        return self._videofps

    def set_videofps(self, value):
        self._videofps = value

    def get_videoar(self):
        return self._videoar

    def set_videoar(self, value):
        self._videoar = value

    def get_audioinfo(self):
        return self._tblaudioinfo

    def set_audioinfo(self, value):
        self._tblaudioinfo = value

    def get_audiobitrate(self):
        return self._audiobitrate

    def set_audiobitrate(self, value):
        self._audiobitrate = value

    def get_audiosample(self):
        return self._audiosample

    def set_audiosample(self, value):
        self._audiosample = value

    def get_audiocodec(self):
        return self._audiocodec

    def set_audiocodec(self, value):
        self._audiocodec = value

    def get_audiochan(self):
        return self._audiochan

    def set_audiochan(self, value):
        self._audiochan = value

    def get_subinfo(self):
        return self._tblsubinfo

    def set_subinfo(self, value):
        self._tblsubinfo = value

    def get_sublangs(self):
        return self._sublangs

    def set_sublangs(self, value):
        self._sublangs = value

    def get_imginfo(self):
        return self._tblimginfo

    def set_imginfo(self, value):
        self._tblimginfo = value

    def get_imgres(self):
        return self._imgres

    def set_imgres(self, value):
        self._imgres = value
        
    def get_imgdate(self):
        return self._imgdate

    def set_imgdate(self, value):
        self._imgdate = value

    def get_imgauthor(self):
        return self._imgauthor

    def set_imgauthor(self, value):
        self._imgauthor = value

    def get_imgsoft(self):
        return self._imgsoft

    def set_imgsoft(self, value):
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
    
    def load_default_settings(self):
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
        self._missingmime = True
        self._ioerror = True
        self._metadataerror = True
        self._missingicon = True
        self._thumberror = True
        
        #Filters
        self._gnuhidden = True
        self._savebackup = True