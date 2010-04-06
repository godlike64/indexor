#!/usr/bin/python
# -*- coding: utf-8 -*-

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

#Local imports
from logic.input.indexer import Indexer
from controller.mainhandler import MainHandler

#Regular imports
import pygtk
pygtk.require('2.0')
import gtk
import gobject
import os

class Main(object):

    def __init__(self):
        gobject.threads_init()
        handler = MainHandler("view/indexor.glade")
        gtk.main()

if __name__ == "__main__":
    Main()
