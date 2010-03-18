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

import sys
import datetime
import time
import gtk

try:
   import kaa.metadata
   NO_KAA = False
except ImportError:
   NO_KAA = True
    
from fs.entities import MetaDir, File, Directory, Video, Audio, Photo
from logic.midput import SETTINGS
from logic.logging import MANAGER

import elixir
from sqlalchemy.schema import MetaData

from logic.input.constants import ICONS, MIMES, NO_INFO, NOT_AUDIO, SEPARATOR

class Factory(object):
    
    def __init__(self, engine, session):
        self._engine = engine
        self._session = session
        a_metadata = MetaData
        a_metadata.bind = engine
        elixir.setup_all()
        elixir.create_all(self._engine)
        #File._connection.debug = True
        #Directory._connection.debug = True
        
    def new_metadir(self, target, files, dirs, size, strsize):
        metadir = MetaDir(target = target, files = files, dirs = dirs, 
                       size = size, strsize = strsize, 
                       connection = self._conn)
        self._session.save(metadir)
        self._session.commit()
        return metadir
        
    def new_file(self, parent, name, relpath, mimetype, atime, mtime, 
                 root, strabs, size = None, strsize = None, isdir = False):

        atime, mtime = self._check_stat(atime, mtime)
        if mimetype is not None and mimetype[0] is not None:
            mimetype = mimetype[0]
        else:
            mimetype = "text/plain"
        _file = File(parent = parent, name = name, relpath = relpath,
                    mimetype = mimetype, atime = atime, mtime = mtime, 
                    size = size, strsize = strsize, isdir = isdir, 
                    strabs = strabs, root = root, connection = self._conn)
        self._session.save(_file)
        self._session.commit()
        return _file

    
    def new_dir(self, parent, name, relpath, atime, mtime, root, size, 
                strsize, strabs, isdir = True):
        atime, mtime = self._check_stat(atime, mtime)
        mimetype = "inode/folder"
        _dir = Directory(parent = parent, name = name, relpath = relpath, 
                         mimetype = mimetype, atime = atime, mtime = mtime, 
                         size = size, strsize = strsize, isdir = isdir, 
                         strabs = strabs, root = root, 
                         connection = self._conn)
        self._session.save(_dir)
        self._session.commit()
        return _dir
    
    def new_video(self, parent, name, relpath, mimetype, atime, mtime, 
                  root, size, strsize, strabs):
        atime, mtime = self._check_stat(atime, mtime)
        mimetype = mimetype[0]
        video = Video(parent = parent, name = name, relpath = relpath, 
                      mimetype = mimetype, atime = atime, mtime = mtime, 
                      size = size, strsize = strsize, root = root, 
                      isdir = False, strabs = strabs, 
                      connection = self._conn)
        self._get_video_metadata(video)
        self._session.save(video)
        self._session.commit()
        return video
    
    def new_audio(self, parent, name, relpath, mimetype, atime, mtime, 
                  root, size, strsize, strabs):
        atime, mtime = self._check_stat(atime, mtime)
        mimetype = mimetype[0]
        audio = Audio(parent = parent, name = name,  relpath = relpath, 
                      mimetype = mimetype, atime = atime, mtime = mtime, 
                      size = size, strsize = strsize, root = root, 
                      isdir = False, strabs = strabs, 
                      connection = self._conn)
        self._get_audio_metadata(audio)
        self._session.save(audio)
        self._session.commit()
        return audio
    
    def new_photo(self, parent, name, relpath, mimetype, atime, mtime, 
                  root, size, strsize, strabs):
        atime, mtime = self._check_stat(atime, mtime)
        mimetype = mimetype[0]
        photo = Photo(parent = parent, name = name, relpath = relpath, 
                      mimetype = mimetype, atime = atime, mtime = mtime, 
                      size = size, strsize = strsize, root = root, 
                      isdir = False, strabs = strabs, 
                      connection = self._conn)
        self._get_photo_metadata(photo)
        self._session.save(photo)
        self._session.commit()
        return photo
    
    def _get_video_metadata(self, video):
        """Try to load metadata from the actual file"""
        video.length, video.videocodec, video.videobitrate, \
        video.videores, video.videofps, video.videoar, \
        video.audiobitrate, video.audiosamplerate, video.audiocodec, \
        video.audiochannels = _return_tuple(NO_INFO, 10)
        length, videocodec, videobitrate, videores, \
        videofps, videoar, audiobitrate, audiosamplerate, \
        audiocodec, audiochannels, sublangs = _return_tuple(0, 11)
        try:
            info = kaa.metadata.parse(video.__str__())
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
                    vinfo = info.video[0]
                    if hasattr(vinfo, "codec") and vinfo.codec is not None:
                        videocodec = str(vinfo.codec)
                    if hasattr(vinfo, "bitrate")\
                    and vinfo.bitrate is not None:
                        videobitrate = str(vinfo.bitrate) + " Kbps"
                    if hasattr(vinfo, "aspect")\
                    and vinfo.aspect is not None:
                        videoar = str(round(vinfo.aspect, 2))
                    if hasattr(vinfo, "width") and vinfo.width is not None \
                    and hasattr(vinfo, "height") and vinfo.height is not None:
                        videores = str(vinfo.width) + "x" + str(vinfo.height)
                        if videoar == 0:
                            videoar = str(round(float(vinfo.width)
                                                /vinfo.height,2))
                    if hasattr(vinfo, "fps") and vinfo.fps is not None:
                        videofps = str(round(vinfo.fps, 3))
                
                #Loading audio attributes
                if hasattr(info, "audio") and info.audio[0] is not None:
                    ainfo = info.audio[0]
                    if hasattr(ainfo, "codec") and ainfo.codec is not None:
                        audiocodec = str(ainfo.codec)
                    if hasattr(ainfo, "samplerate")\
                    and ainfo.samplerate is not None:
                        audiosamplerate = str(ainfo.samplerate / 1000) + \
                                            " KHz"
                    if hasattr(ainfo, "bitrate")\
                    and ainfo.bitrate is not None:
                        audiobitrate = str(ainfo.bitrate)
                    if hasattr(ainfo, "channels")\
                    and ainfo.channels is not None:
                        audiochannels = str(ainfo.channels)
                
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
            video.length = length
        if videocodec != 0:
            video.videocodec = videocodec
        if videobitrate != 0:
            video.videobitrate = videobitrate
        if videores != 0:
            video.videores = videores
        if videofps != 0:
            video.videofps = videofps
        if videoar != 0:
            video.videoar = videoar
        if audiobitrate != 0:
            video.audiobitrate = audiobitrate
        if audiosamplerate != 0:
            video.audiosamplerate = audiosamplerate
        if audiocodec != 0:
            video.audiocodec = audiocodec
        if audiochannels != 0:
            video.audiochannels = audiochannels
        if sublangs != 0:
            video.sublangs = sublangs
    
    def _get_audio_metadata(self, audio):
        """Try to load metadata from the actual file"""
        audio.bitrate, audio.codec, audio.length, \
        audio.samplerate = _return_tuple(NO_INFO, 4)
        length, samplerate, bitrate, codec = _return_tuple(0, 4)
        try:
            info = kaa.metadata.parse(audio.__str__())
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
            audio.length = length
        if samplerate != 0:
            audio.samplerate = samplerate
        if bitrate != 0:
            audio.bitrate = bitrate
        if codec != 0:
            audio.codec = codec
    
    def _get_photo_metadata(self, photo):
        """Try to load metadata from the actual file"""
        photo.author, photo.date_taken, photo.res, \
        photo.soft = _return_tuple(NO_INFO, 4)
        try:
            width, height, author, soft, date_taken = _return_tuple(0, 5)
            info = kaa.metadata.parse(photo.__str__())
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
            photo.res = str(width) + "x" + str(height)
        if author != 0:
            photo.author = author
        if soft != 0:
            photo.soft = soft
        if date_taken != 0:
            photo.date_taken = date_taken
        
        try:
            photo.icon = \
            gtk.gdk.pixbuf_new_from_file_at_size(photo.strabs,
                                                 SETTINGS.thumblistsize,
                                                 SETTINGS.thumblistsize)
            photo.thumb = \
            gtk.gdk.pixbuf_new_from_file_at_size(photo.strabs,
                                                 SETTINGS.thumbpanesize,
                                                 SETTINGS.thumbpanesize)
            photo.hasthumb = True
        except Exception as exc:
            if SETTINGS.thumberror is True:
                MANAGER.append_event("Error loading thumbnail",
                                     photo.__str__(), exc, 5)
            print "Error occurred loading image metadata: " + self.__str__()
            print exc
            photo.hasthumb = False
            
    def _check_stat(self, atime, mtime):
        if atime is None:
            atime = NO_INFO
        if mtime is None:
            mtime = NO_INFO
        return atime, mtime
    
def _return_tuple(arg, count):
    """Method used to return a tuple of similar values
    
    It is used when assigning the same value to multiple variables. This
    method returns a tuple of \"count\" number of items, all of wich have the
    \"arg\" as value
    """
    return tuple([arg] * count)