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

"""Module for the handler of catalog_properties"""

import gtk

from constants import CATEGORIES, MEDIA_TYPES


class CatalogPropertiesHandler(object):
    
    def __init__(self, mainhandler, metadir):
        self._metadir = metadir
        self._mainhandler = mainhandler
        self._wtree = gtk.Builder()
        self._wtree.add_from_file("view/catalog_properties.glade")
        self._wtree.connect_signals(self)
        self._txt_path = self._wtree.get_object("txt_path")
        self._txtv_comments = self._wtree.get_object("txtv_comments")
        self._lbl_time = self._wtree.get_object("lbl_time")
        self._lbl_files = self._wtree.get_object("lbl_files")
        self._lbl_dirs = self._wtree.get_object("lbl_dirs")
        self._window = self._wtree.get_object("mainwindow")
        
        self._lstype = gtk.ListStore(str, str)
        
        for type in MEDIA_TYPES:
            self._lstype.append([MEDIA_TYPES[type], type])
        
        self._crpicon = gtk.CellRendererPixbuf()
        self._crname = gtk.CellRendererText()    
        self._tvcolname = self._wtree.get_object("tvcolname")
        self._tvcolname.pack_start(self._crpicon, False)
        self._tvcolname.pack_start(self._crname)
        self._tvcolname.add_attribute(self._crpicon, "icon-name", 0)
        self._tvcolname.add_attribute(self._crname, "text", 1)
        
        self._tvtype = self._wtree.get_object("tvtype")
        self._tvtype.set_model(self._lstype)
        
        self._lscategories = gtk.ListStore(bool, str)
        self._crcheck = gtk.CellRendererToggle()
        self._crcategory = gtk.CellRendererText()
        self._crcheck.set_property("activatable", True)
        self._crcheck.connect( "toggled", self.crcheck_toggled_cb)
        self._tvcolcatname = self._wtree.get_object("tvcolcatname")
        self._tvcolcatname.pack_start(self._crcheck, False)
        self._tvcolcatname.pack_start(self._crcategory)
        self._tvcolcatname.add_attribute(self._crcheck, "active", 0)
        self._tvcolcatname.add_attribute(self._crcategory, "text", 1)
        
        self._tvcategories = self._wtree.get_object("tvcategories")
        self._tvcategories.set_model(self._lscategories)
        
        for category in CATEGORIES:
            self._lscategories.append([False, category])
        
        self._window.set_transient_for(self._mainhandler.window)
        self.load_catalog_data()
        self._window.show_all()
    
    def load_catalog_data(self):
        selection = self._tvtype.get_selection()
        self._txt_path.set_text(self._metadir.target)
        self._txtv_comments.get_buffer().set_text(self._metadir.comments)
        self._lbl_files.set_text(str(self._metadir.files))
        self._lbl_dirs.set_text(str(self._metadir.dirs))
        self._lbl_time.set_text(str(self._metadir.time) + " ms")
        for row in self._lstype:
            if row[0] == self._metadir.media_type:
                selection.select_path(row.path)
                break
        for row in self._lscategories:
            if row[1] in self._metadir.categories.split():
                row[0] = True
        
    def btnok_clicked_cb(self, widget):
        selection = self._tvtype.get_selection()
        media_type = self._lstype.get(selection.get_selected()[1], 0)[0]
        self._metadir.media_type = media_type
        buffer = self._txtv_comments.get_buffer()
        self._metadir.comments = buffer.get_text(buffer.get_start_iter(), buffer.get_end_iter())
        self._metadir.categories = ""
        for row in self._lscategories:
            if row[0] is True:
                self._metadir.categories += row[1] + " "
        self.btncancel_clicked_cb(widget)
    
    def btncancel_clicked_cb(self, widget):
        self._window.destroy()
        
    def crcheck_toggled_cb(self, cell, path):
        self._lscategories[path][0] = not self._lscategories[path][0]