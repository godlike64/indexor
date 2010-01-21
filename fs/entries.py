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

"""Module for the different filesystem entities.

This module is meant to be extendable: the listed classes represent normal
filesystem types, but of course not all of them are represented. Any changes
in this module will surely break binary compatibility with older archives, so
be cautious!
The two constants defined in this module help in the detection of mimetypes,
and in the setting of the corresponding icon for the entry.
All metadata from media files is extracted using the kaa.metadata package.
"""

import gtk
import sys
try:
    import kaa.metadata
    NO_KAA = False
except ImportError:
    NO_KAA = True
import datetime

from logic.midput import SETTINGS
from logic.logging import MANAGER

if sys.platform == "win32":
    SEPARATOR = "\\"
else:
    SEPARATOR = "/"

NO_INFO = "No information available"

MIMES = {
        "audio/basic"                                   :   "audio",
        "audio/flac"                                    :   "audio",
        "audio/midi"                                    :   "audio",
        "audio/mpeg"                                    :   "audio",
        "audio/ogg"                                     :   "audio",
        "audio/x-aiff"                                  :   "audio",
        "audio/x-mpegurl"                               :   "audio",
        "audio/x-ms-wma"                                :   "audio",
        "audio/x-musepack"                              :   "audio",
        "audio/x-scpls"                                 :   "audio",
        "audio/x-spc"                                   :   "audio",
        "audio/x-wav"                                   :   "audio",
        "application/base64"                            :   "executable",
        "application/java-archive"                      :   "archive",
        "application/java-serialized-object"            :   "executable",
        "application/java-vm"                           :   "executable",
        "application/json"                              :   "source",
        "application/mathematica"                       :   "ascii",
        "application/msword"                            :   "document",
        "application/octet-stream"                      :   "executable",
        "application/ogg"                               :   "audio",
        "application/pdf"                               :   "document",
        "application/pgp-keys"                          :   "security",
        "application/pgp-signature"                     :   "security",
        "application/pics-rules"                        :   "file",
        "application/postscript"                        :   "print",
        "application/rar"                               :   "archive",
        "application/relax-ng-compact-syntax"           :   "html",
        "application/rdf+xml"                           :   "html",
        "application/rtf"                               :   "document",
        "application/vnd.lotus-organizer"               :   "html",
        "application/vnd.mozilla.xul+xml"               :   "html",
        "application/vnd.ms-cab-compressed"             :   "archive",
        "application/vnd.ms-excel"                      :   "spreadsheet",
        "application/vnd.ms-excel.sheet." +
        "macroenabled.12"                               :   "spreadsheet",
        "application/vnd.ms-pki.seccat"                 :   "archive",
        "application/vnd.ms-powerpoint"                 :   "presentation",
        "application/vnd.oasis.opendocument.database"   :   "document",
        "application/vnd.oasis.opendocument.formula"    :   "document",
        "application/vnd.oasis.opendocument." +
        "presentation"                                  :   "presentation",
        "application/vnd.oasis.opendocument." +
        "spreadsheet"                                   :   "spreadsheet",
        "application/vnd.oasis.opendocument.text"       :   "document",
        "application/vnd.openxmlformats-" +
        "officedocument.presentationml.presentation"    :   "presentation",
        "application/vnd.openxmlformats-" +
        "officedocument.spreadsheetml.sheet"            :   "spreadsheet",
        "application/vnd.openxmlformats-" +
        "officedocument.wordprocessingml.document"      :   "document",
        "application/vnd.palm"                          :   "executable",
        "application/vnd.visio"                         :   "drawing",
        "application/winhlp"                            :   "help",
        "application/wsdl+xml"                          :   "html",
        "application/x-bittorrent"                      :   "archive",
        "application/x-bzip"                            :   "archive",
        "application/x-bzip2"                           :   "archive",
        "application/x-bzip-compressed-tar"             :   "archive",
        "application/x-bzip-compressed-tar"             :   "archive",
        "application/x-bcpio"                           :   "archive",
        "application/x-cdlink"                          :   "optical",
        "text/x-c"                                      :   "source",
        "application/x-chm"                             :   "help",
        "application/x-cpio"                            :   "archive",
        "application/x-csh"                             :   "script",
        "application/x-debian-package"                  :   "archive",
        "application/x-director"                        :   "internet",
        "application/x-dtbresource+xml"                 :   "html",
        "application/x-flac"                            :   "audio",
        "application/x-font"                            :   "font",
        "application/x-font-type1"                      :   "font",
        "application/x-font-ttf"                        :   "font",
        "application/x-genesis-rom"                     :   "game",
        "application/x-glade"                           :   "glade",
        "application/x-graphing-calculator"             :   "calc",
        "application/x-gzip"                            :   "archive",
        "application/x-internet-signup"                 :   "internet",
        "application/x-iso9660-image"                   :   "optical",
        "application/x-javascript"                      :   "html",
        "application/x-maker"                           :   "script",
        "application/x-mif"                             :   "mail",
        "application/x-msdos-program"                   :   "script",
        "application/x-msdownload"                      :   "executable",
        "application/x-msi"                             :   "executable",
        "application/x-mswrite"                         :   "document",
        "application/x-netcdf"                          :   "browser",
        "application/x-object"                          :   "file",
        "application/x-php"                             :   "html",
        "application/x-pn-realaudio"                    :   "audio",
        "application/x-pkcs7-crl"                       :   "certificate",
        "application/x-python-code"                     :   "script",
        "application/x-rar-compressed"                  :   "archive",
        "application/x-redhat-package-manager"          :   "archive",
        "application/x-sh"                              :   "script",
        "application/x-shockwave-flash"                 :   "video",
        "application/x-ssh-key"                         :   "security",
        "application/x-subrip"                          :   "ascii",
        "application/x-tar"                             :   "archive",
        "application/x-tcl"                             :   "executable",
        "application/x-tex"                             :   "ascii",
        "application/x-trash"                           :   "trash",
        "application/x-troff"                           :   "ascii",
        "application/x-troff-man"                       :   "ascii",
        "application/x-troff-me"                        :   "ascii",
        "application/x-troff-ms"                        :   "ascii",
        "application/x-wais-source"                     :   "executable",
        "application/x-x509-ca-cert"                    :   "certificate",
        "application/x-xcf"                             :   "image",
        "application/x-xfig"                            :   "image",
        "application/x-xpinstall"                       :   "executable",
        "application/xhtml+xml"                         :   "html",
        "application/xml"                               :   "html",
        "application/xml-dtd"                           :   "html",
        "application/xslt+xml"                          :   "html",
        "application/zip"                               :   "archive",
        "chemical/x-crossfire"                          :   "file",
        "chemical/x-gamess-input"                       :   "file",
        "chemical/x-gaussian-log"                       :   "file",
        "chemical/x-pdb"                                :   "file",
        "chemical/x-xyz"                                :   "file",
        "image/x-corelphotopaint"                       :   "image",
        "image/gif"                                     :   "image",
        "image/jpeg"                                    :   "image",
        "image/pict"                                    :   "image",
        "image/png"                                     :   "image",
        "image/svg+xml"                                 :   "image",
        "image/tiff"                                    :   "image",
        "image/vnd.djvu"                                :   "image",
        "image/x-icon"                                  :   "image",
        "image/x-ms-bmp"                                :   "image",
        "image/x-photoshop"                             :   "image",
        "image/x-portable-bitmap"                       :   "image",
        "image/x-portable-pixmap"                       :   "image",
        "image/x-xbitmap"                               :   "image",
        "image/x-xpixmap"                               :   "image",
        "image/x-tga"                                   :   "image",
        "message/rfc822"                                :   "mail",
        "text/cache"                                    :   "ascii",
        "text/calendar"                                 :   "calendar",
        "text/comma-separated-values"                   :   "ascii",
        "text/css"                                      :   "html",
        "text/csv"                                      :   "ascii",
        "text/html"                                     :   "html",
        "text/plain"                                    :   "ascii",
        "text/rtf"                                      :   "document",
        "text/sgml"                                     :   "html",
        "text/texmacs"                                  :   "document",
        "text/troff"                                    :   "document",
        "text/x-asm"                                    :   "source",
        "text/x-bibtex"                                 :   "text",
        "text/x-c++hdr"                                 :   "source",
        "text/x-c++src"                                 :   "source",
        "text/x-chdr"                                   :   "script",
        "text/x-csrc"                                   :   "source",
        "text/x-fortran"                                :   "source",
        "text/x-haskell"                                :   "source",
        "text/x-perl"                                   :   "script",
        "text/x-subviewer"                              :   "ascii",
        "text/x-java"                                   :   "source",
        "text/x-java-source"                            :   "source",
        "text/x-moc"                                    :   "source",
        "text/x-psp"                                    :   "ascii",
        "text/x-python"                                 :   "script",
        "text/x-sgml"                                   :   "html",
        "text/x-sh"                                     :   "script",
        "text/x-tex"                                    :   "document",
        "text/x-tcl"                                    :   "source",
        "text/x-vcalendar"                              :   "calendar",
        "text/x-vcard"                                  :   "ascii",
        "text/vnd.sun.j2me.app-descriptor"              :   "archive",
        "text/xml"                                      :   "html",
        "text/xul"                                      :   "html",
        "video/mp4"                                     :   "video",
        "video/mpeg"                                    :   "video",
        "video/quicktime"                               :   "video",
        "video/ogg"                                     :   "video",
        "video/x-flv"                                   :   "video",
        "video/x-matroska"                              :   "video",
        "video/x-mng"                                   :   "video",
        "video/x-ms-asf"                                :   "video",
        "video/x-ms-wmv"                                :   "video",
        "video/x-msvideo"                               :   "video",
        }

ICONS = {
        "ascii"                 :   "text-x-generic",
            "archive"           :   "package-x-generic",
            "audio"             :   "audio-x-generic",
            "calc"              :   "accessories-calculator",
            "calendar"          :   "x-office-calendar",
            "certificate"       :   "application-certificate",
            "browser"           :   "browser",
            "disk"              :   "drive-harddisk",
            "document"          :   "x-office-document",
            "document-template" :   "x-office-document-template",
            "drawing"           :   "x-office-drawing",
            "executable"        :   "application-x-executable",
            "file"              :   "text-x-generic",
            "font"              :   "font-x-generic",
            "folder"            :   "folder",
            "game"              :   "applications-games",
            "glade"             :   "preferences-system-session",
            "help"              :   "help-browser",
            "html"              :   "text-html",
            "image"             :   "image-x-generic",
            "internet"          :   "applications-internet",
            "mail"              :   "internet-mail",
            "optical"           :   "media-optical",
            "print"             :   "document-print",
            "presentation"      :   "x-office-presentation",
            "security"          :   "system-lock-screen",
            "script"            :   "text-x-script",
            "source"            :   "text-x-generic-template",
            "spreadsheet"       :   "x-office-spreadsheet",
            "trash"             :   "user-trash",
            "video"             :   "video-x-generic",
         }

#==============================================================================
# AUDIO = {
#            ".ape"  :   mutagen.monkeysaudio.MonkeysAudio,
#            ".asf"  :   mutagen.asf.ASF,
#            ".flac" :   mutagen.flac.FLAC,
#            ".m4a"  :   mutagen.mp4.MP4,
#            ".mp3"  :   mutagen.mp3.MP3,
#            ".mpc"  :   mutagen.musepack.Musepack,
#            ".ogg"  :   mutagen.oggvorbis.OggVorbis,
#            ".wav"  :   wave.open,
#            ".wma"  :   mutagen.asf.ASF
#         }
#==============================================================================

NOT_AUDIO = [
             "audio/basic",
             "audio/x-mpegurl",
             "audio/x-scpls",
             "audio/x-spc",
             "audio/midi"
             ]

class File(object):

    """Class that represents a regular file.
    
    There is no additional data to register in this class, other than the 
    mimetype, icon and size. However, all other classes must extend from this
    one in order to avoid duplicated behaviour.
    """
    
    def __init__(self, parent, name, relpath, mimetype, atime, mtime,
                 size=None, strsize=None, isdir=False):
        self._parent = parent
        self._name = name
        self._relpath = relpath 
        if atime is not None:
            self._atime = atime
        else:
            self._atime = "No information available"
        if mtime is not None:
            self._mtime = mtime
        else:
            self._mtime = "No information available"
        self._size = size
        self._strsize = strsize
        self._mimetype = "ascii"
        self._icon = None
        if mimetype is not None and mimetype[0] is not None:
            self._mimetype = mimetype[0]
            try:
                self._icon = gtk.icon_theme_get_default().\
                load_icon(ICONS[MIMES[self._mimetype]], SETTINGS.iconlistsize,
                          gtk.ICON_LOOKUP_FORCE_SVG)
            except Exception as exc:
                if SETTINGS.missingicon is True:
                    if not isdir:
                        MANAGER.\
                        append_event("Error loading icon for mimetype: " +
                                     self._mimetype, self.__str__(), exc, 4)
                        print "Error loading icon for mimetype: " + \
                        self._mimetype + ". File: " + self.__str__()
        if self._icon == None:
            self._mimetype = "text/plain"
            self._icon = gtk.icon_theme_get_default().\
            load_icon(ICONS["file"], SETTINGS.iconlistsize,
                      gtk.ICON_LOOKUP_FORCE_SVG)

    #################################
    #Properties
    #################################
    def get_mimetype(self):
        """Property"""
        return self._mimetype

    def set_mimetype(self, value):
        """Property"""
        self._mimetype = value

    def get_name(self):
        """Property"""
        return self._name

    def set_name(self, name):
        """Property"""
        self._name = name

    def get_relpath(self):
        """Property"""
        return self._relpath

    def set_relpath(self, relpath):
        """Property"""
        self._relpath = relpath

    def get_parent(self):
        """Property"""
        return self._parent

    def set_parent(self, parent):
        """Property"""
        self._parent = parent

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

    def get_size(self):
        """Property"""
        return self._size

    def set_size(self, size):
        """Property"""
        self._size = size

    def get_strsize(self):
        """Property"""
        return self._strsize

    def set_strsize(self, strsize):
        """Property"""
        self._strsize = strsize

    def get_icon(self):
        """Property"""
        return self._icon

    def set_icon(self, icon):
        """Property"""
        self._icon = icon

    name = property(get_name, set_name)
    parent = property(get_parent, set_parent)
    relpath = property(get_relpath, set_relpath)
    atime = property(get_atime, set_atime)
    mtime = property(get_mtime, set_mtime)
    size = property(get_size, set_size)
    strsize = property(get_strsize, set_strsize)
    mimetype = property(get_mimetype, set_mimetype)
    icon = property(get_icon, set_icon)

    #################################
    #Methods
    #################################
    def __str__(self):
        return self.parent + SEPARATOR + self.name

    def parse_icon(self):
        """Method used when reading from binary file."""
        try:
            self._icon = gtk.icon_theme_get_default().\
                load_icon(ICONS[MIMES[self._mimetype]], SETTINGS.iconlistsize,
                        gtk.ICON_LOOKUP_FORCE_SVG)
        except Exception as exc:
            if SETTINGS.missingicon is True:
                MANAGER.append_event("Error loading icon for mimetype: " +
                                     self._mimetype, self.__str__(), exc, 4)
        if self._icon == None:
            self._icon = gtk.icon_theme_get_default().\
            load_icon(ICONS["file"], SETTINGS.iconlistsize,
                      gtk.ICON_LOOKUP_FORCE_SVG)

    def __getstate__(self):
        result = self.__dict__.copy()
        return result

    def __setstate__(self, result):
        self.__dict__ = result

class Directory(File):

    """Class that represents a directory."""

    def __init__(self, parent, name, relpath, atime, mtime, size, strsize):
        super(Directory, self).__init__(parent, name, relpath, atime, mtime,
                                        None, isdir=True)
        self._dirs = []
        self._files = []
        self._size = size
        self._strsize = strsize
        self._icon = gtk.icon_theme_get_default().\
            load_icon("folder", SETTINGS.iconlistsize,
                      gtk.ICON_LOOKUP_FORCE_SVG)

    #################################
    #Properties
    #################################
    def get_dirs(self):
        """Property"""
        return self._dirs

    def get_files(self):
        """Property"""
        return self._files

    dirs = property(get_dirs)
    files = property(get_files)

    #################################
    #Methods
    #################################
    def append_dir(self, _dir):
        """Append a directory to the respective array."""
        self._dirs.append(_dir)

    def append_file(self, _file):
        """Append a file to the respective array."""
        self._files.append(_file)

    def __getstate__(self):
        dictcopy = self.__dict__.copy()
        result = (dictcopy, self.dirs, self.files, self.icon)
        return result

    def __setstate__(self, result):
        self.__dict__ = result[0]
        self._dirs = result [1]
        self._files = result [2]
        self.icon = result[3]

    def parse_icon(self):
        """Method used when reading from binary file."""
        self._icon = gtk.icon_theme_get_default().\
            load_icon("folder", SETTINGS.iconlistsize,
                      gtk.ICON_LOOKUP_FORCE_SVG)

class Video(File):
    
    """Class that represents a Video file"""

    def __init__(self, parent, name, relpath, mimetype, atime, mtime, size,
                 strsize):
        super(Video, self).__init__(parent, name, relpath, mimetype, atime,
                                    mtime, size=size, strsize=strsize)
        self._length, self._videocodec, self._videobitrate, \
        self._videores, self._videofps, self._videoar, self._audiobitrate, \
        self._audiosamplerate, self._audiocodec, \
        self._audiochannels = _return_tuple(NO_INFO, 10)
        if NO_KAA is not True:
            self._load_metadata()

    #################################
    #Properties
    #################################
    def get_length(self):
        """Property"""
        return self._length

    def get_videocodec(self):
        """Property"""
        return self._videocodec

    def get_videobitrate(self):
        """Property"""
        return self._videobitrate

    def get_videores(self):
        """Property"""
        return self._videores

    def get_videofps(self):
        """Property"""
        return self._videofps

    def get_videoar(self):
        """Property"""
        return self._videoar

    def get_audiobitrate(self):
        """Property"""
        return self._audiobitrate

    def get_audiosamplerate(self):
        """Property"""
        return self._audiosamplerate

    def get_audiocodec(self):
        """Property"""
        return self._audiocodec

    def get_audiochannels(self):
        """Property"""
        return self._audiochannels

    def get_sublangs(self):
        """Property"""
        return self._sublangs

    length = property(get_length)
    videocodec = property(get_videocodec)
    videobitrate = property(get_videobitrate)
    videores = property(get_videores)
    videofps = property(get_videofps)
    videoar = property(get_videoar)
    audiobitrate = property(get_audiobitrate)
    audiosamplerate = property(get_audiosamplerate)
    audiocodec = property(get_audiocodec)
    audiochannels = property(get_audiochannels)
    sublangs = property(get_sublangs)

    #################################
    #Methods
    #################################
    def _load_metadata(self):
        """Try to load metadata from the actual file"""
        length, videocodec, videobitrate, videores, \
        videofps, videoar, audiobitrate, audiosamplerate, \
        audiocodec, audiochannels, sublangs = _return_tuple(0, 11)
        try:
            info = kaa.metadata.parse(self.__str__())
            if info is not None:
                if hasattr(info, "length") and info.length is not None:
                    hourlength, minlength, seclength = _return_tuple(0, 3)
                    if info.length >= 60:
                        minlength = int(info.length / 60)
                        seclength = int(info.length % 60)
                        while minlength >= 60:
                            hourlength += int(minlength / 60)
                            minlength = int(minlength % 60)
                    length = str(hourlength) + ":" + str(minlength).zfill(2)\
                                + ":" + str(seclength).zfill(2)
                
                #Loading video attributes
                if hasattr(info, "video") and info.video[0] is not None:
                    video = info.video[0]
                    if hasattr(video, "codec") and video.codec is not None:
                        videocodec = str(video.codec)
                    if hasattr(video, "bitrate")\
                    and video.bitrate is not None:
                        videobitrate = str(video.bitrate) + " Kbps"
                    if hasattr(video, "aspect")\
                    and video.aspect is not None:
                        videoar = str(round(video.aspect, 2))
                    if hasattr(video, "width") and video.width is not None\
                    and hasattr(video, "height") and video.height is not None:
                        videores = str(video.width) + "x" + str(video.height)
                        if videoar == 0:
                            videoar = str(round(float(video.width)
                                                /video.height,2))
                    if hasattr(video, "fps") and video.fps is not None:
                        videofps = str(round(video.fps, 3))
                
                #Loading audio attributes
                if hasattr(info, "audio") and info.audio[0] is not None:
                    audio = info.audio[0]
                    if hasattr(audio, "codec") and audio.codec is not None:
                        audiocodec = str(audio.codec)
                    if hasattr(audio, "samplerate")\
                    and audio.samplerate is not None:
                        audiosamplerate = str(audio.samplerate / 1000) + " KHz"
                    if hasattr(audio, "bitrate")\
                    and audio.bitrate is not None:
                        audiobitrate = str(audio.bitrate)
                    if hasattr(audio, "channels")\
                    and audio.channels is not None:
                        audiochannels = str(audio.channels)
                
                #Loading subtitle attributes
                if hasattr(info, "subtitles") and len(info.subtitles) > 0:
                    sublangs = ""
                    sublangs += info.subtitles[0].language
                    if len(info.subtitles) > 1:
                        for sub in info.subtitles[1:]:
                            sublangs += ", " + sub.language
        except Exception as exc:
            if SETTINGS.metadataerror is True:
                MANAGER.append_event("Error loading video metadata", 
                                     self.__str__(), exc, 3)
            print "Error loading video metadata: " + self.__str__()
            print exc
        
        #Assigning to class variables
        if length != 0:
            self._length = length
        if videocodec != 0:
            self._videocodec = videocodec
        if videobitrate != 0:
            self._videobitrate = videobitrate
        if videores != 0:
            self._videores = videores
        if videofps != 0:
            self._videofps = videofps
        if videoar != 0:
            self._videoar = videoar
        if audiobitrate != 0:
            self._audiobitrate = audiobitrate
        if audiosamplerate != 0:
            self._audiosamplerate = audiosamplerate
        if audiocodec != 0:
            self._audiocodec = audiocodec
        if audiochannels != 0:
            self._audiochannels = audiochannels
        if sublangs != 0:
            self._sublangs = sublangs

class Audio(File):

    """Class that represents a music file."""
    
    def __init__(self, parent, name, relpath, mimetype, atime, mtime, size,
                 strsize):
        super(Audio, self).__init__(parent, name, relpath, mimetype, atime,
                                    mtime, size=size, strsize=strsize)
        self._length, self._bitrate, self._samplerate, self._codec = \
        _return_tuple(NO_INFO, 4)
        if NO_KAA is not True:
            self._load_metadata()
        
    #################################
    #Properties
    #################################
    def get_length(self):
        """Property"""
        return self._length

    def get_bitrate(self):
        """Property"""
        return self._bitrate

    def get_sample_rate(self):
        """Property"""
        return self._samplerate

    def get_codec(self):
        """Property"""
        return self._codec

    length = property(get_length)
    bitrate = property(get_bitrate)
    samplerate = property(get_sample_rate)
    codec = property(get_codec)

    #################################
    #Methods
    #################################
    def _load_metadata(self):
        """Try to load metadata from the actual file"""
        length, samplerate, bitrate, codec = _return_tuple(0, 4)
        try:
            info = kaa.metadata.parse(self.__str__())
            if info is not None:
                if hasattr(info, "length") and info.length is not None:
                    length = str(int(info.length / 60)) + ":" + \
                                str(int(info.length % 60)).zfill(2)
                elif hasattr(info, "audio"):
                    if (info.audio[0]) is not None and \
                    hasattr(info.audio[0], "length") and \
                    info.audio[0].length is not None:
                        length = str(int(info.audio[0].length / 60)) + ":" + \
                                    str(int(info.audio[0].length % 60))\
                                    .zfill(2)
                if hasattr(info, "bitrate") and info.bitrate is not None:
                    bitrate = str(info.bitrate) + " Kbps"
                elif hasattr(info, "audio"):
                    if (info.audio[0]) is not None and \
                    hasattr(info.audio[0], "bitrate") and \
                    info.audio[0].bitrate is not None:
                        bitrate = str(info.audio[0].bitrate) + " Kbps"
                if hasattr(info, "samplerate")\
                and info.samplerate is not None:
                    samplerate = str(info.samplerate / 1000) + " KHz"
                elif hasattr(info, "audio"):
                    if (info.audio[0]) is not None and \
                    hasattr(info.audio[0], "samplerate") and \
                    info.audio[0].samplerate is not None:
                        samplerate = str(info.audio[0].samplerate
                                         / 1000) + " KHz"
                if hasattr(info, "codec") and info.codec is not None:
                    codec = info.codec
                elif hasattr(info, "audio"):
                    if (info.audio[0]) is not None and \
                    hasattr(info.audio[0], "codec") and \
                    info.audio[0].codec is not None:
                        codec = info.audio[0].codec
        except Exception as exc:
            if SETTINGS.metadataerror is True:
                MANAGER.append_event("Error loading audio metadata",
                                     self.__str__(), exc, 3)
            print "Error loading audio metadata: " + self.__str__()
            print exc
        if length != 0:
            self._length = length
        if samplerate != 0:
            self._samplerate = samplerate
        if bitrate != 0:
            self._bitrate = bitrate
        if codec != 0:
            self._codec = codec

class Photo(File):

    """Class that represents an image or photo.
    
    The name was chosen on purpose in order to avoid name colliding with
    other clases (e.g. gtk.Image).
    """
    
    def __init__(self, parent, name, relpath, mimetype, atime, mtime, size,
                 strsize):
        super(Photo, self).__init__(parent, name, relpath, mimetype, atime,
                                    mtime, size=size, strsize=strsize)
        try:
            self._icon = \
            gtk.gdk.pixbuf_new_from_file_at_size(self._parent + SEPARATOR +
                                                 self._name,
                                                 SETTINGS.thumblistsize,
                                                 SETTINGS.thumblistsize)
            self._thumb = \
            gtk.gdk.pixbuf_new_from_file_at_size(self._parent + SEPARATOR + \
                                                 self._name,
                                                 SETTINGS.thumbpanesize,
                                                 SETTINGS.thumbpanesize)
            self._hasthumb = True
        except Exception as exc:
            if SETTINGS.thumberror is True:
                MANAGER.append_event("Error loading thumbnail",
                                     self.__str__(), exc, 5)
            self.parse_icon()
        #Try loading image metadata
        self._res, self._date_taken, self._author, self._soft, \
            self._date_taken = _return_tuple(NO_INFO, 5)
        if NO_KAA is not True:
            self._load_metadata()

    #################################
    #Properties
    #################################             
    def get_hasthumb(self):
        """Property"""
        return self._hasthumb

    def get_res(self):
        """Property"""
        return self._res

    def get_date_taken(self):
        """Property"""
        return self._date_taken

    def get_soft(self):
        """Property"""
        return self._soft

    def get_author(self):
        """Property"""
        return self._author
    
    def get_thumb(self):
        """Property"""
        return self._thumb
    
    def set_thumb(self, thumb):
        """Property"""
        self._thumb = thumb

    hasthumb = property(get_hasthumb)
    res = property(get_res)
    date_taken = property(get_date_taken)
    soft = property(get_soft)
    author = property(get_author)
    thumb = property(get_thumb, set_thumb)

    #################################
    #Methods
    #################################
    def parse_icon(self):
        """Method used when reading from binary file."""
        try:
            self._icon = gtk.icon_theme_get_default().\
                    load_icon(ICONS["image"], SETTINGS.iconlistsize,
                              gtk.ICON_LOOKUP_FORCE_SVG)
            self._thumb = gtk.icon_theme_get_default().\
                    load_icon(ICONS["image"], SETTINGS.iconlistsize,
                              gtk.ICON_LOOKUP_FORCE_SVG)
        except Exception as exc:
            if SETTINGS.missingicon is True:
                MANAGER.append_event("Error loading icon for mimetype: " +
                                     self._mimetype, self.__str__(), exc, 4)
        finally:
            self._hasthumb = False

    def _load_metadata(self):
        """Try to load metadata from the actual file"""
        try:
            width, height, author, soft, date_taken = _return_tuple(0, 5)
            info = kaa.metadata.parse(self.__str__())
            if info is not None:
                if info.width is not None:
                    width = info.width
                if info.height is not None:
                    height = info.height
                if info.author is not None:
                    author = info.author
                elif info.artist is not None:
                    author = info.author
                if info.software is not None:
                    soft = info.software
                if info.timestamp is not None:
                    date_taken = datetime.datetime.fromtimestamp\
                                    (info.timestamp).strftime\
                                    ("%Y/%m/%d %H:%M:%S")
        except Exception, exc:
            if SETTINGS.metadataerror is True:
                MANAGER.append_event("Error loading image metadata",
                                     self.__str__(), exc, 3)
            print "Error occurred loading image metadata: " + self.__str__()
            print exc
        if width != 0 and height != 0:
            self._res = str(width) + "x" + str(height)
        if author != 0:
            self._author = author
        if soft != 0:
            self._soft = soft
        if date_taken != 0:
            self._date_taken = date_taken


def _return_tuple(arg, count):
    """Method used to return a tuple of similar values
    
    It is used when assigning the same value to multiple variables. This
    method returns a tuple of \"count\" number of items, all of wich have the
    \"arg\" as value
    """
    return tuple([arg] * count)
