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

"""Module for the handler of the treeviews"""

import gtk

import fs.entries

class TVHandler(object):
    
    """Treeviews' handler.
    
    All the treeview-related thingies got separated in this class in order
    to keep things tidy.
    """
    
    def __init__(self, mainhandler, wtree):
        self._indexer = None
        self._root = None
        self._wtree = wtree
        self._mainhandler = mainhandler
        self._pbar = self._wtree.get_object("pbar")
        self._tbsavetree = self._wtree.get_object("tbsave")
        self._tvdirtree = self._wtree.get_object("tvdirtree")
        self._entrysearch = self._wtree.get_object("entrysearch")
        self._tsdirtree = gtk.TreeStore(str, str, str)
        self._tmfdirtree = self._tsdirtree.filter_new()
        self._tmfdirtree.set_visible_func(self._mainhandler.search_in_dirtree)
        self._tvdirtree.set_model(self._tmfdirtree)
        self._crpdirtree = gtk.CellRendererPixbuf()
        self._crnamefilelist = gtk.CellRendererText()
        self._tvcolnamedt = self._wtree.get_object("tvcolnamedt")
        self._tvcolnamedt.pack_start(self._crpdirtree, False)
        self._tvcolnamedt.pack_start(self._crnamefilelist)
        self._tvcolnamedt.add_attribute(self._crpdirtree, 'icon-name', 0)
        self._tvcolnamedt.add_attribute(self._crnamefilelist, 'text', 1)
        self._tvfilelist = self._wtree.get_object("tvfilelist")
        self._lsfilelist = gtk.ListStore(gtk.gdk.Pixbuf, str, str, str)
        self._tmffilelist = self._lsfilelist.filter_new()
        self._tmffilelist.set_visible_func(self._mainhandler.search_in_filelist)
        self._tvfilelist.set_model(self._tmffilelist)
        self._crpfilelist = gtk.CellRendererPixbuf()
        self._crnamefilelist = gtk.CellRendererText()
        self._crsizefilelist = gtk.CellRendererText()
        self._tvcolnamefl = self._wtree.get_object("tvcolnamefl")
        self._tvcolsizefl = self._wtree.get_object("tvcolsizefl")
        self._tvcolnamefl.pack_start(self._crpfilelist, False)
        self._tvcolnamefl.pack_start(self._crnamefilelist, False)
        self._tvcolsizefl.pack_start(self._crsizefilelist, False)
        self._tvcolnamefl.add_attribute(self._crpfilelist, 'pixbuf', 0)
        self._tvcolnamefl.add_attribute(self._crnamefilelist, 'text', 1)
        self._tvcolsizefl.add_attribute(self._crsizefilelist, 'text', 2)
        self._tvfilelist.columns_autosize()
        
    #################################
    #Properties
    #################################    
    def get_root(self):
        """Property"""
        return self._root
    
    def set_root(self, root):
        """Property"""
        
        self._root = root
    
    def get_indexer(self):
        """Property"""
        return self._indexer
    
    def set_indexer(self, indexer):
        """Property"""
        self._indexer = indexer
        
    def get_tmfdirtree(self):
        """Property"""
        return self._tmfdirtree
    
    def get_lsfilelist(self):
        """Property"""
        return self._lsfilelist
    
    def set_lsfilelist(self, lsfilelist):
        """Property"""
        self._lsfilelist = lsfilelist
        
    def get_tvdirtree(self):
        """Property"""
        return self._tvdirtree
    
    def get_tmffilelist(self):
        """Property"""
        return self._tmffilelist
        
    root = property(get_root, set_root)
    indexer = property(get_indexer, set_indexer)
    tmfdirtree = property(get_tmfdirtree)
    lsfilelist = property(get_lsfilelist, set_lsfilelist)
    tvdirtree = property(get_tvdirtree)
    tmffilelist = property(get_tmffilelist)
    
    #################################
    #Methods  
    #################################
    def clear_stores(self):
        """Empties the stores."""
        self._tsdirtree.clear()
        self._lsfilelist.clear()
        
    def append_directories(self, piter, _dir):
        """Adds directories to the left treeview.
        
        Called once after indexing.
        """
        for dirchild in _dir.get_dirs():
            _iter = self._tsdirtree.append(piter, ['folder', dirchild.name,
                                       dirchild.__str__()])
            self.append_directories(_iter, dirchild)
            
    def print_output(self):
        """Populates the directory tree treestore.
        
        This method is called after the indexing process finishes.
        First it populates the left treestore with all the dirs from the
        indexing process. Then does the needed thingies in the GUI to
        keep it consistent.
        """
        #self._tsdirtree.clear()
        self.clear_stores()
        if not self._root:
            self._root = self._indexer.get_root()
        self._mainhandler.root = self._root
        self._rootiter = self._tsdirtree.append(None, ['drive-harddisk', 
                                                       self._root.name + 
                                                       " (" + 
                                                       self._root.strsize +
                                                       ")",
                                                        self._root.__str__()])
        self.append_directories(self._rootiter, self._root)
        self._tbsavetree.set_sensitive(True)
        self._pbar.hide()
        self._wtree.get_object("tbloadfile").set_sensitive(True)
        self._wtree.get_object("tbnewpath").set_sensitive(True)
        self._wtree.get_object("tbsearch").set_sensitive(True)
        
        
    def generate_file_list(self, parent, lsfl):
        """Populate the file list treestore.
        
        This method is called when a directory is selected on the left
        treeview. It populates the right treestore with the contents of
        the selected directory. Has a built-in check for the filter text
        entry.
        """
        lsfl.clear()
        if self._entrysearch.get_text() == "":
            for dirchild in parent.get_dirs():
                lsfl.append([dirchild.icon, dirchild.name,
                             dirchild.strsize, dirchild.__str__()])
            for filechild in parent.get_files():
                lsfl.append([filechild.icon, filechild.name,
                             filechild.strsize, filechild.__str__()])
        else:
            text = self._entrysearch.get_text()
            for dirchild in parent.get_dirs():
                if self._mainhandler.find_cased_string(dirchild.name, text):
                    lsfl.append([dirchild.icon, dirchild.name,
                                 dirchild.strsize, dirchild.__str__()])
            for filechild in parent.get_files():
                if self._mainhandler.find_cased_string(filechild.name, text):
                    lsfl.append([filechild.icon, filechild.name,
                              filechild.strsize, filechild.__str__()])
                    
    def switch_to_node_from_fs_path(self, fs_path, parent):
        """Switch to a node in the structure with a given fs path.
        
        This method is called when something is selected in the search
        window. It receives a path and iterates over the indexed structure
        until it finds the selected node and parent. Then selects the parent
        so the node's directory is loaded in the right treeview.
        """
        #TODO: select the node in the filelist treeview
        self._switching = None
        if self._root.parent == parent:
            for row in self._tsdirtree:
                if row[2] == fs_path:
                    self._switching = row
                    break
        else:
            for row in self._tsdirtree:
                if row[2] == parent:
                    self._switching = row
                    break
                self.iterate_over_children(parent, row)
        self._currentpath = self._switching.path
        self._tvdirtree.expand_to_path(self._currentpath)
        self._tvdirtree.set_cursor(self._currentpath)
                
    def iterate_over_children(self, parent, row):
        """Iterates over the children of a treeview row.
        
        Used in the switch_to_node_from_fs_path method.
        """
        for child in row.iterchildren():
            if child[2] == parent:
                self._switching = child
                break
            self.iterate_over_children(parent, child)

    #################################        
    #Callbacks
    #################################
    def tvdirtree_cursor_changed_cb(self, tvdt):
        """Callback that handles the selection in the directory treeview.
        
        Each time the directory tree selection changes, gets the node which
        was selected and loads its contents in the file list treeview. Some
        variables are saved for consistency and later checks.
        """
        (_model, _iter) = tvdt.get_selection().get_selected()
        self._currentpath = tvdt.get_model().get_path(_iter)
        parent = tvdt.get_model().get_value(_iter, 2)
        self._current = _iter
        self._mainhandler.currentpath = self._currentpath
        self._mainhandler.current = self._current
        self._currentnode = self._mainhandler.\
                                find_dir_with_fs_path(parent, self._root)
        self._mainhandler.currentnode = self._currentnode
        self._tvfilelist.columns_autosize()
        self.generate_file_list(self._currentnode, self._lsfilelist)
        
    def tvfilelist_cursor_changed_cb(self, tvfl):
        """Callback that handles the selection in the file list treeview.
        
        Each time the file list selection changes, gets the selected node
        and calls the main handler's relevant method to update the info pane.
        """
        (_model, _iter) = tvfl.get_selection().get_selected()
        path = tvfl.get_model().get_value(_iter, 3)
        node = self._mainhandler.find_dir_or_file_with_fs_path(path,
                                                               self._root)
        self._mainhandler.set_infopane_content(node)
        
    def tvfilelist_row_activated_cb(self, tvfl, path, view_column):
        """Callback that handles row activation in the file list treeview.
        
        Each time a row is activated in the file list treeview, this method
        checks if it is a directory, and if it is, switchs to it on the left
        treeview, causing it to load the directory contents in the right
        treeview.
        """
        #cursor = self._tvfilelist.get_cursor()
        _iter = tvfl.get_model().get_iter(path)
        fs_path = self._tmffilelist.get(_iter, 3)[0]
        node = self._mainhandler.find_dir_with_fs_path(fs_path, self._root)
        if isinstance(node, fs.entries.Directory):
            activated = tvfl.get_model().get_value(_iter, 3)
            dtcursor = self._tvdirtree.get_cursor()
            path = dtcursor[0]
            curiter = self._tmfdirtree.get_iter(path)
            iterdest = self._tmfdirtree.iter_children(curiter)
            while iterdest is not None:
                if self._tmfdirtree.get_value(iterdest, 2) == activated:
                    break
                iterdest = self._tmfdirtree.iter_next(iterdest)
            path = self._tmfdirtree.get_path(iterdest)
            self._tvdirtree.expand_to_path(path)
            self._tvdirtree.set_cursor(path)
