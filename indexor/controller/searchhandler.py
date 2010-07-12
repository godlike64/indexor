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

"""Module for the handler of the search window"""

import gtk

class SearchHandler(object):

    """Search window handler.
    
    Handles all events from the search window, and also performs the searches.
    I know that last bit of code should not be in here, but it is really small
    and to me it doesn't justify creating another module/class for it.
    """

    def __init__(self, mainhandler):
        self._gladefile = "view/search.glade"
        self._mainhandler = mainhandler
        self._wtree = gtk.Builder()
        self._wtree.add_from_file(gladefile)
        self._window = self._wtree.get_object("searchwindow")
        self._window.connect("destroy", self.destroy)
        self._btnjumpto = self._wtree.get_object("btnjumpto")
        self._btnjumpto.set_sensitive(False)
        self._entrysearch = self._wtree.get_object("txtsearch")
        self._wtree.connect_signals(self)
        self._lssearch = gtk.ListStore(gtk.gdk.Pixbuf, str, str, str,
                                       str, float)
        self._cellpb = gtk.CellRendererPixbuf()
        self._cellname = gtk.CellRendererText()
        self._cellsize = gtk.CellRendererText()
        self._tvsearchcolname = self._wtree.get_object("tvsearchcolname")
        self._tvsearchcolsize = self._wtree.get_object("tvsearchcolsize")
        self._tvsearchcolname.set_sizing(gtk.TREE_VIEW_COLUMN_FIXED)
        self._tvsearchcolname.set_fixed_width((self._window.get_size()[0])
                                              - 150)
        self._tvsearchcolname.pack_start(self._cellpb, False)
        self._tvsearchcolname.pack_start(self._cellname, False)
        self._tvsearchcolsize.pack_start(self._cellsize, False)
        self._tvsearchcolname.set_attributes(self._cellpb, pixbuf = 0)
        self._tvsearchcolname.set_attributes(self._cellname, markup = 1)
        self._tvsearchcolsize.set_attributes(self._cellsize, text = 2)
        self._tvsearchcolname.set_sort_column_id(1)
        self._tvsearchcolsize.set_sort_column_id(5)
        self._tvsearch = self._wtree.get_object("tvsearch")
        self._tvsearch.set_model(self._lssearch)
        self._tvsearch.columns_autosize()
        self._window.show_all()

    def destroy(self, widget):
        """Destroys the window."""
        if self._window is not None:
            self._window.destroy()
            self._window = None

    def find_text(self, name, text):
        """Returns the result of the search with lowercase values."""
        return name.lower().find(text.lower())

    def search_and_append(self, node, text):
        """Searches in the entire directory structure.
        
        Searches in all available nodes, and if any name matches the specified
        text, appends the node data to the treestore, bold markup-ing the term
        in the name. WARNING: this is not some google magic search, just 
        simple case-insensitive search!
        """
        name2 = node.name.decode("utf-8")
        str2 = node.__str__().decode("utf-8")
        text2 = text.decode("utf-8")
        index = self.find_text(name2, text2)
        if index != -1 and text2 != "":
            namemarkup = name2[0:index]
            namemarkup += "<b>"
            namemarkup += name2[index:index + len(text2)]
            namemarkup += "</b>"
            namemarkup += name2[index + len(text2):len(name2)]
            namemarkup += "\n" + str2
            self._lssearch.append([node.icon, namemarkup.replace("&", "&amp;"),
                                   node.strsize, node.__str__(), node.parent,
                                   node.size])
        if hasattr(node, "dirs"):
            for _dir in node.dirs:
                self.search_and_append(_dir, text)
        if hasattr(node, "files"):
            for _file in node.files:
                self.search_and_append(_file, text)

    #################################
    #Callbacks
    #################################

    def btncancel_clicked_cb(self, widget):
        """Destroys the window."""
        self.destroy()

    def btnjumpto_clicked_cb(self, widget):
        """Binds the "Jump To" button to the row_activated callback.
        
        Gets the necessary data in order to call the row_activated
        callback, so we are not doing things twice.
        """
        (_model, _iter) = self._tvsearch.get_selection().get_selected()
        _path = _model.get_path(_iter)
        _column = self._tvsearch.get_column(0)
        self.tvsearch_row_activated_cb(self._tvsearch, _path, _column)

    def btnsearch_clicked_cb(self, widget):
        """Starts the search."""
        self._lssearch.clear()
        self._tvsearch.columns_autosize()
        self.search_and_append(self._root, self._entrysearch.get_text())

    def txtsearch_activate_cb(self, widget):
        """Starts the search."""
        self.btnsearch_clicked_cb(widget)

    def txtsearch_changed_cb(self, widget):
        """Starts the search."""
        self.btnsearch_clicked_cb(widget)

    def btnclear_clicked_cb(self, widget):
        """Clears the search store."""
        self._lssearch.clear()
        self._btnjumpto.set_sensitive(True)

    def tvsearch_cursor_changed_cb(self, widget):
        """Sets the "Jump To" button sensitive."""
        self._btnjumpto.set_sensitive(True)

    def tvsearch_row_activated_cb(self, tvdt, path, view_column):
        """Jumps to the selected node in the main window.
        
        Gets all needed data and calls the relevant main handler's method
        to jump to the selected node.
        """
        _iter = self._lssearch.get_iter(path)
        _str = self._lssearch.get_value(_iter, 3)
        _parent = self._lssearch.get_value(_iter, 4)
        self._tvhandler.switch_to_node_from_fs_path(_str, _parent)
