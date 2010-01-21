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

"""Module for the handler of the main window"""

#Local imports
import fs.entries as entries
from logic.input.indexer import Indexer
from logic.output.binary import BinaryReader, BinaryWriter
from logic.output.plaintext import PlainTextWriter
from tvhandler import TVHandler
from searchhandler import SearchHandler
from settingshandler import SettingsHandler
from logic.midput import LOADER, SETTINGS
#from controller import LOGHANDLER
from controller.loghandler import LogHandler
from controller.abouthandler import AboutHandler
from logic.logging import MANAGER

#Regular imports
import gobject
import pygtk
pygtk.require('2.0')
import gtk


class MainHandler(object):

    """Main window handler.
    
    Grabs all events from the main window, and passes those relevant to the
    treeviews to the TVHandler. And the rest, is magic ;-).
    """
    
    def __init__(self, gladefile):
        #======================================================================
        # MANAGER.loghandler = LOGHANDLER
        # LOGHANDLER.mainhandler = self
        #======================================================================
        self._indexer = None
        self._root = None
        self._rootiter = None
        self._path = None
        self._current = None
        self._currentnode = None
        self._currentpath = None
        self._selected = None
        self._gladefile = gladefile
        self._wtree = gtk.Builder()
        self._wtree.add_from_file(self._gladefile)
        self._window = self._wtree.get_object("mainwindow")
        self._hbpbar = self._wtree.get_object("hbpbar")
        self._pbar = self._wtree.get_object("pbar")
        self._btncancel = self._wtree.get_object("btncancel")
        self._tvhandler = TVHandler(self, self._wtree)
        self._window.drag_dest_set(gtk.DEST_DEFAULT_DROP,
                                   [('text/plain', 0, 0)], 0)
        self._window.connect("configure-event", self._configure)
        self._window.connect("destroy", self._destroy)
        self._window.connect("drag_motion", self.motion_cb)
        self._window.connect("drag_data_received", self.got_data_cb)
        self._window.connect("window-state-event", self.view_state)
        self._imgmnscan = self._wtree.get_object("imgmnscan")
        self._imgmnload = self._wtree.get_object("imgmnload")
        self._imgmnsaveas = self._wtree.get_object("imgmnsaveas")
        self._tbsearch = self._wtree.get_object("tbsearch")
        self._tbsearch.set_sensitive(False)
        self._tbnewpath = self._wtree.get_object("tbnewpath")
        self._tbsave = self._wtree.get_object("tbsave")
        self._tbloadfile = self._wtree.get_object("tbloadfile")
        self._current = None
        self._currentnode = None
        self._currentpath = None
        self._entrysearch = self._wtree.get_object("entrysearch")
        
        self._chkmnlog = self._wtree.get_object("chkmnlog")
        
        self._load_infopane_variables()
        self._wtree.connect_signals(self)
        self._window.set_default_size(*SETTINGS.windowsize)
        self._hplistpane.set_position(SETTINGS.infopanesize)
        if SETTINGS.windowmax is True:
            self._window.maximize()
        self._window.show_all()
        self._hide_after_shown()

    #################################
    #Properties
    #################################
    def get_currentpath(self):
        """Property"""
        return self._currentpath

    def set_currentpath(self, currentpath):
        """Property"""
        self._currentpath = currentpath

    def get_currentnode(self):
        """Property"""
        return self._currentnode

    def set_currentnode(self, currentnode):
        """Property"""
        self._currentnode = currentnode

    def get_current(self):
        """Property"""
        return self._current

    def set_current(self, current):
        """Property"""
        self._current = current

    def get_root(self):
        """Property"""
        return self._root

    def set_root(self, root):
        """Property"""
        self._root = root
        
    def get_chkmnlog(self):
        """Property"""
        return self._chkmnlog
    
    def get_window(self):
        """Property"""
        return self._window

    currentpath = property(get_currentpath, set_currentpath)
    currentnode = property(get_currentnode, set_currentnode)
    current = property(get_current, set_current)
    root = property(get_root, set_root)
    chkmnlog = property(get_chkmnlog)
    window = property(get_window)

    #################################
    #Methods
    #################################
    def _destroy(self, widget):
        """Destroys the window."""
        SETTINGS.infopanesize = self._hplistpane.get_position()
        LOADER.save_settings()
        gtk.main_quit()
        
    def _hide_after_shown(self):
        """Hide things that should not be shown immediately."""
        self._hbpbar.hide()
        self._infopane.hide()
        self._entrysearch.hide()
        self._tblmediainfo.hide()
        self._tblimginfo.hide()
        self._tblaudioinfo.hide()
        self._tblsubinfo.hide()
        self._tblvideoinfo.hide()
        
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
        self._lblinfoabspath.set_text(node.parent + entries.SEPARATOR)
        self._lblinforelpath.set_text(node.relpath)
        self._lblinfosize.set_text(node.strsize)
        self._lblinfomime.set_text(node.mimetype)
        self._lblinfoatime.set_text(node.atime)
        self._lblinfomtime.set_text(node.mtime)
        if hasattr(self, "_infoimg"):
            self._vwpinfoimg.remove(self._infoimg)

        if isinstance(node, entries.Directory):
            self._infoimg = gtk.image_new_from_pixbuf\
                                (gtk.icon_theme_get_default().\
                                 load_icon('folder', SETTINGS.iconpanesize,
                                           gtk.ICON_LOOKUP_FORCE_SVG))
            self._lblinfomime.set_text("folder")
        elif isinstance(node, entries.Photo):
            self._infoimg = gtk.image_new_from_pixbuf(node.thumb)
            self._lblimgres.set_text(node.res)
            self._lblimgdate.set_text(node.date_taken)
            self._lblimgauthor.set_text(node.author)
            self._lblimgsoft.set_text(node.soft)
            self._tblimginfo.show()
        else:
            if isinstance(node, entries.Audio):
                self._tblmediainfo.show()
                self._tblaudioinfo.show()
                self._lblmedialength.set_text(node.length)
                self._lblaudiobitrate.set_text(node.bitrate)
                self._lblaudiosample.set_text(node.samplerate)
                self._lblaudiocodec.set_text(node.codec)
            if isinstance(node, entries.Video):
                self._tblmediainfo.show()
                self._tblaudioinfo.show()
                self._tblaudiochaninfo.show()
                self._tblvideoinfo.show()
                if hasattr(node, "_sublangs"):
                    self._tblsubinfo.show()
                    self._lblsublangs.set_text(node.sublangs)
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
                                 load_icon(entries.ICONS[entries.MIMES
                                                        [node.mimetype]], 120,
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
        if isinstance(self._selected, entries.Audio):
            self._tblimginfo.hide()
            self._tblvideoinfo.hide()
            self._tblsubinfo.hide()
            self._tblaudiochaninfo.hide()
        elif isinstance(self._selected, entries.Video):
            self._tblimginfo.hide()
        elif isinstance(self._selected, entries.Photo):
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

    def get_pane_width(self):
        """Calculates and returns the info pane's width."""
        firststep = self._hptreelist.get_position()
        secondstep = self._hplistpane.get_position()
        idle = 12
        total = self._window.get_allocation().width
        result = total - idle - firststep - secondstep
        return result
    
    def set_pane_width(self, width):
        """Sets the pane's width. Used when restoring settings"""
        firststep = self._hptreelist.get_position()
        idle = 12
        total = self._window.get_allocation().width
        secondstep = total - idle - firststep - width
        self._hplistpane.set_position(secondstep)

    def init_index_process(self):
        """Starts the indexing process.
        
        Fires up the relevant methods in a thread. Then checks if something
        was already indexed, and clears the environment accordingly.
        """
        if (self._path is not None):
            self.set_buttons_sensitivity(False)
            self._indexer = Indexer(self._path, 
                                    self._pbar, self)
            fscountthread = self._indexer.start_counting()
            self._tvhandler.indexer = self._indexer
            gobject.timeout_add(500, self.check_if_counting_finished,
                                fscountthread)
        if (hasattr(self, "_root")):
            self._root = None
            self._tvhandler.root = None
            self._tvhandler.clear_stores()
            self._pbar.set_text("")
            self._hbpbar.show()
        
    def find_dir_with_fs_path(self, path, root):
        """Finds a directory with a given path"""
        if root.__str__() == path:
            return root
        else:
            for _dir in root.get_dirs():
                if (self.find_dir_with_fs_path(path, _dir) is not None):
                    return self.find_dir_with_fs_path(path, _dir)

    def find_dir_or_file_with_fs_path(self, path, root):
        """Finds a directory or a file with a given path"""
        if root.__str__() == path:
            return root
        else:
            if hasattr(root, "dirs"):
                for _dir in root.dirs:
                    if (self.find_dir_or_file_with_fs_path(path, _dir)
                        is not None):
                        return self.find_dir_or_file_with_fs_path(path, _dir)
            if hasattr(root, "files"):
                for _file in root.files:
                    if (self.find_dir_or_file_with_fs_path(path, _file)
                        is not None):
                        return self.find_dir_or_file_with_fs_path(path, _file)

    def find_cased_dir_or_file(self, text, root):
        """Checks if a dir or file match the specified text.
        
        Used when filtering in treeviews.
        """
        if root.name.lower().find(text.lower()) != -1:
            return True
        else:
            for _dir in root.get_dirs():
                if self.find_cased_dir_or_file(text, _dir):
                    return True
            for _file in root.get_files():
                if self.find_cased_file(text, _file):
                    return True

    def find_cased_file(self, text, _file):
        """Checks if a file name matches the specified text."""
        if hasattr(_file, "name"):
            if _file.name.lower().find(text.lower()) != -1:
                return True

    def find_cased_string(self, name, text):
        """Checks if name contains text.
        
        Used when filtering in treeviews.
        """
        if name.lower().find(text.lower()) != -1:
            return True
        else:
            return False

    def check_if_counting_finished(self, fscountthread):
        """Checks if the counting process finished.
        
        If Indexor has finished counting files, starts indexing them.
        Called from gobject.timeout_add.
        """
        if not fscountthread.is_alive():
            fsindexthread = self._indexer.start_indexing()
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
            self._tvhandler.print_output()
            return False
        else:
            return True

    def search_in_dirtree(self, model, _iter):
        """Filtering function for directory tree treeview filter."""
        text = self._entrysearch.get_text()
        if text == "" or model.get_value(_iter, 1) is None:
            return True
        node = self.find_dir_with_fs_path(model.get_value(_iter, 2),
                                           self._root)
        if self.find_cased_dir_or_file(text, node) is True:
            return True
        else:
            return False

    def search_in_filelist(self, model, _iter):
        """Filtering function for file list treeview filter."""
        text = self._entrysearch.get_text()
        if text == "" or model.get_value(_iter, 1) is None:
            return True
        node = self.find_dir_or_file_with_fs_path\
                (model.get_value(_iter, 2), self._root)
        if self.find_cased_file(text, node) is True:
            return True
        else:
            return False
    
    def hide_progressbar(self):
        """This is refactored into a method because other classes use it"""
        self._hbpbar.hide()
        
    def set_buttons_sensitivity(self, sensitive):
        """Sets buttons (and menus) sensitivity according to value given
        
        This method is used when the indexing process begins or ends.
        """
        if sensitive is True:
            self._btncancel.hide()
        else:
            self._btncancel.show()
        self._tbnewpath.set_sensitive(sensitive)
        self._tbloadfile.set_sensitive(sensitive)
        self._imgmnscan.set_sensitive(sensitive)
        self._imgmnload.set_sensitive(sensitive)
        if hasattr(self, "_root") and self._root is not None:
            self._tbsave.set_sensitive(True)
            self._imgmnsaveas.set_sensitive(True)
        else:
            self._tbsave.set_sensitive(False)
            self._imgmnsaveas.set_sensitive(False)

    #################################
    #Callbacks
    #################################
    def tvdirtree_cursor_changed_cb(self, tvdt):
        """Callback redirected to TVHandler."""
        self._tvhandler.tvdirtree_cursor_changed_cb(tvdt)

    def tvfilelist_cursor_changed_cb(self, tvfl):
        """Callback redirected to TVHandler."""
        self._tvhandler.tvfilelist_cursor_changed_cb(tvfl)

    def tvfilelist_row_activated_cb(self, tvdt, path, view_column):
        """Callback redirected to TVHandler."""
        self._tvhandler.tvfilelist_row_activated_cb(tvdt, path, view_column)

    def tbnewpath_clicked_cb(self, widget):
        """Shows the "New Path" dialog."""
        opendialog = \
        gtk.FileChooserDialog(title="Point me a path...",
                              parent = self._window,
                              action = gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER, 
                              buttons = (gtk.STOCK_CANCEL, 
                                         gtk.RESPONSE_CANCEL,
                                         gtk.STOCK_OK, gtk.RESPONSE_OK))
        response = opendialog.run()
        if response == gtk.RESPONSE_OK:
            self._tvhandler.clear_stores()
            self._infopane.hide()
            #if self._entrysearch.get_text() != "":
                #self._entrysearch.set_text("")
                #self.entrysearch_changed_cb(self._entrysearch)
            self._path = opendialog.get_filename()
            if hasattr(self, "_searchhandler"):
                self._searchhandler.destroy(self._window)
            self._tbsearch.set_sensitive(False)
            self._tbloadfile.set_sensitive(False)
            self.init_index_process()
        opendialog.destroy()

    def tbsave_clicked_cb(self, widget):
        """Shows the "Save" dialog."""
        savedialog = \
        gtk.FileChooserDialog(title="Point me a destination...",
                              parent = self._window,
                              action = gtk.FILE_CHOOSER_ACTION_SAVE,
                              buttons = (gtk.STOCK_CANCEL,
                                         gtk.RESPONSE_CANCEL,
                                         gtk.STOCK_OK, gtk.RESPONSE_OK))
        plainfilter = gtk.FileFilter()
        plainfilter.add_mime_type("text/plain")
        plainfilter.set_name("Plain text")
        binaryfilter = gtk.FileFilter()
        binaryfilter.add_pattern("*.gz")
        binaryfilter.set_name("Binary file")
        savedialog.add_filter(binaryfilter)
        savedialog.add_filter(plainfilter)
        savedialog.set_do_overwrite_confirmation(True)
        response = savedialog.run()
        if response == gtk.RESPONSE_OK:
            if savedialog.get_filter() == binaryfilter:
                BinaryWriter(savedialog.get_filename(), self._root)
            if savedialog.get_filter() == plainfilter:
                PlainTextWriter(savedialog.get_filename(), self._root)
        savedialog.destroy()

    def tbloadfile_clicked_cb(self, widget):
        """Shows the "Load" dialog."""
        opendialog = \
        gtk.FileChooserDialog(title = "Point me a source...",
                              parent = self._window,
                              action = gtk.FILE_CHOOSER_ACTION_OPEN,
                              buttons = (gtk.STOCK_CANCEL,
                                         gtk.RESPONSE_CANCEL,
                                         gtk.STOCK_OK, gtk.RESPONSE_OK))
        response = opendialog.run()
        if response == gtk.RESPONSE_OK:
            self._infopane.hide()
            self._tvhandler.clear_stores()
            binreader = BinaryReader(opendialog.get_filename())
            opendialog.destroy()
            if hasattr(self, "_searchhandler"):
                self._searchhandler.destroy(self._window)
            self._root = binreader.get_root()
            self._tvhandler.root = self._root
            self._tvhandler.print_output()

    def entrysearch_changed_cb(self, widget):
        """Callback used for the filtering text entry."""
        #self._tmfdirtree.refilter()
        #self.generate_file_list(self._currentnode,
                                #self._tvhandler.lsfilelist)
        #gobject.idle_add(self.generate_file_list, self._currentnode,
                         #self._tvhandler.lsfilelist)
        pass

    def tbsearch_clicked_cb(self, widget):
        """Shows the search window.
        
        Creates a new SearchHandler and shows its window.
        """
        self._searchhandler = SearchHandler("view/search.glade", self,
                                            self._tvhandler)

    def btncancel_clicked_cb(self, widget):
        """Callback used when cancelling the indexing process"""
        self._indexer.stop = True
        self._pbar.set_text("Indexing process of " + self._path +
                            " cancelled.")
        gobject.timeout_add(2000, self.hide_progressbar)

    #Menu
    def imgmnscan_activate_cb(self, widget):
        """Redirects to "tbnew" method"""
        self.tbnewpath_clicked_cb(widget)
        
    def imgmnload_activate_cb(self, widget):
        """Redirects to "tbload" method"""
        self.tbloadfile_clicked_cb(widget)
        
    def imgmnsaveas_activate_cb(self, widget):
        """Redirects to "tbsave" method"""
        self.tbsave_clicked_cb(widget)
        
    def imgmnquit_activate_cb(self, widget):
        """Quits the program"""
        if self._indexer is not None:
            self.btncancel_clicked_cb(widget)
        self._destroy(widget)
        
    def chkmnlog_toggled_cb(self, widget):
        """Shows/hides the log viewer window"""
        if widget.get_active() is True:
            self._loghandler = LogHandler(self)
            MANAGER.loghandler = self._loghandler
        else:
            MANAGER.loghandler = None
            self._loghandler.btnclose_clicked_cb(self)
            self._loghandler = None
            
    def chkmninfopane_toggled_cb(self, widget):
        """Shows/hides the info pane."""
        if widget.get_active():
            self._infopane.show()
        else:
            self._infopane.hide()
            
    def imgmnsettings_activate_cb(self, widget):
        """Shows the options window"""
        self._settings = SettingsHandler(self)

    def imgmnabout_activate_cb(self, widget):
        """Shows the about window"""
        AboutHandler(self)

    #Info pane labels size fix
    def hplistpane_size_allocate_cb(self, widget, alloc):
        """Callback to detect a change in the info pane size."""
        result = self.get_pane_width()
        self.set_labels_sizes(result - 22)

    #Drag and drop
    def motion_cb(self, wid, context, dim_x, dim_y, time):
        """First callback needed for drag & drop."""
        context.drag_status(gtk.gdk.ACTION_COPY, time)
        return True

    def got_data_cb(self, wid, context, dim_x, dim_y, data, info, time):
        """Second callback needed for drag & drop.
        
        Extracts the string from the object dragged, sets it as the path
        to scan, and indexes it.
        """
        datamod = data.get_text()[7:]
        if data.get_text()[-1] == "\n":
            datamod = datamod[:-1]
        datamod.encode("utf-8")
        self._path = datamod
        self.init_index_process()
        
    def view_state(self, widget, event):
        """view state callback, to store wether the window is maximized"""
        if event.new_window_state == gtk.gdk.WINDOW_STATE_MAXIMIZED:
            SETTINGS.windowmax = True
        else:
            SETTINGS.windowmax = False
            
    def _configure(self, widget, event):
        """Configure event callback, used to store the window size"""
        SETTINGS.windowsize = (event.width, event.height)
