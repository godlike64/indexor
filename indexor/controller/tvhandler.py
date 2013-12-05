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
import pango
import gobject
import pynotify

#import fs.entries
from fs.entities import MetaDir, File, Directory, Video, Audio, Photo
from constants import ICONS, MIMES, SEPARATOR
from logic.midput import SETTINGS

class TVHandler(object):

    """Treeviews' handler.
    
    All the treeview-related thingies got separated in this class in order
    to keep things tidy.
    """

    def __init__(self, mainhandler, path):
        self._path = path
        self._dbmanager = None
        self._root = None
        self._is_scanning = False
        self._wtree = gtk.Builder()
        self._wtree.add_from_file("view/scan.glade")
        self._wtree.connect_signals(self)
        self._mainhandler = mainhandler
        self._scanframe = self._wtree.get_object("scanframe")
        self._pbar = self._wtree.get_object("pbar")
        self._btncancel = self._wtree.get_object("btncancel")
        self._tbsavetree = self._wtree.get_object("tbsave")
        self._tvdirtree = self._wtree.get_object("tvdirtree")
        self._entrysearch = self._wtree.get_object("entrysearch")
        self._tsdirtree = gtk.TreeStore(str, str, str)
        self._tmfdirtree = self._tsdirtree.filter_new()
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
        self._hbpbar = self._wtree.get_object("hbpbar")
        self._load_infopane_variables()
        self._hplistpane.set_position(SETTINGS.infopanesize)
        self._hide_after_shown()
        if self._mainhandler.chkmninfopane.get_active() is True:
            self._infopane.show()
        else:
            self._infopane.hide()

    #################################
    #Properties
    #################################    
    def get_root(self):
        """Property"""
        return self._root

    def set_root(self, root):
        """Property"""

        self._root = root

    def get_dbmanager(self):
        """Property"""
        return self._dbmanager

    def set_dbmanager(self, dbmanager):
        """Property"""
        self._dbmanager = dbmanager
        self._conn = dbmanager.conn

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

    def get_hbpbar(self):
        return self._hbpbar

    def get_pbar(self):
        return self._pbar

    def get_infopane(self):
        return self._infopane

    def get_path(self):
        return self._path

    def get_is_scanning(self):
        return self._is_scanning

    def set_is_scanning(self, value):
        self._is_scanning = value

    root = property(get_root, set_root)
    dbmanager = property(get_dbmanager, set_dbmanager)
    tmfdirtree = property(get_tmfdirtree)
    lsfilelist = property(get_lsfilelist, set_lsfilelist)
    tvdirtree = property(get_tvdirtree)
    tmffilelist = property(get_tmffilelist)
    hbpbar = property(get_hbpbar)
    pbar = property(get_pbar)
    infopane = property(get_infopane)
    path = property(get_path)
    is_scanning = property(get_is_scanning, set_is_scanning)

    #################################
    #Methods  
    #################################
    def add_to_viewport(self):
        vwp = gtk.Viewport()
        vwp.add(self._scanframe)
        vwp.show()
        hbox = gtk.HBox(False, 2)
        label = gtk.Label(self._path)
        if SETTINGS.tabellipsize is True:
            label.set_ellipsize(SETTINGS.tabellipplace)
        label.set_width_chars(SETTINGS.tablength)
        hbox.pack_start(label, False)
        button = gtk.Button()
        button.connect("clicked", self._mainhandler.tabbtn_clicked_cb, self)
        button.set_relief(gtk.RELIEF_NONE)
        pixbuf = gtk.icon_theme_get_default().load_icon("process-stop", 16,
                                   gtk.ICON_LOOKUP_NO_SVG)
        image = gtk.image_new_from_pixbuf(pixbuf)
        button.set_image(image)
        hbox.pack_start(button, False)
        hbox.show_all()
        index = self._mainhandler.notebook.append_page(vwp, hbox)
        self._mainhandler.notebook.child_set_property(vwp, "tab-expand", False)
        self._mainhandler.notebook.child_set_property(vwp, "tab-fill", False)
        self._mainhandler.notebook.set_current_page(index)
        self.clear_stores()

    def _load_infopane_variables(self):
        """Create the objects needed for info pane handling."""
        #Pane and tables
        self._vwpinfoimg = self._wtree.get_object("vwpinfoimg")
        self._infopane = self._wtree.get_object("swinfopane")
        self._geninfo = self._wtree.get_object("tblgeninfo")
        self._tblinfoabspath = self._wtree.get_object("tblinfoabspath")
        self._tblinforelpath = self._wtree.get_object("tblinforelpath")
        self._tblinfosize = self._wtree.get_object("tblinfosize")
        self._tblinfomime = self._wtree.get_object("tblinfomime")
        self._tblinfoatime = self._wtree.get_object("tblinfoatime")
        self._tblinfomtime = self._wtree.get_object("tblinfomtime")
        self._tblmediainfo = self._wtree.get_object("tblmediainfo")
        self._tblvideoinfo = self._wtree.get_object("tblvideoinfo")
        self._tblvideocodec = self._wtree.get_object("tblvideocodec")
        self._tblvideobitrate = self._wtree.get_object("tblvideobitrate")
        self._tblvideores = self._wtree.get_object("tblvideores")
        self._tblvideofps = self._wtree.get_object("tblvideofps")
        self._tblvideoar = self._wtree.get_object("tblvideoar")
        self._tblaudioinfo = self._wtree.get_object("tblaudioinfo")
        self._tblaudiobitrate = self._wtree.get_object("tblaudiobitrate")
        self._tblaudiosample = self._wtree.get_object("tblaudiosample")
        self._tblaudiocodec = self._wtree.get_object("tblaudiocodec")
        self._tblaudiochan = self._wtree.get_object("tblaudiochan")
        self._tblaudiochaninfo = self._wtree.get_object("tblaudiochan")
        self._tblsubinfo = self._wtree.get_object("tblsubinfo")
        self._tblsublangs = self._wtree.get_object("tblsublangs")
        self._tblimginfo = self._wtree.get_object("tblimginfo")
        self._tblimgres = self._wtree.get_object("tblimgres")
        self._tblimgdate = self._wtree.get_object("tblimgdate")
        self._tblimgauthor = self._wtree.get_object("tblimgauthor")
        self._tblimgsoft = self._wtree.get_object("tblimgsoft")
        self._tblmedialength = self._wtree.get_object("tblmedialength")
        #Labels
        self._lblinfoname = self._wtree.get_object("lblinfoname")
        self._lblinfoabspath = self._wtree.get_object("lblinfoabspath")
        self._lblinforelpath = self._wtree.get_object("lblinforelpath")
        self._lblinfosize = self._wtree.get_object("lblinfosize")
        self._lblinfomime = self._wtree.get_object("lblinfomime")
        self._lblinfoatime = self._wtree.get_object("lblinfoatime")
        self._lblinfomtime = self._wtree.get_object("lblinfomtime")
        self._lblmedialength = self._wtree.get_object("lblmedialength")
        self._lblvideocodec = self._wtree.get_object("lblvideocodec")
        self._lblvideobitrate = self._wtree.get_object("lblvideobitrate")
        self._lblvideores = self._wtree.get_object("lblvideores")
        self._lblvideofps = self._wtree.get_object("lblvideofps")
        self._lblvideoar = self._wtree.get_object("lblvideoar")
        self._lblaudiobitrate = self._wtree.get_object("lblaudiobitrate")
        self._lblaudiosample = self._wtree.get_object("lblaudiosample")
        self._lblaudiocodec = self._wtree.get_object("lblaudiocodec")
        self._lblaudiochan = self._wtree.get_object("lblaudiochan")
        self._lblsublangs = self._wtree.get_object("lblsublangs")
        self._lblimgres = self._wtree.get_object("lblimgres")
        self._lblimgdate = self._wtree.get_object("lblimgdate")
        self._lblimgauthor = self._wtree.get_object("lblimgauthor")
        self._lblimgsoft = self._wtree.get_object("lblimgsoft")
        self._hptreelist = self._wtree.get_object("hptreelist")
        self._hplistpane = self._wtree.get_object("hplistpane")

    def _hide_after_shown(self):
        """Hide things that should not be shown immediately."""
        self._hbpbar.hide()
        self._infopane.hide()
        self._tblmediainfo.hide()
        self._tblimginfo.hide()
        self._tblaudioinfo.hide()
        self._tblsubinfo.hide()
        self._tblvideoinfo.hide()

    def clear_stores(self):
        """Empties the stores."""
        self._tsdirtree.clear()
        self._lsfilelist.clear()

    def append_directories(self, piter, _dir):
        """Adds directories to the left treeview.
        
        Called once after indexing.
        """
        for dirchild in _dir.dirs:
            _iter = self._tsdirtree.append(piter, ['folder', dirchild.name,
                                       dirchild.__str__()])
            self.append_directories(_iter, dirchild)

    def check_if_counting_finished(self, fscountthread):
        """Checks if the counting process finished.
        
        If Indexor has finished counting files, starts indexing them.
        Called from gobject.timeout_add.
        """
        if not fscountthread.is_alive():
            fsindexthread = self._dbmanager.start_indexing()
            gobject.timeout_add(500, self.check_if_indexing_finished,
                                fsindexthread)
            return False
        else:
            return True

    def check_if_indexing_finished(self, fsindexthread):
        """Checks if the indexing process finished.
        
        If Indexor has finished indexing files, orders the TVHandler
        to populate the treeviews. Called from gobject.timeout_add.
        """
        if not fsindexthread.is_alive():
            self._root = None
            self.print_output()
            print "Total time consumed: " + str(self._dbmanager.\
                                                get_time_consumed()) + " ms."
            return False
        else:
            return True

    def print_output(self):
        """Populates the directory tree treestore.
        
        This method is called after the indexing process finishes.
        First it populates the left treestore with all the dirs from the
        indexing process. Then does the needed thingies in the GUI to
        keep it consistent.
        """
        
        self._is_scanning = False
        self._dbmanager.create_metadir()
        self._dbmanager.set_root_node()
        rootselect = Directory.select(Directory.q.relpath == "/",
                                      connection = self._conn)
        root = rootselect[0]
        self._root = root
        self._mainhandler.populate_catalog_list()
        if self._root is not None:
            self._mainhandler.root = self._root
            self._rootiter = self._tsdirtree.append(None,
                                                    ['drive-harddisk',
                                                     self._root.name + 
                                                     " (" + 
                                                     self._root.strsize + 
                                                     ")",
                                                     self._root.__str__()])
            self.append_directories(self._rootiter, self._root)
            gobject.timeout_add(2000, self.hide_progressbar)
        self._mainhandler.set_buttons_sensitivity(True)
        notification = pynotify.Notification("Indexing finished", "Indexing of " + root.name + " has finished successfully.")
        notification.show()


    def generate_file_list(self, parent, lsfl):
        """Populate the file list treestore.
        
        This method is called when a directory is selected on the left
        treeview. It populates the right treestore with the contents of
        the selected directory. Has a built-in check for the filter text
        entry.
        """
        lsfl.clear()
        for dirchild in parent.dirs:
            lsfl.append([gtk.icon_theme_get_default().\
                         load_icon(ICONS[MIMES[dirchild.mimetype]],
                                   SETTINGS.iconlistsize,
                                   gtk.ICON_LOOKUP_FORCE_SVG),
                                   dirchild.name, dirchild.strsize,
                                   dirchild.__str__()])
        for filechild in parent.files:
            if isinstance(filechild, Photo) \
            and filechild.hasthumb is True:
                lsfl.append([filechild.icon, filechild.name,
                             filechild.strsize, filechild.__str__()])
            else:
                lsfl.append([gtk.icon_theme_get_default().\
                             load_icon(ICONS[MIMES[filechild.mimetype]],
                                       SETTINGS.iconlistsize,
                                       gtk.ICON_LOOKUP_FORCE_SVG),
                                       filechild.name, filechild.strsize,
                                       filechild.__str__()])

    def switch_to_node_from_fs_path(self, fs_path, parent):
        """Switch to a node in the structure with a given fs path.
        
        This method is called when something is selected in the search
        window. It receives a path and iterates over the indexed structure
        until it finds the selected node and parent. Then selects the parent
        so the node's directory is loaded in the right treeview.
        """
        #print fs_path
        #print parent
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
        for row in self._lsfilelist:
            if row[3] == fs_path:
                self._tvfilelist.set_cursor(row.path)

    def iterate_over_children(self, parent, row):
        """Iterates over the children of a treeview row.
        
        Used in the switch_to_node_from_fs_path method.
        """
        for child in row.iterchildren():
            if child[2] == parent:
                self._switching = child
                break
            self.iterate_over_children(parent, child)

    def _iterate_inside(self, parentiter, activated):
        for row in parentiter.iterchildren():
            if activated == row[2]:
                self._candidate = row.iter
            self._iterate_inside(row, activated)

    def _clear_infopane(self):
        """Hides all non-common attributes from the info pane."""
        self._tblmediainfo.hide()
        self._tblaudioinfo.hide()
        self._tblaudiochaninfo.hide()
        self._tblsubinfo.hide()
        self._tblvideoinfo.hide()
        self._tblimginfo.hide()

    def set_infopane_content(self, node):
        """Sets the labels of the info pane.
        
        This method is called each time an entry is selected in the file
        list. Then sets the info pane labels to the correct values.
        """
        self._selected = node
        self._clear_infopane()
        self._lblinfoname.set_text(node.name)
        self._lblinfoabspath.set_text(node.parent + SEPARATOR)
        self._lblinforelpath.set_text(node.relpath)
        self._lblinfosize.set_text(node.strsize)
        self._lblinfomime.set_text(node.mimetype)
        self._lblinfoatime.set_text(node.atime)
        self._lblinfomtime.set_text(node.mtime)
        if hasattr(self, "_infoimg"):
            self._vwpinfoimg.remove(self._infoimg)

        #======================================================================
        # if isinstance(node, Directory):
        #    self._infoimg = gtk.image_new_from_pixbuf\
        #                        (gtk.icon_theme_get_default().\
        #                         load_icon('folder', SETTINGS.iconpanesize,
        #                                   gtk.ICON_LOOKUP_FORCE_SVG))
        #    self._lblinfomime.set_text("folder")
        #======================================================================
        if isinstance(node, Photo):
            self._infoimg = gtk.image_new_from_pixbuf(node.thumb)
            self._lblimgres.set_text(node.res)
            self._lblimgdate.set_text(node.date_taken)
            self._lblimgauthor.set_text(node.author)
            self._lblimgsoft.set_text(node.soft)
            self._tblimginfo.show()
        else:
            if isinstance(node, Audio):
                self._tblmediainfo.show()
                self._tblaudioinfo.show()
                self._lblmedialength.set_text(node.length)
                self._lblaudiobitrate.set_text(node.bitrate)
                self._lblaudiosample.set_text(node.samplerate)
                self._lblaudiocodec.set_text(node.codec)
            if isinstance(node, Video):
                self._tblmediainfo.show()
                self._tblaudioinfo.show()
                self._tblaudiochaninfo.show()
                self._tblvideoinfo.show()
                if hasattr(node, "_sublangs"):
                    self._tblsubinfo.show()
                    self._lblsublangs.set_text(node.sublangs)
                print node.length
                self._lblmedialength.set_text(node.length)
                self._lblvideocodec.set_text(node.videocodec)
                self._lblvideobitrate.set_text(node.videobitrate)
                self._lblvideores.set_text(node.videores)
                self._lblvideofps.set_text(node.videofps)
                self._lblvideoar.set_text(node.videoar)
                self._lblaudiobitrate.set_text(node.audiobitrate)
                self._lblaudiosample.set_text(node.audiosamplerate)
                self._lblaudiocodec.set_text(node.audiocodec)
                self._lblaudiochan.set_text(node.audiochannels)
            self._infoimg = gtk.image_new_from_pixbuf\
                                (gtk.icon_theme_get_default().\
                                 load_icon(ICONS[MIMES[node.mimetype]],
                                           SETTINGS.iconpanesize,
                                           gtk.ICON_LOOKUP_FORCE_SVG))
        self._infoimg.show()
        self._vwpinfoimg.add(self._infoimg)
        self.set_infopanes_visibility()

    def set_infopanes_visibility(self):
        """Sets the visibility of each label, according to stored settings"""
        self._geninfo.set_property("visible", SETTINGS.geninfo)
        self._tblinfoabspath.set_property("visible", SETTINGS.abspath)
        self._tblinforelpath.set_property("visible", SETTINGS.relpath)
        self._tblinfosize.set_property("visible", SETTINGS.size)
        self._tblinfomime.set_property("visible", SETTINGS.mime)
        self._tblinfoatime.set_property("visible", SETTINGS.atime)
        self._tblinfomtime.set_property("visible", SETTINGS.mtime)
        self._tblmediainfo.set_property("visible", SETTINGS.mediainfo)
        self._tblmedialength.set_property("visible", SETTINGS.medialength)
        self._tblvideoinfo.set_property("visible", SETTINGS.videoinfo)
        self._tblvideocodec.set_property("visible", SETTINGS.videocodec)
        self._tblvideobitrate.set_property("visible", SETTINGS.videobitrate)
        self._tblvideores.set_property("visible", SETTINGS.videores)
        self._tblvideofps.set_property("visible", SETTINGS.videofps)
        self._tblvideoar.set_property("visible", SETTINGS.videoar)
        self._tblaudioinfo.set_property("visible", SETTINGS.audioinfo)
        self._tblaudiosample.set_property("visible", SETTINGS.audiosample)
        self._tblaudiocodec.set_property("visible", SETTINGS.audiocodec)
        self._tblaudiochan.set_property("visible", SETTINGS.audiochan)
        self._tblsubinfo.set_property("visible", SETTINGS.subinfo)
        self._tblsublangs.set_property("visible", SETTINGS.sublangs)
        self._tblimginfo.set_property("visible", SETTINGS.imginfo)
        self._tblimgres.set_property("visible", SETTINGS.imgres)
        self._tblimgdate.set_property("visible", SETTINGS.imgdate)
        self._tblimgauthor.set_property("visible", SETTINGS.imgauthor)
        self._tblimgsoft.set_property("visible", SETTINGS.imgsoft)
        if isinstance(self._selected, Audio):
            self._tblimginfo.hide()
            self._tblvideoinfo.hide()
            self._tblsubinfo.hide()
            self._tblaudiochaninfo.hide()
        elif isinstance(self._selected, Video):
            self._tblimginfo.hide()
        elif isinstance(self._selected, Photo):
            self._tblmediainfo.hide()
            self._tblvideoinfo.hide()
            self._tblaudioinfo.hide()
            self._tblsubinfo.hide()
        else:
            self._tblimginfo.hide()
            self._tblmediainfo.hide()
            self._tblvideoinfo.hide()
            self._tblaudioinfo.hide()
            self._tblsubinfo.hide()

    def hide_progressbar(self):
        """This is refactored into a method because other classes use it"""
        self._hbpbar.hide()

    #################################        
    #Callbacks
    #################################
    def btncancel_clicked_cb(self, widget):
        """Callback used when cancelling the indexing process"""
        self._dbmanager.stop = True
        self._pbar.set_text("Indexing process of " + self._path + 
                            " cancelled.")
        gobject.timeout_add(1000, self.hide_progressbar)
        gobject.timeout_add(2000, self._mainhandler.remove_scan, self)

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
        #self._currentnode = self._mainhandler.\
        #                        find_dir_with_fs_path(parent, self._root)
        self._currentnode = Directory.select(Directory.q.strabs == parent,
                                             connection = self._conn)[0]
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
        #node = self._mainhandler.find_dir_or_file_with_fs_path(path,
        #                                                       self._root)
        node = File.select(File.q.strabs == path, connection = self._conn)
        node = node[0]
        self.set_infopane_content(node)

    def tvfilelist_row_activated_cb(self, tvfl, path, view_column):
        """Callback that handles row activation in the file list treeview.
        
        Each time a row is activated in the file list treeview, this method
        checks if it is a directory, and if it is, switchs to it on the left
        treeview, causing it to load the directory contents in the right
        treeview.
        """
        _iter = tvfl.get_model().get_iter(path)
        fs_path = self._tmffilelist.get(_iter, 3)[0]
        nodelist = Directory.select(Directory.q.strabs == fs_path,
                                    connection = self._conn)
        if nodelist.count() == 1:
            node = nodelist[0]
            activated = tvfl.get_model().get_value(_iter, 3)
            dtcursor = self._tvdirtree.get_cursor()
            parentiter = iter(self._tmfdirtree).next()
            self._candidate = None
            self._iterate_inside(parentiter, activated)
            path = self._tmfdirtree.get_path(self._candidate)
            self._tvdirtree.expand_to_path(path)
            self._tvdirtree.set_cursor(path)

    #Info pane labels size fix
    def hplistpane_size_allocate_cb(self, widget, alloc):
        """Callback to detect a change in the info pane size."""
        result = self.get_pane_width()
        self.set_labels_sizes(result - 22)

    def get_pane_width(self):
        """Calculates and returns the info pane's width."""
        firststep = self._hptreelist.get_position()
        secondstep = self._hplistpane.get_position()
        idle = 12
        total = self._scanframe.get_allocation().width
        result = total - idle - firststep - secondstep
        return result

    def set_labels_sizes(self, width):
        """Resizes the labels so they wrap accordingly.
        
        This method is called each time the slider for the info pane
        is moved.
        """
        if width < 200:
            pass
        else:
            self._lblinfoname.set_size_request(width - 80, -1)
            self._lblinfoabspath.set_size_request(width - 80, -1)
            self._lblinforelpath.set_size_request(width - 80, -1)
            self._lblinfosize.set_size_request(width - 80, -1)
            self._lblinfomime.set_size_request(width - 80, -1)
            self._lblinfoatime.set_size_request(width - 80, -1)
            self._lblinfomtime.set_size_request(width - 80, -1)
            self._lblmedialength.set_size_request(width - 80, -1)
            self._lblvideocodec.set_size_request(width - 80, -1)
            self._lblvideobitrate.set_size_request(width - 80, -1)
            self._lblvideores.set_size_request(width - 80, -1)
            self._lblvideofps.set_size_request(width - 80, -1)
            self._lblvideoar.set_size_request(width - 80, -1)
            self._lblaudiobitrate.set_size_request(width - 80, -1)
            self._lblaudiosample.set_size_request(width - 80, -1)
            self._lblaudiocodec.set_size_request(width - 80, -1)
            self._lblaudiochan.set_size_request(width - 80, -1)
            self._lblimgres.set_size_request(width - 80, -1)
            self._lblimgdate.set_size_request(width - 80, -1)
            self._lblimgauthor.set_size_request(width - 80, -1)
            self._lblimgsoft.set_size_request(width - 80, -1)
            self._lblsublangs.set_size_request(width - 80, -1)

