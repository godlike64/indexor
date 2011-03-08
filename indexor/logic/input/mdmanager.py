#    This file is part of Indexor.
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
import gtk

from fs.entities import MetaDir
from logic.midput.settings import CATALOGDIR


class MDManager(object):

    def __init__(self, mainhandler, lsscanlist):
        self._mainhandler = mainhandler
        self._lsscanlist = lsscanlist
        self._metadir_dict = {}
        
    def get_metadir_dict(self):
        return self._metadir_dict
    
    metadir_dict = property(get_metadir_dict)

    def populate_catalog_list(self):
        self._lsscanlist.clear()
        for _file in os.listdir(CATALOGDIR):
            con_str = "sqlite://" + CATALOGDIR + _file
            conn = connectionForURI(con_str)
            selectmetadir = MetaDir.select(connection = conn)
            if selectmetadir.count() == 1:
                metadir = selectmetadir.getOne()
                self._lsscanlist.append([gtk.icon_theme_get_default().\
                                  load_icon(metadir.media_type, 64, gtk.ICON_LOOKUP_FORCE_SVG),
                                  "<b>" + metadir.name + "</b>\nFiles: " + 
                                  str(metadir.files) + "\nDirectories: " + 
                                  str(metadir.dirs) + "\nSize: " + 
                                  metadir.strsize, CATALOGDIR + _file])
                self._metadir_dict[CATALOGDIR + _file] = metadir
