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

"""This module handles the writing of the resulting catalog in plain text
form.

The constants defined in this module are used when writing the matrix that
will be saved to a file (see below).
"""

import sys

from logic.logging.event import TYPES

BLANK = "    "
LAST = "`-- "
LINE = "|   "
CHILD = "|-- "

class PlainTextWriter(object):
    
    """Class that writes the catalog to a plain text file.
    
    The writing mimics the output from the `tree` GNU/Linux command, or
    the Norton Commander's "tree" function. In order to do so, a matrix is
    used.
    """
    
    def __init__(self, filename, root):
        if sys.platform == "win32":
            self._newline = "\\\n"
        else:
            self._newline = "/\n"
        outputfile = open(filename, 'w')
        self._depth = 0
        self._count = 0
        self.get_depth_limit(root, self._depth + 1)
        self.get_number_limit(root)
        self._matrix = []
        for i in range(self._count + 1):
            self._matrix.append([BLANK] * (self._depth + 2))
        self._dest = 0
        self.populate_matrix(root, 0, 0, None)
        for row in self._matrix:
            for item in row:
                outputfile.write(item)
            outputfile.write("\n")
        outputfile.close()
            
    def is_last_dir(self, parent, _dir):
        """Check if the directory is the last in its array."""
        if (parent is not None) and (_dir is parent.dirs[-1]):
            return True
        else:
            return False
        
    def is_last_file(self, parent, _file):
        """Check if the file is the last in its array."""
        if _file is parent.files[-1]:
            return True
        else:
            return False

    def get_depth_limit(self, root, depth):
        """Get the maximum directory depth (right limit)."""
        for _dir in root.dirs:
            if depth > self._depth:
                self._depth = depth
            self.get_depth_limit(_dir, depth + 1)
            
    def get_number_limit(self, root):
        """Get the maximum number of files and dirs (bottom limit)."""
        for _file in root.files:
            self._count += 1
        for _dir in root.dirs:
            self._count += 1
            self.get_number_limit(_dir)
    
    def populate_matrix(self, _dir, par, col, parent):
        """Populate the matrix with the data from the structure."""
        if self._dest == 0:
            self.print_to_matrix(_dir, par, col, parent, True)
            col += 1
        for child in _dir.dirs:
            self.print_to_matrix(child, par, col, _dir, True)
            self.populate_matrix(child, self._dest - 1, col + 1, _dir)
        for _file in _dir.files:
            self.print_to_matrix(_file, par, col, _dir, False)
            
    def print_to_matrix(self, node, par, col, parent, isdir):
        """Fill the matrix.
        
        Checks are in place in order to know which set of four characters
        (see module constants) to append, depending on the entry to be
        written, if it is last in its array and the previously written
        line.
        """
        if self._dest == 0:
            self._matrix[self._dest][col] = node.name + "/"
        else:
            i = 0
            while (i < col - 1):
                if self._matrix[par][i] == CHILD:
                    self._matrix[self._dest][i] = LINE
                elif self._matrix[par][i] == LAST:
                    self._matrix[self._dest][i] = BLANK
                else:
                    self._matrix[self._dest][i] = self._matrix[par][i]
                i += 1
            if isdir:
                if (self.is_last_dir(parent, node)) & (len(parent.files)
                                                       == 0):
                    self._matrix[self._dest][i] = LAST
                else:
                    self._matrix[self._dest][i] = CHILD
                self._matrix[self._dest][i + 1] = node.name + "/"
            else:
                if self.is_last_file(parent, node):
                    self._matrix[self._dest][i] = LAST
                else:
                    self._matrix[self._dest][i] = CHILD
                self._matrix[self._dest][i + 1] = node.name
        self._dest += 1
        
class EventPlainTextWriter(object):
    
    """Class that writes the log events to a plaintext file"""
    
    def __init__(self, events, destination):
        outputfile = open(destination, "w")
        self._write_to_disk(events, outputfile)
        outputfile.close()
        
    def _write_to_disk(self, events, outputfile):
        """Writes the events to disk"""
        for event in events:
            outputfile.write("Message: " + event.msg + "\n")
            outputfile.write("Filename: " + event.filename + "\n")
            outputfile.write("Error: " + str(event.err) + "\n")
            outputfile.write("Type: " + TYPES[event.type] + "\n")
            outputfile.write("Location: " + event.location + "\n")
            outputfile.write("Date: " + event.date + "\n")
            outputfile.write("=" * 79 + "\n")