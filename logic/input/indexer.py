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

"""This module handles the indexing process."""

import os
import gobject
import threading
import datetime
import mimetypes

from fs.entries import File, Directory, Audio, Video, Photo, MIMES, \
NOT_AUDIO, SEPARATOR
from logic.midput import SETTINGS
from logic.logging import MANAGER

class Indexer(object):

    """Class which carries out the indexing process.
    
    It initializes the mimetypes module with the misc/mime.types file. Feel
    free to add more mimetypes to that file, respecting its format.
    There are also filters defined as methods which ignore some files from
    the indexed result. Currently, such filters ignore all files beginning
    with "." ("hidden" files in GNU/Linux) and all files ending in "~" (some
    GNU/Linux apps write such files as backup of others). New filters can be
    added easily as long as the structure is honored.
    """

    def __init__(self, path, progress, mainhandler):
        #mimetypes.init(['misc/mime.types'])
        mimetypes.add_type("audio/x-musepack", ".mpc", True)
        mimetypes.add_type("audio/x-spc", ".spc", True)
        mimetypes.add_type("application/base64", ".mm", True)
        mimetypes.add_type("application/vnd.palm", ".pdb", True)
        mimetypes.add_type("application/x-bzip2", ".bz2", True)
        mimetypes.add_type("application/x-chm", ".chm", True)
        mimetypes.add_type("application/x-genesis-rom", ".gen", True)
        mimetypes.add_type("application/x-ssh-key", ".pub", True)
        mimetypes.add_type("text/cache", ".cache", True)
        mimetypes.add_type("text/plain", ".dat", True)
        mimetypes.add_type("video/x-matroska", ".mkv", True)
        self._count = 0
        self._root = None
        self._position = 0
        self._lastfile = ""
        self._stop = False
        self._mainhandler = mainhandler
        if path[-1] == SEPARATOR:
            self._path = path[:-1]
        else:
            self._path = path
        self._list = ""
        self._last = ""
        self._progress = progress

    #################################
    #Properties
    #################################
    def get_root(self):
        """Property"""
        return self._root

    def get_list(self):
        """Property"""
        return self._list

    def get_count(self):
        """Property"""
        return self._count

    def set_count(self, count):
        """Property"""
        self._count = count

    def get_progress(self):
        """Property"""
        return self._progress

    def get_lastfile(self):
        """Property"""
        return self._lastfile

    def set_lastfile(self, lastfile):
        """Property"""
        self._lastfile = lastfile

    def get_position(self):
        """Property"""
        return self._position

    def set_position(self, position):
        """Property"""
        self._position = position

    def get_last(self):
        """Property"""
        return self._last

    def set_last(self, last):
        """Property"""
        self._last = last
        
    def get_stop(self):
        """Property"""
        return self._stop
    
    def set_stop(self, stop):
        """Property"""
        self._stop = stop

    root = property(get_root)
    list = property(get_list)
    count = property(get_count, set_count) 
    progress = property(get_progress)
    lastfile = property(get_lastfile, set_lastfile)
    position = property(get_position, set_position)
    last = property(get_last, set_last)
    stop = property(get_stop, set_stop)

    #################################
    #Methods
    #################################
    def start_counting(self):
        """Wraps the counting process.
        
        Fires up the counting process in a thread, along with the progress
        bar update method using gobject.timeout_add. Returns the thread. It
        is called from the main handler class.
        """
        fscountthread = threading.Thread(target=self.count_files,
                                         args=(self._path,))
        fscountthread.start()
        self.progress.pulse()
        gobject.timeout_add(80, self.update_progressbar_pulse,
                            fscountthread)
        gobject.timeout_add(500, self.update_progressbar_counting,
                            fscountthread)
        return fscountthread

    def start_indexing(self):
        """Wraps the indexing process.
        
        Fires up the indexing process in a thread, along with the progress
        bar update method using gobject.timeout_add. Returns the thread. It
        is called from the main handler class.
        """
        fsindexthread = threading.Thread(target=self.do_index_process,
                                         args=(self._path, ""))
        fsindexthread.start()
        gobject.timeout_add(500, self.update_progressbar_indexing,
                            fsindexthread)
        return fsindexthread

    def print_dirs(self, _dir):
        """Prints the indexed directories to stdout.
        
        Used for debugging purposes.
        """
        self._list += _dir.__str__() + "\tSize: " + _dir.strsize + "\n"
        self.print_files(_dir)
        for child in _dir.dirs:
            self.print_dirs(child)

    def print_files(self, _dir):
        """Prints the indexed files to stdout.
        
        Used for debugging purposes.
        """
        for child in _dir.files:
            self._list += child.parent + SEPARATOR + child.name\
                            + "\tSize: " + child.strsize
            self._list += "\n"

    def hidden_linux_filter(self, ldir):
        """Filters out "hidden" GNU/Linux files."""
        i = 0
        while i < len(ldir):
            if ldir[i][0] == ".":
                ldir.pop(i)
                i -= 1
            i += 1

    def save_backup_linux_filter(self, ldir):
        """Filters out backup GNU/Linux files."""
        i = 0
        while i < len(ldir):
            if ldir[i][len(ldir[i]) - 1] == "~":
                ldir.pop(i)
                i -= 1
            i += 1

    def parse_size(self, size):
        """Parses the numerical file size and returns it as a string."""
        finalsize = size
        count = 0
        while (finalsize >= 1024):
            finalsize = finalsize / 1024
            count += 1
        finalsize = round(finalsize, 2)
        if count == 0:
            finalsize = str(finalsize) + " B"
        elif count == 1:
            finalsize = str(finalsize) + " KB"
        elif count == 2:
            finalsize = str(finalsize) + " MB"
        elif count == 3:
            finalsize = str(finalsize) + " GB"
        elif count == 4:
            finalsize = str(finalsize) + " TB"
        return finalsize

    def calculate_dir_size(self, _dir):
        """Calculates total directory size."""
        contentsize = 0
        if self._stop is False:
            for _file in _dir.files:
                contentsize += _file.size
            for childdir in _dir.dirs:
                self.calculate_dir_size(childdir)
                contentsize += childdir.size
            _dir.size = contentsize

    def do_index_process(self, path, relpath):
        """The bulk of the indexing process.
        
        It is called recursively for every file and directory found, and
        appends it to the structure.
        """
        if self._stop is True:
            return None
        try:
            dirname = os.path.dirname(path)
            basename = os.path.basename(path)
            absname = dirname + SEPARATOR + basename
            relpath += SEPARATOR
            size = os.path.getsize(absname)
            size = round(size, 2)
            stat = os.stat(absname)
            atime = datetime.datetime.fromtimestamp(stat.st_atime).\
                    strftime("%Y/%m/%d %H:%M:%S")
            mtime = datetime.datetime.fromtimestamp(stat.st_mtime).\
                    strftime("%Y/%m/%d %H:%M:%S")
            root = Directory(dirname, basename, relpath, atime, mtime, size,
                             self.parse_size(size))
            ldir = os.listdir(path)
            ldir.sort(cmp=lambda x, y: cmp(x.lower(), y.lower()))
            if SETTINGS.gnuhidden is True:
                self.hidden_linux_filter(ldir)
            if SETTINGS.savebackup is True:
                self.save_backup_linux_filter(ldir)
            relpath += basename
            for entry in ldir:
                if self._stop is True:
                    return None
                try:
                    rpath = relpath + SEPARATOR
                    self.last = path + SEPARATOR + entry
                    if os.path.isfile(path + SEPARATOR + entry):
                        atime = datetime.datetime.fromtimestamp\
                                (os.path.getatime(path + SEPARATOR + entry)
                                 ).strftime("%Y/%m/%d %H:%M:%S")
                        mtime = datetime.datetime.fromtimestamp\
                        (os.path.getmtime(path + SEPARATOR + entry)
                         ).strftime("%Y/%m/%d %H:%M:%S")
                        mimetype = mimetypes.guess_type(path + SEPARATOR 
                                                        + entry, False)
                        size = os.path.getsize(root.__str__() + SEPARATOR
                                               + entry)
                        size = round(size, 2)
                        if (mimetype[0] is not None and MIMES[mimetype[0]] 
                            == "image"):
                            _file = Photo(root.parent + SEPARATOR +root.name,
                                          entry, rpath, mimetype, atime,
                                          mtime, size, self.parse_size(size))
                        elif (mimetype[0] is not None and MIMES[mimetype[0]] 
                              == "audio" and not mimetype[0] in NOT_AUDIO):
                            _file = Audio(root.parent + SEPARATOR +root.name,
                                          entry, rpath, mimetype, atime,
                                          mtime, size, self.parse_size(size))
                        elif (mimetype[0] is not None and MIMES[mimetype[0]]
                              == "video"):
                            _file = Video(root.parent + SEPARATOR + root.name,
                                          entry, rpath, mimetype, atime,
                                          mtime, size, self.parse_size(size))
                        else:
                            _file = File(root.parent + SEPARATOR +
                                         root.name, entry, rpath, mimetype,
                                         atime, mtime, size,
                                         self.parse_size(size))
                        if root is not None:
                            root.append_file(_file)
                        self._position += 1
                    else:
                        if self._stop is False:
                            _dir = self.do_index_process(path + SEPARATOR +
                                                         entry, relpath)
                            root.append_dir(_dir)
                            self._position += 1
                        else:
                            return None
                except KeyError as error:
                    if SETTINGS.missingmime:
                        MANAGER.\
                        append_event("Error indexing file. Probably the " +
                                     "MIME is not found in the MIME list.", 
                                     absname + SEPARATOR + entry, error, 1)
                        print "Error indexing file: " + absname + SEPARATOR +\
                                entry + ". Probably the MIME is not" +\
                                "found in the MIME list."
                        print error
                except Exception as exc:
                    if SETTINGS.ioerror:
                        MANAGER.\
                        append_event("Error indexing file. I/O error.",
                                     absname + SEPARATOR + entry, exc, 2)
                        print "Error indexing file: " + absname + SEPARATOR +\
                                entry + ". I/O error."
                        print exc
            if root is not None:
                self.calculate_dir_size(root)
                root.strsize = self.parse_size(root.size)
                if (root.__str__() == self._path):
                    self._root = root
                return root
        except Exception as exc:
            if SETTINGS.ioerror:
                MANAGER.append_event("Error indexing directory. I/O error",
                                     absname, exc, 2)
            print "Error indexing directory: " + absname 
            print exc
            return root

    def count_files(self, path):
        """Counts files in the target directory.
        
        This method is used to provide some data to the progress bar to be
        displayed, so the user has an idea of what the program has done so far
        """
        for root, dirs, files in os.walk(path):
            if self._stop is True:
                return None
            if SETTINGS.gnuhidden is True:
                self.hidden_linux_filter(files)
                self.hidden_linux_filter(dirs)
            if SETTINGS.savebackup is True:
                self.save_backup_linux_filter(files)
                self.save_backup_linux_filter(dirs)
            self._count += len(files)
            self._count += len(dirs)

    def update_progressbar_pulse(self, fscountthread):
        """Pulses the progress bar."""
        if self._stop is True:
            return False
        if not fscountthread.is_alive():
            self.progress.set_fraction(0)
            return False
        else:
            self.progress.pulse()
            return True

    def update_progressbar_counting(self, fscountthread):
        """Updates the progressbar while in counting mode."""
        if self._stop is True:
            return False
        if not fscountthread.is_alive():
            return False
        else:
            self.progress.set_text(str(self.count) +
                                   " files and counting, please wait...")
            return True

    def update_progressbar_indexing(self, fsthread):
        """Updates the progressbar while in indexing mode."""
        if self._stop is True:
            return False
        if not fsthread.is_alive():
            self.progress.set_text("Completed indexing "
                                   + str(self.count) + " files.")
            self.progress.set_fraction(1.0)
            gobject.timeout_add(2000, self._mainhandler.hide_progressbar)
            return False
        else:
            self.progress.set_text(self.last)
            self.progress.set_fraction(round(float(self.position), 2)
                                       / self.count)
            return True
