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

from logic.logging import MANAGER
from logic.logging.event import TYPES
from logic.midput import SETTINGS

class LogHandler(object):
    
    def __init__(self, mainhandler):
        self._mainhandler = mainhandler
        self._types = [TYPES[1], TYPES[2], TYPES[3], TYPES[4], TYPES[5]]
        self._wtree = gtk.Builder()
        self._wtree.add_from_file("view/logviewer.glade")
        self._wtree.connect_signals(self)
        self._window = self._wtree.get_object("logwindow")
        self._window.connect("destroy", self.btnclose_clicked_cb)
        self._window.connect("configure-event", self._configure)
        self._window.set_default_size(*SETTINGS.logwindowsize)
        if SETTINGS.logwindowmax is True:
            self._window.maximize()
        self._tvlogviewer = self._wtree.get_object("tvlogviewer")
        self._lslogviewer = gtk.ListStore(str, str, str, str, str, str)
        self._tmflogviewer = self._lslogviewer.filter_new()
        self._tmflogviewer.set_visible_func(self._filter_logs)
        self._tmslogviewer = gtk.TreeModelSort(self._tmflogviewer)
        self._tvlogviewer.set_model(self._tmslogviewer)
        self._cellmsg = gtk.CellRendererText()
        self._cellfilename = gtk.CellRendererText()
        self._cellerr = gtk.CellRendererText()
        self._celltype = gtk.CellRendererText()
        self._celllocation = gtk.CellRendererText()
        self._celldate = gtk.CellRendererText()
        self._tvcolmsg = self._wtree.get_object("tvcolmsg")
        self._tvcolfilename = self._wtree.get_object("tvcolfilename")
        self._tvcolerr = self._wtree.get_object("tvcolerr")
        self._tvcoltype = self._wtree.get_object("tvcoltype")
        self._tvcollocation = self._wtree.get_object("tvcollocation")
        self._tvcoldate = self._wtree.get_object("tvcoldate")
        self._tvcolmsg.pack_start(self._cellmsg, False)
        self._tvcolfilename.pack_start(self._cellfilename, False)
        self._tvcolerr.pack_start(self._cellerr, False)
        self._tvcoltype.pack_start(self._celltype, False)
        self._tvcollocation.pack_start(self._celllocation, False)
        self._tvcoldate.pack_start(self._celldate, False)
        self._tvcolmsg.set_attributes(self._cellmsg, text=0)
        self._tvcolfilename.set_attributes(self._cellfilename, text=1)
        self._tvcolerr.set_attributes(self._cellerr, text=2)
        self._tvcoltype.set_attributes(self._celltype, text=3)
        self._tvcollocation.set_attributes(self._celllocation, text=4)
        self._tvcoldate.set_attributes(self._celldate, text=5)
        self._tvcolfilename.set_sort_column_id(1)
        self._tvcoldate.set_sort_column_id(5)
        self._populate_logviewer()
        self._window.show_all()

    def get_mainhandler(self):
        return self._mainhandler
    
    def set_mainhandler(self, mainhandler):
        self._mainhandler = mainhandler
        
    mainhandler = property(get_mainhandler, set_mainhandler)

    #################################
    #Methods
    #################################
    def _populate_logviewer(self):
        if MANAGER.events is not None:
            for event in MANAGER.events:
                self.add_event_to_store(event)
        
    def add_event_to_store(self, event):
        self._lslogviewer.append([event.msg, event.filename, event.err,
                                     TYPES[event.type], event.location,
                                     event.date])
        
    def hide_or_show(self, active):
        if active is True:
            self._window.show_all()
        else:
            self._mainhandler.chkmnlog.set_active(active)
            self._window.hide()

    def _filter_logs(self, model, iter):
        if model.get_value(iter, 3) in self._types:
            return True
        else:
            return False
    
    #################################
    #Callbacks
    #################################
    def chklogmissingmime_toggled_cb(self, widget):
        if widget.get_active() is True:
            self._types.append(TYPES[1])
        else:
            self._types.remove(TYPES[1])
        self._tmflogviewer.refilter()

    def chklogioerror_toggled_cb(self, widget):
        if widget.get_active() is True:
            self._types.append(TYPES[2])
        else:
            self._types.remove(TYPES[2])
        self._tmflogviewer.refilter()
    
    def chklogmetadataerror_toggled_cb(self, widget):
        if widget.get_active() is True:
            self._types.append(TYPES[3])
        else:
            self._types.remove(TYPES[3])
        self._tmflogviewer.refilter()

    def chklogmissingicon_toggled_cb(self, widget):
        if widget.get_active() is True:
            self._types.append(TYPES[4])
        else:
            self._types.remove(TYPES[4])
        self._tmflogviewer.refilter()

    def chklogthumberror_toggled_cb(self, widget):
        if widget.get_active() is True:
            self._types.append(TYPES[5])
        else:
            self._types.remove(TYPES[5])
        self._tmflogviewer.refilter()
        
    def btnclose_clicked_cb(self, widget):
        self._mainhandler.chkmnlog.set_active(False)
        self._window.destroy()
    
    def btnsave_clicked_cb(self, widget):
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
        savedialog.add_filter(plainfilter)
        savedialog.set_do_overwrite_confirmation(True)
        response = savedialog.run()
        if response == gtk.RESPONSE_OK:
            MANAGER.save_to_disk(savedialog.get_filename())
        savedialog.destroy()
        
    def _configure(self, widget, event):
        SETTINGS.logwindowsize = (event.width, event.height)
        
    def view_state(self, widget, event):
        if event.new_window_state == gtk.gdk.WINDOW_STATE_MAXIMIZED:
            SETTINGS.logwindowmax = True
        else:
            SETTINGS.logwindowmax = False