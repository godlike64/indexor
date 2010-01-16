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

from controller import VERSION

class AboutHandler(object):
    
    def __init__(self, mainhandler):
        self._mainhandler = mainhandler
        self._wtree = gtk.Builder()
        self._wtree.add_from_file("view/about.glade")
        self._window = self._wtree.get_object("mainwindow")
        self._window.set_transient_for(self._mainhandler.window)
        self._window.connect("destroy", self.destroy)
        self._lblversion = self._wtree.get_object("lblversion")
        self._vwpicon = self._wtree.get_object("vwpicon")
        self._icon = gtk.gdk.pixbuf_new_from_file("icons/indexorapp.png")
        self._iconimg = gtk.image_new_from_pixbuf(self._icon)
        
        self._vwpicon.add(self._iconimg)
        self._lblversion.set_text("Indexor " + VERSION)
        
        self._window.show_all()
        
    def destroy(self, widget):
        if self._window is not None:
            self._window.destroy()
            self._window = None