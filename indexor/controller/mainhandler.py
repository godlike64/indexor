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



#Regular imports
import gobject
import pygtk
pygtk.require('2.0')
import gtk
import shutil
import os
import sys

#Local imports
from fs.entities import File, Directory, Video, Audio, Photo
from constants import ICONS, MIMES, SEPARATOR
from logic.input.indexer import Indexer
from logic.output.plaintext import PlainTextWriter
from tvhandler import TVHandler
from searchhandler import SearchHandler
from settingshandler import SettingsHandler
from logic.midput import LOADER, SETTINGS
from logic.midput.settings import CATALOGDIR
#from controller import LOGHANDLER
from controller.loghandler import LogHandler
from controller.abouthandler import AboutHandler
from controller.catalog_properties import CatalogPropertiesHandler
from logic.logging import MANAGER
from logic.input.dbmanager import DBManager, get_scanned_path_from_catalog, get_correct_filename_from_catalog
from logic.input.mdmanager import MDManager
from logic.utils import clean_catalog_dir


class MainHandler(object):

    """Main window handler.
    
    Grabs all events from the main window, and passes those relevant to the
    treeviews to the TVHandler. And the rest, is magic ;-).
    """

    def __init__(self, gladefile):
        clean_catalog_dir()
        #======================================================================
        # MANAGER.loghandler = LOGHANDLER
        # LOGHANDLER.mainhandler = self
        #======================================================================
        self._tvhandlers = []
        self._dbmanagers = []
        self._dbmanager = None
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
        #self._tvhandler = TVHandler(self)
        self._window.drag_dest_set(gtk.DEST_DEFAULT_DROP,
                                   [('text/plain', 0, 0)], 0)
        self._window.connect("configure-event", self._configure)
        self._window.connect("destroy", self._destroy)
        self._window.connect("drag_motion", self.motion_cb)
        self._window.connect("drag_data_received", self.got_data_cb)
        self._window.connect("window-state-event", self.view_state)
        self._chkmninfopane = self._wtree.get_object("chkmninfopane")
        self._imgmnscan = self._wtree.get_object("imgmnscan")
        self._imgmnload = self._wtree.get_object("imgmnload")
        self._imgmnsaveas = self._wtree.get_object("imgmnsaveas")
        self._tbsearch = self._wtree.get_object("tbsearch")
        #self._tbsearch.set_sensitive(False)
        self._tbnewpath = self._wtree.get_object("tbnewpath")
        self._tbsave = self._wtree.get_object("tbsave")
        self._tbloadfile = self._wtree.get_object("tbloadfile")
        #self._vwpscan = self._wtree.get_object("vwpscan")
        self._notebook = self._wtree.get_object("notebook")
        #self._notebook.set_scrollable(True)
        self._hpscanlist = self._wtree.get_object("hpscanlist")
        self._tvscanlist = self._wtree.get_object("tvscanlist")
        self._lsscanlist = gtk.ListStore(gtk.gdk.Pixbuf, str, str)
        self._tvscanlist.set_model(self._lsscanlist)

        self._tvcolsl_data = self._wtree.get_object("tvcolsl_data")
        self._cellsl_icon = gtk.CellRendererPixbuf()
        self._cellsl_data = gtk.CellRendererText()
        self._tvcolsl_data.pack_start(self._cellsl_icon, False)
        self._tvcolsl_data.pack_start(self._cellsl_data, False)
        self._tvcolsl_data.add_attribute(self._cellsl_icon, "pixbuf", 0)
        self._tvcolsl_data.add_attribute(self._cellsl_data, "markup", 1)

        self.scanlist_popup = self._wtree.get_object("scanlist_popup")
        self._mdmanager = MDManager(self, self._lsscanlist)
        self._mdmanager.populate_catalog_list()

        self._current = None
        self._currentnode = None
        self._currentpath = None

        self._chkmnlog = self._wtree.get_object("chkmnlog")

        self._wtree.connect_signals(self)
        self._window.set_default_size(*SETTINGS.windowsize)
        #self._hplistpane.set_position(SETTINGS.infopanesize)
        
        self._tray_popup = self._wtree.get_object("tray_popup")
        
        self._tray = gtk.StatusIcon()
        if sys.platform == "win32":
            self._tray.set_from_file("icons/indexorapp.png")
        else:
            self._tray.set_from_file("icons/indexorapp.svg")
        self._tray.set_tooltip("Indexor")
        
        self._tray.connect("activate", self.tray_activate_cb)
        self._tray.connect("popup-menu", self.tray_popup_menu)
        
        
        if SETTINGS.windowmax is True:
            self._window.maximize()
        self._window.show_all()

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

    def get_pbar(self):
        return self._pbar

    #def get_vwpscan(self):
    #    return self._vwpscan

    def get_notebook(self):
        return self._notebook

    def get_chkmninfopane(self):
        return self._chkmninfopane
    
    def get_tvhandlers(self):
        return self._tvhandlers
    
    def get_mdmanager(self):
        return self._mdmanager

    currentpath = property(get_currentpath, set_currentpath)
    currentnode = property(get_currentnode, set_currentnode)
    current = property(get_current, set_current)
    root = property(get_root, set_root)
    chkmnlog = property(get_chkmnlog)
    window = property(get_window)
    pbar = property(get_pbar)
    notebook = property(get_notebook)
    chkmninfopane = property(get_chkmninfopane)
    tvhandlers = property(get_tvhandlers)
    mdmanager = property(get_mdmanager)
    #vwpscan = property(get_vwpscan)

    #################################
    #Methods
    #################################
    def populate_catalog_list(self):
        self._mdmanager.populate_catalog_list(
                                              )
    def _destroy(self, widget):
        """Destroys the window."""
        #SETTINGS.infopanesize = self._hplistpane.get_position()
        LOADER.save_settings()
        gtk.main_quit()

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

    def init_index_process(self, path):
        """Starts the indexing process.
        
        Fires up the relevant methods in a thread. Then checks if something
        was already indexed, and clears the environment accordingly.
        """
        if (path is not None):
            tvhandler = TVHandler(self, path)
            self._tvhandlers.append(tvhandler)
            #self.set_buttons_sensitivity(False)
            tvhandler.add_to_viewport()
            tvhandler.pbar.set_text("")
            tvhandler.hbpbar.show()
            dbmanager = DBManager(self, tvhandler)
            self._dbmanagers.append(dbmanager)
            if dbmanager.index_new_dir(path) is True:
                fscountthread = dbmanager.start_counting()
                tvhandler.dbmanager = dbmanager
                gobject.timeout_add(500, tvhandler.check_if_counting_finished,
                                    fscountthread)
                tvhandler.hbpbar.show()
                tvhandler.is_scanning = True
            else:
                self.set_buttons_sensitivity(True)

    def remove_scan(self, tvhandler):
        index = self._tvhandlers.index(tvhandler)
        self._tvhandlers.pop(index)
        self._dbmanagers.pop(index)
        self._notebook.remove_page(index)
        if len(self._tvhandlers) == 0:
            self._root = None
            self._catalog_to_save = None
            self.set_buttons_sensitivity(True)

    def set_buttons_sensitivity(self, sensitive):
        """Sets buttons (and menus) sensitivity according to value given
        
        This method is used when the indexing process begins or ends.
        """
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

    def load_catalog_from_filename(self, filename):
        opened = False
        for tvhandler in self._tvhandlers:
            if tvhandler.path == get_scanned_path_from_catalog(filename):
                self._notebook.set_current_page(self._tvhandlers.
                                                index(tvhandler))
                opened = True
        if opened is False:
            path = get_scanned_path_from_catalog(filename)
            tvhandler = TVHandler(self, path)
            self._tvhandlers.append(tvhandler)
            dbmanager = DBManager(self, tvhandler)
            self._dbmanagers.append(dbmanager)
            dbmanager.create_connection(filename, path)
            dbmanager.set_root_node()
            tvhandler.dbmanager = dbmanager
            tvhandler.add_to_viewport()
            tvhandler.print_output()


    def set_infopanes_visibility(self, value):
        if value is None:
            value = self._chkmninfopane.get_active()
        if value is True:
            for tvhandler in self._tvhandlers:
                tvhandler.infopane.show()
        else:
            for tvhandler in self._tvhandlers:
                tvhandler.infopane.hide()

    #################################
    #Callbacks
    #################################
    def notebook_switch_page_cb(self, notebook, page, page_num):
        widget = self._notebook.get_nth_page(page_num)
        label = self._notebook.get_tab_label(widget).get_children()[0].get_text()
        for dbmanager in self._dbmanagers:
            if dbmanager.path == label:
                self._root = dbmanager.root
                self._catalog_to_save = dbmanager.scanningcatalog

    def tbnewpath_clicked_cb(self, widget):
        """Shows the "New Path" dialog."""
        opendialog = \
        gtk.FileChooserDialog(title = "Point me a path...",
                              parent = self._window,
                              action = gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER,
                              buttons = (gtk.STOCK_CANCEL,
                                         gtk.RESPONSE_CANCEL,
                                         gtk.STOCK_OK, gtk.RESPONSE_OK))
        response = opendialog.run()
        if response == gtk.RESPONSE_OK:
            if hasattr(self, "_searchhandler"):
                self._searchhandler.destroy(self._window)
            self._tbloadfile.set_sensitive(False)
            self.init_index_process(opendialog.get_filename())
        opendialog.destroy()
        #CatalogPropertiesHandler(self, None)
        

    def tbsave_clicked_cb(self, widget):
        """Shows the "Save" dialog."""
        savedialog = \
        gtk.FileChooserDialog(title = "Point me a destination...",
                              parent = self._window,
                              action = gtk.FILE_CHOOSER_ACTION_SAVE,
                              buttons = (gtk.STOCK_CANCEL,
                                         gtk.RESPONSE_CANCEL,
                                         gtk.STOCK_OK, gtk.RESPONSE_OK))
        plainfilter = gtk.FileFilter()
        plainfilter.add_mime_type("text/plain")
        plainfilter.set_name("Plain text")
        binaryfilter = gtk.FileFilter()
        binaryfilter.add_pattern("*.db")
        binaryfilter.set_name("Binary file")
        savedialog.add_filter(binaryfilter)
        savedialog.add_filter(plainfilter)
        savedialog.set_do_overwrite_confirmation(True)
        response = savedialog.run()
        if response == gtk.RESPONSE_OK:
            if savedialog.get_filter() == binaryfilter:
                shutil.copy(self._catalog_to_save, savedialog.get_filename())
            if savedialog.get_filter() == plainfilter:
                PlainTextWriter(savedialog.get_filename(), self._root)
        savedialog.destroy()

    def tbloadfile_clicked_cb(self, widget):
        """Shows the "Load" dialog."""
        binaryfilter = gtk.FileFilter()
        binaryfilter.add_pattern("*.db")
        binaryfilter.set_name("Binary file")
        opendialog = \
        gtk.FileChooserDialog(title = "Point me a source...",
                              parent = self._window,
                              action = gtk.FILE_CHOOSER_ACTION_OPEN,
                              buttons = (gtk.STOCK_CANCEL,
                                         gtk.RESPONSE_CANCEL,
                                         gtk.STOCK_OK, gtk.RESPONSE_OK))
        opendialog.add_filter(binaryfilter)
        response = opendialog.run()
        if response == gtk.RESPONSE_OK:
            filename = opendialog.get_filename()
            dest = get_correct_filename_from_catalog(filename)
            shutil.copy(filename, CATALOGDIR + "/" + dest)
            filename = CATALOGDIR + "/" + dest
            self.load_catalog_from_filename(filename)
            if hasattr(self, "_searchhandler"):
                self._searchhandler.destroy(self._window)
        opendialog.destroy()

    def tbsearch_clicked_cb(self, widget):
        """Shows the search window.
        
        Creates a new SearchHandler and shows its window.
        """
        self._searchhandler = SearchHandler(self)

    def btncancel_clicked_cb(self, widget):
        """Callback used when cancelling the indexing process"""
        self._dbmanager.stop = True
        self._pbar.set_text("Indexing process of " + self._path + 
                            " cancelled.")
        gobject.timeout_add(2000, self._tvhandler.hide_progressbar)

    #Notebook
    def tabbtn_clicked_cb(self, widget, tvhandler):
        self.remove_scan(tvhandler)

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
        if self._dbmanager is not None:
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
        self.set_infopanes_visibility(widget.get_active())

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

    def tvscanlist_row_activated_cb(self, tvsl, path, view_column):
        _iter = tvsl.get_model().get_iter(path)
        self.load_catalog_from_filename(self._lsscanlist.get(_iter, 2)[0])
        
    def tvscanlist_button_press_event_cb(self, treeview, event):
        if event.button == 3:
            x = int(event.x)
            y = int(event.y)
            time = event.time
            pathinfo = treeview.get_path_at_pos(x, y)
            if pathinfo is not None:
                path, col, cellx, celly = pathinfo
                treeview.grab_focus()
                treeview.set_cursor(path, col, 0)
                self.scanlist_popup.popup(None, None, None, event.button, time)
            return True
        
    def sl_edit_activate_cb(self, menuitem):
        selection = self._tvscanlist.get_selection()
        metadirfile = self._lsscanlist.get(selection.get_selected()[1], 2)[0]
        metadir = self._mdmanager.metadir_dict[metadirfile]
        CatalogPropertiesHandler(self, metadir)
    
    def sl_delete_activate_cb(self, menuitem):
        selection = self._tvscanlist.get_selection()
        metadirfile = self._lsscanlist.get(selection.get_selected()[1], 2)[0]
        message = gtk.MessageDialog(self._window, gtk.DIALOG_MODAL, gtk.MESSAGE_INFO, gtk.BUTTONS_NONE, "Do you wish to delete the selected catalog?")
        message.add_button(gtk.STOCK_OK, gtk.RESPONSE_OK)
        message.add_button(gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT)
        message.set_property("title", "Delete catalog?")
        resp = message.run()
        if resp == gtk.RESPONSE_OK:
            os.remove(metadirfile)
            self.populate_catalog_list()
        message.destroy()

    def tray_activate_cb(self, tray):
        if self._window.get_property("visible") is True:
            self._window.hide()
        else:
            self._window.show()

    def tray_popup_menu(self, widget, button, time):
        self._tray_popup.popup(None, None, None, 3, time)
        
    def try_close_activate_cb(self, menuitem):
        message = gtk.MessageDialog(self._window, gtk.DIALOG_MODAL, gtk.MESSAGE_WARNING, gtk.BUTTONS_NONE, "Do you wish to close Indexor?")
        message.add_button(gtk.STOCK_OK, gtk.RESPONSE_OK)
        message.add_button(gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT)
        message.set_property("title", "Exit program?")
        resp = message.run()
        message.destroy()
        if resp == gtk.RESPONSE_OK:
            self._destroy(menuitem)
            
    def try_show_hide_activate_cb(self, menuitem):
        self.tray_activate_cb(menuitem)
    
    def try_scan_path_activate_cb(self, menuitem):
        self.tbnewpath_clicked_cb(menuitem)
        
    def try_open_catalog_activate_cb(self, menuitem):
        self.tbloadfile_clicked_cb(menuitem)
