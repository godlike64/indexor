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
import os
import threading

from logic.input.dbmanager import CATALOGDIR
from logic.midput.search import Crawler

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
        self._wtree.add_from_file(self._gladefile)
        self._window = self._wtree.get_object("searchwindow")
        self._window.connect("destroy", self.destroy)
        self._btnjumpto = self._wtree.get_object("btnjumpto")
        self._btnjumpto.set_sensitive(False)
        self._entrysearch = self._wtree.get_object("txtsearch")
        self._wtree.connect_signals(self)
        self._lssearch = gtk.ListStore(str, str, str, str,
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
        self._tvsearchcolname.add_attribute(self._cellpb, "icon-name", 0)
        self._tvsearchcolname.add_attribute(self._cellname, "markup", 1)
        self._tvsearchcolsize.add_attribute(self._cellsize, "text", 2)
        self._tvsearchcolname.set_sort_column_id(1)
        self._tvsearchcolsize.set_sort_column_id(5)
        self._tvsearch = self._wtree.get_object("tvsearch")
        self._tvsearch.set_model(self._lssearch)
        self._tvsearch.columns_autosize()

        self._lssearchlocations = gtk.ListStore(str, str, str)

        self._tvsearchlocations = self._wtree.get_object("tvsearchlocations")
        self._tvsearchlocations.set_model(self._lssearchlocations)
        self._tvname = self._wtree.get_object("tvname")
        self._tvcount = self._wtree.get_object("tvcount")
        self._celllocpb = gtk.CellRendererPixbuf()
        self._cellnameloc = gtk.CellRendererText()
        self._cellcount = gtk.CellRendererText()
        self._tvname.pack_start(self._celllocpb, False)
        self._tvname.pack_start(self._cellnameloc, False)
        self._tvcount.pack_start(self._cellcount, False)
        self._tvname.add_attribute(self._celllocpb, "icon-name", 0)
        self._tvname.add_attribute(self._cellnameloc, "text", 1)
        self._tvcount.add_attribute(self._cellcount, "text", 2)


        self._crawlers = []
        self._crawlersstore = []
        self._crawlersstore.append(gtk.ListStore(str, str, str, str,
                                       str, float, str, str))
        for catalog in os.listdir(CATALOGDIR):
            crawler = Crawler(self, catalog)
            self._crawlers.append(crawler)
            self._crawlersstore.append(gtk.ListStore(str, str, str, str,
                                                     str, float, str, str))

        self._window.show_all()


    def get_lssearch(self):
        return self._lssearch

    lssearch = property(get_lssearch)

    def destroy(self, widget):
        """Destroys the window."""
        if self._window is not None:
            self._window.destroy()
            self._window = None


    def recreate_searchlocations(self):
        self._lssearchlocations.append(["", "All", "0"])
        for crawler in self._crawlers:
            self._lssearchlocations.append([crawler.metadir.media_type, crawler.name, "0"])

    def clear_liststores(self):
        self._tvsearch.get_selection().unselect_all()
        self._tvsearchlocations.get_selection().unselect_all()
        self._lssearch.clear()
        self._lssearchlocations.clear()
        for store in self._crawlersstore:
            store.clear()
        self._tvsearch.set_model(None)


    def notify_and_add(self, crawler, node):
        index = self._crawlers.index(crawler) + 1
        row = self._lssearchlocations[index]
        row[2] = str(int(row[2]) + 1)
        self._crawlersstore[index].append(node)
        row = self._lssearchlocations[0]
        row[2] = str(int(row[2]) + 1)
        self._crawlersstore[0].append(node)

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

    def txtsearch_activate_cb(self, entry):
        self.clear_liststores()
        self.recreate_searchlocations()
        for crawler in self._crawlers:
            thread = threading.Thread(target = crawler.search, args = (self._entrysearch.get_text(),))
            thread.start()

    def tvsearchlocations_cursor_changed_cb(self, tvsl):
        treeselection = tvsl.get_selection()
        (model, iter_) = treeselection.get_selected()
        path = self._lssearchlocations.get_path(iter_)
        index = path[0]
        self._tvsearch.set_model(self._crawlersstore[index])
        selection = self._tvsearch.get_selection()
        iter_ = selection.get_selected()[1]
        if iter_ is None:
            self._btnjumpto.set_sensitive(False)

    def tvsearch_row_activated_cb(self, tvs, path, view_column):
        treeselection = self._tvsearchlocations.get_selection()
        (model, iter_) = treeselection.get_selected()
        pathloc = self._lssearchlocations.get_path(iter_)
        index = pathloc[0]
        filename = self._crawlersstore[index][path][6]
        parent = self._crawlersstore[index][path][4]
        absname = self._crawlersstore[index][path][3]
        self._mainhandler.load_catalog_from_filename(CATALOGDIR + filename)
        indexpage = self._mainhandler.notebook.get_current_page()
        tvhandler = self._mainhandler.tvhandlers[indexpage]
        tvhandler.switch_to_node_from_fs_path(absname, parent)
        
    def tvsearch_cursor_changed_cb(self, tvsl):
        selection = self._tvsearch.get_selection()
        iter_ = selection.get_selected()[1]
        if iter_ is not None:
            self._btnjumpto.set_sensitive(True)
            
    def btnjumpto_clicked_cb(self, widget):
        treeselection = self._tvsearchlocations.get_selection()
        (model, iter_) = treeselection.get_selected()
        pathloc = self._lssearchlocations.get_path(iter_)
        index = pathloc[0]
        selection = self._tvsearch.get_selection()
        iter_ = selection.get_selected()[1]
        print iter_
        path = self._crawlersstore[index].get_path(iter_)
        print path
        self.tvsearch_row_activated_cb(None, path, None)
        
    def btnclear_clicked_cb(self, widget):
        for store in self._crawlersstore:
            store.clear()
        self._lssearchlocations.clear()
        self._entrysearch.set_text("")
        self._btnjumpto.set_sensitive(False)
        
    def btnsearch_clicked_cb(self, widget):
        self.txtsearch_activate_cb(widget)