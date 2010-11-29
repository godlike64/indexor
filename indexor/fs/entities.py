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


import gtk
from sqlobject import SQLObject, StringCol, FloatCol, BoolCol, IntCol, \
                        ForeignKey, DateTimeCol, PickleCol, MultipleJoin, \
                        RelatedJoin, DateTimeCol
from sqlobject.inheritance import InheritableSQLObject

from constants import SEPARATOR

class MetaDir(SQLObject):
    date = DateTimeCol()
    name = StringCol()
    target = StringCol()
    files = IntCol()
    dirs = IntCol()
    size = FloatCol()
    strsize = StringCol()
    time = IntCol()
    category = StringCol(default = "None")

class FileAbstract(InheritableSQLObject):

    parent = StringCol()
    name = StringCol()
    relpath = StringCol()
    mimetype = StringCol()
    atime = StringCol()
    mtime = StringCol()
    size = FloatCol()
    strsize = StringCol()
    isdir = BoolCol()
    strabs = StringCol()
    root = ForeignKey("Directory")

    def __str__(self):
        return self.strabs

class File(FileAbstract):
    pass


class Directory(FileAbstract):

    #==========================================================================
    # parent = StringCol()
    # name = StringCol()
    # relpath = StringCol()
    # mimetype = StringCol()
    # atime = StringCol()
    # mtime = StringCol()
    # size = FloatCol()
    # strsize = StringCol()
    # isdir = BoolCol()
    # strabs = StringCol()
    # root = ForeignKey("Directory")
    #==========================================================================
    entries = MultipleJoin("FileAbstract", joinColumn = "root_id")
    #dirs = MultipleJoin("Directory", joinColumn = "root_id")
    #files = MultipleJoin("File", joinColumn = "root_id")

    def _filter_entries(self, klass):
        return [entry for entry in self.entries if isinstance(entry, klass)]

    def _get_files(self):
        return self._filter_entries(File)

    def _get_dirs(self):
        return self._filter_entries(Directory)

    def __str__(self):
        return self.strabs

class Video(File):

    length = StringCol(default = None)
    videocodec = StringCol(default = None)
    videobitrate = StringCol(default = None)
    videores = StringCol(default = None)
    videofps = StringCol(default = None)
    videoar = StringCol(default = None)
    audiobitrate = StringCol(default = None)
    audiosamplerate = StringCol(default = None)
    audiocodec = StringCol(default = None)
    audiochannels = StringCol(default = None)
    sublangs = StringCol(default = None)

class Audio(File):

    length = StringCol(default = None)
    bitrate = StringCol(default = None)
    samplerate = StringCol(default = None)
    codec = StringCol(default = None)

class Photo(File):

    hasthumb = BoolCol(default = None)
    author = StringCol(default = None)
    res = StringCol(default = None)
    date_taken = StringCol(default = None)
    soft = StringCol(default = None)
    _thumb = PickleCol(default = None)
    _icon = PickleCol(default = None)

    def get_thumb(self):
        return gtk.gdk.pixbuf_new_from_array(self._thumb,
                                                   gtk.gdk.COLORSPACE_RGB, 8)

    def set_thumb(self, value):
        if isinstance(value, gtk.gdk.Pixbuf):
            self._thumb = value.get_pixels_array()

    def get_icon(self):
        return gtk.gdk.pixbuf_new_from_array(self._icon,
                                                  gtk.gdk.COLORSPACE_RGB, 8)

    def set_icon(self, value):
        if isinstance(value, gtk.gdk.Pixbuf):
            self._icon = value.get_pixels_array()

    thumb = property(get_thumb, set_thumb)
    icon = property(get_icon, set_icon)
