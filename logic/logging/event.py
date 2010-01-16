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

import datetime
import time
import inspect

from logic.midput import SETTINGS


TYPES = {
             1  :   "Missing mimetype",
             2  :   "I/O error",
             3  :   "Metadata error",
             4  :   "Missing icon",
             5  :   "Thumbnail error",
        }

from logic.output.plaintext import EventPlainTextWriter

class Event(object):

    def __init__(self, msg, filename, err, type, location, date):
        self._msg = msg
        self._filename = filename
        self._err = err
        self._type = type
        self._location = location
        self._date = date

    #################################
    #Properties
    #################################        
    def get_msg(self):
        return self._msg
    
    def get_err(self):
        return self._err
    
    def get_location(self):
        return self._location
    
    def get_date(self):
        return self._date
    
    def get_type(self):
        return self._type
    
    def get_filename(self):
        return self._filename
    
    msg = property(get_msg)
    err = property(get_err)
    location = property(get_location)
    date = property(get_date)
    type = property(get_type)
    filename = property(get_filename)

class EventManager(object):
    
    def __init__(self, loghandler=None):
        self._events = []
        self._loghandler = loghandler

    #################################
    #Properties
    #################################
    def get_events(self):
        return self._events
    
    def get_loghandler(self):
        return self._loghandler
    
    def set_loghandler(self, loghandler):
        self._loghandler = loghandler
    
    events = property(get_events)
    loghandler = property(get_loghandler, set_loghandler)
        
    #################################
    #Methods
    #################################
    def append_event(self, msg, filename, err, type):
        #SETTINGS.debug = True
        if SETTINGS.debug is True:
            for i in inspect.stack():
                print "Function " +  i[3] + " on file " +\
                                i[1] + " at line " + \
                                str(i[2])
        location = "Function " +  inspect.stack()[1][3] + " on file " +\
                            inspect.stack()[1][1] + " at line " + \
                            str(inspect.stack()[1][2])
        date = datetime.datetime.fromtimestamp(time.time())\
                        .strftime("%Y/%m/%d %X")
        event = Event(msg, filename, err, type, location, date)
        self._events.append(event)
        if self._loghandler is not None:
            self._loghandler.add_event_to_store(event)
    
    def save_to_disk(self, destination):
        EventPlainTextWriter(self._events, destination)