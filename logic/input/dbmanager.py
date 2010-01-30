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

from sqlobject import connectionForURI
import os
import datetime
import time
import gc

from logic.input.indexer import Indexer
from logic.input.factory import Factory
from logic.midput.settings import HOMEDIR

class DBManager(object):
    
    def __init__(self):
        pass
    
    #################################
    #Propeties
    #################################
    def get_stop(self):
        if hasattr(self, "indexer") and self._indexer is not None:
            return self._indexer.stop
    
    def set_stop(self, stop):
        if hasattr(self, "indexer") and self._indexer is not None:
            self._indexer.stop = stop
    
    def get_indexer(self):
        return self._indexer
    
    def set_indexer(self, indexer):
        if indexer is None:
            self._indexer = None
            gc.collect()
    
    def get_conn(self):
        return self._conn
            
    stop = property(get_stop, set_stop)
    indexer = property(get_indexer, set_indexer)
    conn = property(get_conn)
    #################################
    #Methods
    #################################
    def index_new_dir(self, path, mainhandler):
        date = datetime.datetime.fromtimestamp(time.time()).\
                strftime("%Y.%m.%d-%H.%M.%S")
        con_str = "sqlite://" + HOMEDIR + "/catalogs/" + \
                    os.path.basename(path) + "--" + date + ".db"
        self._conn = connectionForURI(con_str)
        factory = Factory(self._conn)
        self._indexer = Indexer(path, mainhandler.pbar, mainhandler, factory)
    
    def start_counting(self):
        return self._indexer.start_counting()
    
    def start_indexing(self):
        return self._indexer.start_indexing()
        
        