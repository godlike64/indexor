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

"""This module handles the writing and reading of the resulting catalog
in binary form."""

import cPickle as pickle
import gzip
import gtk


class BinaryWriter(object):
    
    """Class that writes the catalog to a binary file.
    
    It compresses the output using gzip, and discards all icons loaded in the
    indexing process, in order to reduce used space. In the case of Photos, it
    serializes the thumbs so they can be saved and retrieved.
    """
    
    def __init__(self, filename, root):
        self.pickle_images(root)
        output = gzip.open(filename, 'wb')
        pickle.dump(root, output, pickle.HIGHEST_PROTOCOL)
        output.close()
        
    def pickle_images(self, root):
        """Discards the icons and serializes thumbnails."""
        for _file in root.files:
            if hasattr(_file, "hasthumb"):
                _file.icon = _file.icon.get_pixels_array()
                _file.thumb = _file.thumb.get_pixels_array()
            else:
                _file.icon = None
        for _dir in root.dirs:
            _dir.icon = None
            self.pickle_images(_dir)

class BinaryReader(object):
    
    """Class that reads a saved catalog in binary form.
    
    After opening and loading the data in the archive, the icons are
    reprocessed and thumbs are deserialized and loaded again.
    """
    
    def __init__(self, filename):
        inputfile = gzip.open(filename, 'rb')
        self._root =  pickle.load(inputfile)
        inputfile.close()
        self.unpickle_images(self._root)
        
    def get_root(self):
        """Return the root node"""
        
        return self._root
        
    def unpickle_images(self, root):
        """Load icons and thumbnails."""
        for _file in root.files:
            if hasattr(_file, "hasthumb"):
                _file.icon = gtk.gdk.pixbuf_new_from_array\
                                (_file.icon, gtk.gdk.COLORSPACE_RGB, 8)
                _file.thumb = gtk.gdk.pixbuf_new_from_array\
                                (_file.thumb, gtk.gdk.COLORSPACE_RGB,8)
            else:
                _file.parse_icon()
        for _dir in root.dirs:
            _dir.parse_icon()
            self.unpickle_images(_dir)
