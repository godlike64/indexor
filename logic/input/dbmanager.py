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

#from sqlobject import connectionForURI
import os
import datetime
import time
import gc
import gtk
import threading

from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy import create_engine
import elixir

from logic.input.indexer import Indexer
from logic.input.factory import Factory
from logic.midput.settings import HOMEDIR
from fs.entities import MetaDir, Directory

CATALOGDIR = HOMEDIR + "/catalogs/"

class DBManager(object):
    
    def __init__(self, mainhandler):
        self._mainhandler = mainhandler
    
    #################################
    #Propeties
    #################################
    def get_stop(self):
        if hasattr(self, "indexer") and self._indexer is not None:
            return self._indexer.stop
    
    def set_stop(self, stop):
        if hasattr(self, "indexer") and self._indexer is not None:
            self._indexer.stop = stop
            os.remove(self._scanningcatalog)
    
    def get_indexer(self):
        return self._indexer
    
    def set_indexer(self, indexer):
        if indexer is None:
            self._indexer = None
            gc.collect()
    
    def get_conn(self):
        return self._session
    
    def get_session(self):
        return self._session
    
    stop = property(get_stop, set_stop)
    indexer = property(get_indexer, set_indexer)
    conn = property(get_conn)
    session = property(get_session)
    
    #################################
    #Methods
    #################################
    def index_new_dir(self, path, mainhandler):
        if self._check_if_was_scanned(path) is True:
            date = datetime.datetime.fromtimestamp(time.time()).\
                    strftime("%Y.%m.%d-%H.%M.%S")
            file_str = CATALOGDIR + os.path.basename(path) + ".-." + date \
                        + ".db"
            con_str = "sqlite:///" + file_str
            self._scanningcatalog = file_str  
            #self._session = connectionForURI(con_str)
            elixir.setup_all()
            self._engine = create_engine(con_str)
            elixir.create_all(self._engine)
            self._session = scoped_session(sessionmaker(autoflush = True, 
                                                  bind = self._engine))
            self._factory = Factory(self._engine, self._session, self)
            self._indexer = Indexer(path, mainhandler.pbar, mainhandler, 
                                    self._factory)
            return True
        else:
            return False
        
    def _check_if_was_scanned(self, path):
        for entry in os.listdir(CATALOGDIR):
            if entry.endswith("-journal"):
                os.remove(CATALOGDIR + entry)
            if entry.startswith(os.path.basename(path)):
                if self._check_if_is_same_dir(entry, path) is True:
                    label = gtk.Label()
                    label.set_markup("Indexor has already registered " + \
                                      "this directory. Do you wish\n" +
                                      "to overwrite the catalog with the" + \
                                      "updated one?")
                    hbox = gtk.HBox(spacing = 8)
                    dialog = gtk.Dialog("Overwrite previous catalog?", 
                                        self._mainhandler.window, 
                                        gtk.DIALOG_MODAL, 
                                        (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
                                         gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
                    icon = gtk.icon_theme_get_default().\
                            load_icon("emblem-important", 64, 
                                      gtk.ICON_LOOKUP_NO_SVG)
                    img = gtk.image_new_from_pixbuf(icon)
                    img.show()
                    hbox.pack_start(img, True, True, 0)
                    hbox.pack_start(label, True, True, 0)
                    hbox.show()
                    dialog.vbox.pack_start(hbox, True, True, 0)
                    label.show()
                    response = dialog.run()
                    dialog.destroy()
                    if response == gtk.RESPONSE_ACCEPT:
                        os.remove(CATALOGDIR + entry)
                        return True
                    else:
                        return False
        return True
    
    def _check_if_is_same_dir(self, entry, path):
        con_str = "sqlite:///" + CATALOGDIR + entry
        elixir.setup_all()
        engine = create_engine(con_str)
        elixir.create_all(engine)
        session = scoped_session(sessionmaker(autoflush = True, 
                                          bind = engine))
        metadircount = session.query(MetaDir).filter_by(target = path).count()
        #metadircount = MetaDir.select(MetaDir.q.target == path, 
        #                         connection = conn).count()
        if metadircount > 0:
            return session.query(MetaDir).filter_by(target = path).one().target == path
            #return MetaDir.select(MetaDir.q.target == path, 
            #                     connection = conn)[0].target == path
        #return metadir.target == path
    
    def start_counting(self):
        return self._indexer.start_counting()
    
    def start_indexing(self):
        return self._indexer.start_indexing()
    
    def create_metadir(self):
        rootselect = self._session.query(Directory).filter_by(relpath = "/")
        #rootselect = Directory.select(Directory.q.relpath == "/", 
        #                              connection = self._session)
        root = rootselect.one()
        self._factory.new_metadir(self._indexer.path, 
                                  self._indexer.countfiles, 
                                  self._indexer.countdirs, root.size, 
                                  root.strsize)
        
        