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
from elixir import Entity, Field, Text, Integer, Float, OneToOne, OneToMany, \
                    ManyToOne, PickleType, Boolean, using_options

from logic.input.constants import SEPARATOR

class MetaDir(Entity):
    target = Field(Text)
    files = Field(Integer)
    dirs = Field(Integer)
    size = Field(Float)
    strsize = Field(Text)
    category = Field(Text)

class File(Entity):
    
    parent = Field(Text)
    name = Field(Text)
    relpath = Field(Text)
    mimetype = Field(Text)
    atime = Field(Text)
    mtime = Field(Text)
    size = Field(Float)
    strsize = Field(Text)
    isdir = Field(Boolean)
    strabs = Field(Text)
    root = ManyToOne("Directory")
    
    def __str__(self):
        return self.strabs
    

class Directory(File):
    
    using_options(inheritance='multi')
    dirs = ManyToOne("Directory")
    files = ManyToOne("File")
    
    def __str__(self):
        return self.strabs
    
class Video(File):
    
    using_options(inheritance='multi')
    length = Field(Text, default = None)
    videocodec = Field(Text, default = None)
    videobitrate = Field(Text, default = None)
    videores = Field(Text, default = None)
    videofps = Field(Text, default = None)
    videoar = Field(Text, default = None)
    audiobitrate = Field(Text, default = None)
    audiosamplerate = Field(Text, default = None)
    audiocodec = Field(Text, default = None)
    audiochannels = Field(Text, default = None)
    sublangs = Field(Text, default = None)

class Audio(File):
    
    using_options(inheritance='multi')
    length = Field(Text, default = None)
    bitrate = Field(Text, default = None)
    samplerate = Field(Text, default = None)
    codec = Field(Text, default = None)

class Photo(File):
    
    using_options(inheritance='multi')
    hasthumb = Field(Boolean, default = None)
    author = Field(Text, default = None)
    res = Field(Text, default = None)
    date_taken = Field(Text, default = None)
    soft = Field(Text, default = None)
    _thumb = Field(PickleType, default = None)
    _icon = Field(PickleType, default = None)
    
    def _get_thumb(self):
        return gtk.gdk.pixbuf_new_from_array(self._thumb, 
                                                   gtk.gdk.COLORSPACE_RGB, 8)
    
    def _set_thumb(self, value):
        if isinstance(value, gtk.gdk.Pixbuf):
            self._thumb = value.get_pixels_array()
    
    def _get_icon(self):
        return gtk.gdk.pixbuf_new_from_array(self._icon, 
                                                  gtk.gdk.COLORSPACE_RGB, 8)
    
    def _set_icon(self, value):
        if isinstance(value, gtk.gdk.Pixbuf):
            self._icon = value.get_pixels_array()