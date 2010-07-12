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

"""Module for the handler of the settings window"""

import gtk
import sys
import pango

from logic.midput import LOADER, SETTINGS

class SettingsHandler(object):

    """Settings window handler"""

    def __init__(self, mainhandler):
        self._mainhandler = mainhandler
        self._wtree = gtk.Builder()
        self._wtree.add_from_file("view/settings.glade")
        self._wtree.connect_signals(self)
        self._tblinterface = self._wtree.get_object("tblinterface")
        self._tbllogs = self._wtree.get_object("tbllogs")
        self._tblfilters = self._wtree.get_object("tblfilters")
        self._tbltabs = self._wtree.get_object("tbltabs")
        self._window = self._wtree.get_object("optionswindow")
        self._window.set_transient_for(self._mainhandler.window)
        self._window.connect("destroy", self.destroy)
        self._vwpfilters = self._wtree.get_object("vwpfilters")
        self._vwplogs = self._wtree.get_object("vwplogs")

        #Treeview
        self._tvconfig = self._wtree.get_object("tvconfig")
        self._tvcol_section = self._wtree.get_object("tvcol_section")
        self._lsconfig = gtk.ListStore(gtk.gdk.Pixbuf, str)
        self._lsconfig.append([gtk.icon_theme_get_default().\
                              load_icon("preferences-desktop-theme", 32,
                                gtk.ICON_LOOKUP_NO_SVG), "Interface"])
        self._lsconfig.append([gtk.icon_theme_get_default().\
                              load_icon("edit-find", 32,
                                gtk.ICON_LOOKUP_NO_SVG), "Logs"])
        self._lsconfig.append([gtk.icon_theme_get_default().\
                              load_icon("system-search", 32,
                                gtk.ICON_LOOKUP_NO_SVG), "Filters"])
        self._lsconfig.append([gtk.icon_theme_get_default().\
                              load_icon("tab-new", 32,
                                gtk.ICON_LOOKUP_NO_SVG), "Tabs"])
        self._tvconfig.set_model(self._lsconfig)
        self._cell_icon = gtk.CellRendererPixbuf()
        self._cell_name = gtk.CellRendererText()
        self._tvcol_section.pack_start(self._cell_icon, False)
        self._tvcol_section.pack_start(self._cell_name, False)
        self._tvcol_section.add_attribute(self._cell_icon, "pixbuf", 0)
        self._tvcol_section.add_attribute(self._cell_name, "text", 1)


        #Interface
        #Icon/thumb sizes
        self._spiniconlistsize = self._wtree.get_object("spiniconsizelist")
        self._spiniconpanesize = self._wtree.get_object("spiniconsizepane")
        self._spinthumblistsize = self._wtree.get_object("spinthumbsizelist")
        self._spinthumbpanesize = self._wtree.get_object("spinthumbsizepane")
        self._cmbiconlistsize = self._wtree.get_object("cmbiconsizelist")
        self._cmbiconpanesize = self._wtree.get_object("cmbiconsizepane")
        self._cmbthumblistsize = self._wtree.get_object("cmbthumbsizelist")
        self._cmbthumbpanesize = self._wtree.get_object("cmbthumbsizepane")

        #Info pane attrs.
        self._chkinterfacegeninfo = self._wtree.get_object("chkinterfacegen")
        self._chkinterfaceabs = self._wtree.get_object("chkinterfaceabs")
        self._chkinterfacerel = self._wtree.get_object("chkinterfacerel")
        self._chkinterfacesize = self._wtree.get_object("chkinterfacesize")
        self._chkinterfacemime = self._wtree.get_object("chkinterfacemime")
        self._chkinterfaceatime = self._wtree.get_object("chkinterfaceatime")
        self._chkinterfacemtime = self._wtree.get_object("chkinterfacemtime")
        self._chkinterfacemediainfo = self._wtree.\
                                        get_object("chkinterfacemedia")
        self._chkinterfacemedialength = self._wtree.\
                                        get_object("chkinterfacemedialength")
        self._chkinterfacevideoinfo = self._wtree.\
                                            get_object("chkinterfacevideo")
        self._chkinterfacevideocodec = self._wtree.\
                                        get_object("chkinterfacevideocodec")
        self._chkinterfacevideobitrate = self._wtree.\
                                        get_object("chkinterfacevideobitrate")
        self._chkinterfacevideores = self._wtree.\
                                        get_object("chkinterfacevideores")
        self._chkinterfacevideofps = self._wtree.\
                                        get_object("chkinterfacevideofps")
        self._chkinterfacevideoar = self._wtree.\
                                        get_object("chkinterfacevideoar")
        self._chkinterfaceaudioinfo = self._wtree.\
                                        get_object("chkinterfaceaudio")
        self._chkinterfaceaudiobitrate = self._wtree.\
                                        get_object("chkinterfaceaudiobitrate")
        self._chkinterfaceaudiosample = self._wtree.\
                                        get_object("chkinterfaceaudiosample")
        self._chkinterfaceaudiocodec = self._wtree.\
                                        get_object("chkinterfaceaudiocodec")
        self._chkinterfaceaudiochan = self._wtree.get_object\
                                        ("chkinterfaceaudiochannels")
        self._chkinterfacesubinfo = self._wtree.\
                                        get_object("chkinterfacesub")
        self._chkinterfacesublangs = self._wtree.\
                                        get_object("chkinterfacesublangs")
        self._chkinterfaceimginfo = self._wtree.\
                                        get_object("chkinterfaceimage")
        self._chkinterfaceimgres = self._wtree.\
                                        get_object("chkinterfaceimageres")
        self._chkinterfaceimgdate = self._wtree.\
                                        get_object("chkinterfaceimagedate")
        self._chkinterfaceimgauthor = self._wtree.\
                                        get_object("chkinterfaceimageauthor")
        self._chkinterfaceimgsoft = self._wtree.\
                                        get_object("chkinterfaceimagesoft")

        #Logs
        self._chklogsdebug = self._wtree.get_object("chklogsdebug")
        self._chklogsmime = self._wtree.get_object("chklogsmime")
        self._chklogsreadio = self._wtree.get_object("chklogsreadio")
        self._chklogsreadmeta = self._wtree.get_object("chklogsreadmeta")
        self._chklogsicon = self._wtree.get_object("chklogsicon")
        self._chklogsthumb = self._wtree.get_object("chklogsthumb")

        #Filters
        self._chkfiltergnuhidden = self._wtree.get_object\
                                    ("chkfiltergnuhidden")
        self._chkfiltersavebackup = self._wtree.get_object\
                                    ("chkfiltersavebackup")

        #Tabs
        self._chktabellipsize = self._wtree.get_object("chktabellipsize")
        self._spintablength = self._wtree.get_object("spintablength")
        self._cmbtabellipplace = self._wtree.get_object("cmbtabellipplace")
        self._set_values_from_settings()
        self._window.show_all()
        self._hide_combo_or_spin()
        #self._hidetbls()

    def destroy(self, widget):
        """Destroys the window"""
        if self._window is not None:
            self._window.destroy()
            self._window = None

    def _hidetbls(self):
        """Hides all tables. Used when switching sections inside the window"""
        self._tblinterface.hide()
        self._tbllogs.hide()
        self._tblfilters.hide()
        self._tbltabs.hide()

    def _hide_combo_or_spin(self):
        """Method to show either the comboboxes or the spinbuttons
        
        This is needed because Windows doesn't handle SVG icons well, so we
        need to use fixed size icons (in order to be sure that the icon is
        loaded from the sized png files.
        """
        if sys.platform == "win32":
            #This means we are on Win32, so we hide the spinbuttons.
            self._spiniconlistsize.hide()
            self._spiniconpanesize.hide()
            self._spinthumblistsize.hide()
            self._spinthumbpanesize.hide()
        else:
            #This means we are NOT on Win32, so we hide the comboboxes.
            self._cmbiconlistsize.hide()
            self._cmbiconpanesize.hide()
            self._cmbthumblistsize.hide()
            self._cmbthumbpanesize.hide()

    def _set_values_from_settings(self):
        """Set all values in the settings windows
        
        The values are taken from the corresponding value set in the SETTINGS
        object.
        """
        if sys.platform == "win32":
            self._set_combos()
        else:
            self._set_spins()
        self._chkinterfacegeninfo.set_active(SETTINGS.geninfo)
        self._chkinterfaceabs.set_active(SETTINGS.abspath)
        self._chkinterfacerel.set_active(SETTINGS.relpath)
        self._chkinterfacesize.set_active(SETTINGS.size)
        self._chkinterfacemime.set_active(SETTINGS.mime)
        self._chkinterfaceatime.set_active(SETTINGS.atime)
        self._chkinterfacemtime.set_active(SETTINGS.mtime)
        self._chkinterfacemediainfo.set_active(SETTINGS.mediainfo)
        self._chkinterfacemedialength.set_active(SETTINGS.medialength)
        self._chkinterfacevideoinfo.set_active(SETTINGS.videoinfo)
        self._chkinterfacevideocodec.set_active(SETTINGS.videocodec)
        self._chkinterfacevideobitrate.set_active(SETTINGS.videobitrate)
        self._chkinterfacevideores.set_active(SETTINGS.videores)
        self._chkinterfacevideofps.set_active(SETTINGS.videofps)
        self._chkinterfacevideoar.set_active(SETTINGS.videoar)
        self._chkinterfaceaudioinfo.set_active(SETTINGS.audioinfo)
        self._chkinterfaceaudiobitrate.set_active(SETTINGS.audiobitrate)
        self._chkinterfaceaudiosample.set_active(SETTINGS.audiosample)
        self._chkinterfaceaudiocodec.set_active(SETTINGS.audiocodec)
        self._chkinterfaceaudiochan.set_active(SETTINGS.audiochan)
        self._chkinterfacesubinfo.set_active(SETTINGS.subinfo)
        self._chkinterfacesublangs.set_active(SETTINGS.sublangs)
        self._chkinterfaceimginfo.set_active(SETTINGS.imginfo)
        self._chkinterfaceimgres.set_active(SETTINGS.imgres)
        self._chkinterfaceimgdate.set_active(SETTINGS.imgdate)
        self._chkinterfaceimgauthor.set_active(SETTINGS.imgauthor)
        self._chkinterfaceimgsoft.set_active(SETTINGS.imgsoft)
        self._chklogsdebug.set_active(SETTINGS.debug)
        self._chklogsmime.set_active(SETTINGS.missingmime)
        self._chklogsreadio.set_active(SETTINGS.ioerror)
        self._chklogsreadmeta.set_active(SETTINGS.metadataerror)
        self._chklogsicon.set_active(SETTINGS.missingicon)
        self._chklogsthumb.set_active(SETTINGS.thumberror)
        self._chkfiltergnuhidden.set_active(SETTINGS.gnuhidden)
        self._chkfiltersavebackup.set_active(SETTINGS.savebackup)
        self._chktabellipsize.set_active(SETTINGS.tabellipsize)
        tabellipplace = 0
        if SETTINGS.tabellipplace == pango.ELLIPSIZE_START:
            tabellipplace = 0
        elif SETTINGS.tabellipplace == pango.ELLIPSIZE_MIDDLE:
            tabellipplace = 1
        elif SETTINGS.tabellipplace == pango.ELLIPSIZE_END:
            tabellipplace = 2
        self._cmbtabellipplace.set_active(tabellipplace)

    def _set_spins(self):
        """Sets the values for the spinbuttons"""
        self._spiniconlistsize.set_value(SETTINGS.iconlistsize)
        self._spiniconpanesize.set_value(SETTINGS.iconpanesize)
        self._spinthumblistsize.set_value(SETTINGS.thumblistsize)
        self._spinthumbpanesize.set_value(SETTINGS.thumbpanesize)
        self._spintablength.set_value(SETTINGS.tablength)

    def _set_combos(self):
        """Sets the values for the comboboxes"""
        sett = {
               0    :   SETTINGS.iconlistsize,
               1    :   SETTINGS.iconpanesize,
               2    :   SETTINGS.thumblistsize,
               3    :   SETTINGS.thumbpanesize,
               }
        cmb = {
               0    :   self._cmbiconlistsize,
               1    :   self._cmbiconpanesize,
               2    :   self._cmbthumblistsize,
               3    :   self._cmbthumbpanesize
               }
        #======================================================================
        # call = {
        #        0   :   self.cmbiconsizelist_changed_cb,
        #        1   :   self.cmbiconsizepane_changed_cb,
        #        2   :   self.cmbthumbsizelist_changed_cb,
        #        3   :   self.cmbthumbsizepane_changed_cb,
        #        }
        #======================================================================
        for i in range(4):
            if sett[i] > 128:
                cmb[i].set_active(3)
            elif sett[i] > 112:
                cmb[i].set_active(8)
            elif sett[i] > 84:
                cmb[i].set_active(7)
            elif sett[i] > 68:
                cmb[i].set_active(6)
            elif sett[i] > 56:
                cmb[i].set_active(5)
            elif sett[i] > 40:
                cmb[i].set_active(4)
            elif sett[i] > 28:
                cmb[i].set_active(3)
            elif sett[i] > 23:
                cmb[i].set_active(2)
            elif sett[i] > 19:
                cmb[i].set_active(1)
            else:
                cmb[i].set_active(0)


    #################################
    #Callbacks
    #################################
    def tvconfig_cursor_changed_cb(self, tvconfig):
        (_model, _iter) = tvconfig.get_selection().get_selected()
        name = tvconfig.get_model().get_value(_iter, 1)
        if name == "Interface":
            self.tbinterface_clicked_cb(None)
        elif name == "Logs":
            self.tblogs_clicked_cb(None)
        elif name == "Filters":
            self.tbfilters_clicked_cb(None)
        elif name == "Tabs":
            self.tbtabs_clicked_cb(None)

    def tbinterface_clicked_cb(self, widget):
        """Callback for the interface section"""
        self._hidetbls()
        self._tblinterface.show()

    def tblogs_clicked_cb(self, widget):
        """Callback for the logs section"""
        self._hidetbls()
        self._tbllogs.show()

    def tbfilters_clicked_cb(self, widget):
        """Callback for the filters section"""
        self._hidetbls()
        self._tblfilters.show()

    def tbtabs_clicked_cb(self, widget):
        self._hidetbls()
        self._tbltabs.show()

    def btnclose_clicked_cb(self, widget):
        """Callback called when closing the window"""
        self.destroy(widget)

    def btnsave_clicked_cb(self, widget):
        """Callback called when saving settings"""
        LOADER.save_settings()

    #Settings
    #Filters
    def chkfiltersavebackup_toggled_cb(self, widget):
        """Callback"""
        SETTINGS.savebackup = widget.get_active()

    def chkfiltergnuhidden_toggled_cb(self, widget):
        """Callback"""
        SETTINGS.gnuhidden = widget.get_active()

    #Logging
    def chklogsdebug_toggled_cb(self, widget):
        """Callback"""
        SETTINGS.debug = widget.get_active()

    def chklogsthumb_toggled_cb(self, widget):
        """Callback"""
        SETTINGS.thumberror = widget.get_active()

    def chklogsicon_toggled_cb(self, widget):
        """Callback"""
        SETTINGS.missingicon = widget.get_active()

    def chklogsreadmeta_toggled_cb(self, widget):
        """Callback"""
        SETTINGS.metadataerror = widget.get_active()

    def chklogsreadio_toggled_cb(self, widget):
        """Callback"""
        SETTINGS.ioerror = widget.get_active()

    def chklogsmime_toggled_cb(self, widget):
        """Callback"""
        SETTINGS.missingmime = widget.get_active()

    #Interface
    #Info pane
    def chkinterfacegen_toggled_cb(self, widget):
        """Callback"""
        SETTINGS.geninfo = widget.get_active()
        self._chkinterfaceabs.set_sensitive(widget.get_active())
        self._chkinterfacerel.set_sensitive(widget.get_active())
        self._chkinterfacesize.set_sensitive(widget.get_active())
        self._chkinterfacemime.set_sensitive(widget.get_active())
        self._chkinterfaceatime.set_sensitive(widget.get_active())
        self._chkinterfacemtime.set_sensitive(widget.get_active())
        self._mainhandler.set_infopanes_visibility(None)

    def chkinterfacemtime_toggled_cb(self, widget):
        """Callback"""
        SETTINGS.mtime = widget.get_active()
        self._mainhandler.set_infopanes_visibility(None)

    def chkinterfaceatime_toggled_cb(self, widget):
        """Callback"""
        SETTINGS.atime = widget.get_active()
        self._mainhandler.set_infopanes_visibility(None)

    def chkinterfacemime_toggled_cb(self, widget):
        """Callback"""
        SETTINGS.mime = widget.get_active()
        self._mainhandler.set_infopanes_visibility(None)

    def chkinterfacerel_toggled_cb(self, widget):
        """Callback"""
        SETTINGS.relpath = widget.get_active()
        self._mainhandler.set_infopanes_visibility(None)

    def chkinterfacesize_toggled_cb(self, widget):
        """Callback"""
        SETTINGS.size = widget.get_active()
        self._mainhandler.set_infopanes_visibility(None)

    def chkinterfaceabs_toggled_cb(self, widget):
        """Callback"""
        SETTINGS.abspath = widget.get_active()
        self._mainhandler.set_infopanes_visibility(None)

    def chkinterfacemedia_toggled_cb(self, widget):
        """Callback"""
        SETTINGS.mediainfo = widget.get_active()
        self._chkinterfacemedialength.set_sensitive(widget.get_active())
        self._mainhandler.set_infopanes_visibility(None)

    def chkinterfacemedialength_toggled_cb(self, widget):
        """Callback"""
        SETTINGS.medialength = widget.get_active()
        self._mainhandler.set_infopanes_visibility(None)

    def chkinterfacevideo_toggled_cb(self, widget):
        """Callback"""
        SETTINGS.videoinfo = widget.get_active()
        self._chkinterfacevideocodec.set_sensitive(widget.get_active())
        self._chkinterfacevideobitrate.set_sensitive(widget.get_active())
        self._chkinterfacevideores.set_sensitive(widget.get_active())
        self._chkinterfacevideofps.set_sensitive(widget.get_active())
        self._chkinterfacevideoar.set_sensitive(widget.get_active())
        self._mainhandler.set_infopanes_visibility(None)

    def chkinterfacevideocodec_toggled_cb(self, widget):
        """Callback"""
        SETTINGS.videocodec = widget.get_active()
        self._mainhandler.set_infopanes_visibility(None)

    def chkinterfacevideobitrate_toggled_cb(self, widget):
        """Callback"""
        SETTINGS.videobitrate = widget.get_active()
        self._mainhandler.set_infopanes_visibility(None)

    def chkinterfacevideores_toggled_cb(self, widget):
        """Callback"""
        SETTINGS.videores = widget.get_active()
        self._mainhandler.set_infopanes_visibility(None)

    def chkinterfacevideofps_toggled_cb(self, widget):
        """Callback"""
        SETTINGS.videofps = widget.get_active()
        self._mainhandler.set_infopanes_visibility(None)

    def chkinterfacevideoar_toggled_cb(self, widget):
        """Callback"""
        SETTINGS.videoar = widget.get_active()
        self._mainhandler.set_infopanes_visibility(None)

    def chkinterfaceaudio_toggled_cb(self, widget):
        """Callback"""
        SETTINGS.audioinfo = widget.get_active()
        self._chkinterfaceaudiobitrate.set_sensitive(widget.get_active())
        self._chkinterfaceaudiosample.set_sensitive(widget.get_active())
        self._chkinterfaceaudiocodec.set_sensitive(widget.get_active())
        self._chkinterfaceaudiochan.set_sensitive(widget.get_active())
        self._mainhandler.set_infopanes_visibility(None)

    def chkinterfaceaudiobitrate_toggled_cb(self, widget):
        """Callback"""
        SETTINGS.audiobitrate = widget.get_active()
        self._mainhandler.set_infopanes_visibility(None)

    def chkinterfaceaudiosample_toggled_cb(self, widget):
        """Callback"""
        SETTINGS.audiosample = widget.get_active()
        self._mainhandler.set_infopanes_visibility(None)

    def chkinterfaceaudiocodec_toggled_cb(self, widget):
        """Callback"""
        SETTINGS.audiocodec = widget.get_active()
        self._mainhandler.set_infopanes_visibility(None)

    def chkinterfaceaudiochannels_toggled_cb(self, widget):
        """Callback"""
        SETTINGS.audiochan = widget.get_active()
        self._mainhandler.set_infopanes_visibility(None)

    def chkinterfacesub_toggled_cb(self, widget):
        """Callback"""
        SETTINGS.subinfo = widget.get_active()
        self._chkinterfacesublangs.set_sensitive(widget.get_active())
        self._mainhandler.set_infopanes_visibility(None)

    def chkinterfacesublangs_toggled_cb(self, widget):
        """Callback"""
        SETTINGS.sublangs = widget.get_active()
        self._mainhandler.set_infopanes_visibility(None)

    def chkinterfaceimage_toggled_cb(self, widget):
        """Callback"""
        SETTINGS.imginfo = widget.get_active()
        self._chkinterfaceimgres.set_sensitive(widget.get_active())
        self._chkinterfaceimgdate.set_sensitive(widget.get_active())
        self._chkinterfaceimgauthor.set_sensitive(widget.get_active())
        self._chkinterfaceimgsoft.set_sensitive(widget.get_active())
        self._mainhandler.set_infopanes_visibility(None)

    def chkinterfaceimageres_toggled_cb(self, widget):
        """Callback"""
        SETTINGS.imgres = widget.get_active()
        self._mainhandler.set_infopanes_visibility(None)

    def chkinterfaceimagedate_toggled_cb(self, widget):
        """Callback"""
        SETTINGS.imgdate = widget.get_active()
        self._mainhandler.set_infopanes_visibility(None)

    def chkinterfaceimageauthor_toggled_cb(self, widget):
        """Callback"""
        SETTINGS.imgauthor = widget.get_active()
        self._mainhandler.set_infopanes_visibility(None)

    def chkinterfaceimagesoft_toggled_cb(self, widget):
        """Callback"""
        SETTINGS.imgsoft = widget.get_active()
        self._mainhandler.set_infopanes_visibility(None)

    #Icon/thumb sizes
    def cmbthumbsizepane_changed_cb(self, widget):
        """Callback"""
        model = widget.get_model()
        _iter = widget.get_active_iter()
        SETTINGS.thumbpanesize = model.get_value(_iter, 0)
        self._set_values_from_settings()

    def cmbiconsizepane_changed_cb(self, widget):
        """Callback"""
        model = widget.get_model()
        _iter = widget.get_active_iter()
        SETTINGS.iconpanesize = model.get_value(_iter, 0)
        self._set_values_from_settings()

    def cmbthumbsizelist_changed_cb(self, widget):
        """Callback"""
        model = widget.get_model()
        _iter = widget.get_active_iter()
        SETTINGS.thumblistsize = model.get_value(_iter, 0)
        self._set_values_from_settings()

    def cmbiconsizelist_changed_cb(self, widget):
        """Callback"""
        model = widget.get_model()
        _iter = widget.get_active_iter()
        SETTINGS.iconlistsize = model.get_value(_iter, 0)
        self._set_values_from_settings()

    def spinthumbsizepane_value_changed_cb(self, widget):
        """Callback"""
        SETTINGS.thumbpanesize = widget.get_value_as_int()

    def spiniconsizepane_value_changed_cb(self, widget):
        """Callback"""
        SETTINGS.iconpanesize = widget.get_value_as_int()

    def spinthumbsizelist_value_changed_cb(self, widget):
        """Callback"""
        SETTINGS.thumblistsize = widget.get_value_as_int()

    def spiniconsizelist_value_changed_cb(self, widget):
        """Callback"""
        SETTINGS.iconlistsize = widget.get_value_as_int()

    def cmbtabellipplace_changed_cb(self, widget):
        """Callback"""
        model = widget.get_model()
        _iter = widget.get_active_iter()
        value = model.get_value(_iter, 0)
        if value == "Start":
            SETTINGS.tabellipplace = pango.ELLIPSIZE_START
        elif value == "Middle":
            SETTINGS.tabellipplace = pango.ELLIPSIZE_MIDDLE
        elif value == "End":
            SETTINGS.tabellipplace = pango.ELLIPSIZE_END
        #self._set_values_from_settings()

    def chktabellipsize_toggled_cb(self, widget):
        self._cmbtabellipplace.set_sensitive(widget.get_active())
        self._spintablength.set_sensitive(widget.get_active())
        SETTINGS.tabellipsize = widget.get_active()

    def spintablength_value_changed_cb(self, widget):
        SETTINGS.tablength = widget.get_value_as_int()
