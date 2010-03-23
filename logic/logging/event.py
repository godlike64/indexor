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

"""Module for the handling of events

This module defines a constant for the different event types, and then two
classes: one for the events itself, and another one to manage all events
occurred in a program instance.
"""

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
    
    """Class that represents an event"""

    def __init__(self, msg, filename, err, _type, location, date):
        self._msg = msg
        self._filename = filename
        self._err = err
        self._type = _type
        self._location = location
        self._date = date

    #################################
    #Properties
    #################################        
    def get_msg(self):
        """Property"""
        return self._msg
    
    def get_err(self):
        """Property"""
        return self._err
    
    def get_location(self):
        """Property"""
        return self._location
    
    def get_date(self):
        """Property"""
        return self._date
    
    def get_type(self):
        """Property"""
        return self._type
    
    def get_filename(self):
        """Property"""
        return self._filename
    
    msg = property(get_msg)
    err = property(get_err)
    location = property(get_location)
    date = property(get_date)
    type = property(get_type)
    filename = property(get_filename)

class EventManager(object):
    
    """Class that manages all events occurred in an instance of the program
    
    Every time an event happens (identified in an exception elsewhere), the
    append_event method is called, with some parameters. As an extra, this
    class uses the inspect module to track down which function at which file
    and at which line caused the event (or called the append_event method). If
    SETTINGS.debug is set, then it will print the stack accessible with
    inspect to stdout.
    This class also registers the date in which the event happened.
    """
    
    def __init__(self, loghandler=None):
        self._events = []
        self._loghandler = loghandler

    #################################
    #Properties
    #################################
    def get_events(self):
        """Property"""
        return self._events
    
    def get_loghandler(self):
        """Property"""
        return self._loghandler
    
    def set_loghandler(self, loghandler):
        """Property"""
        self._loghandler = loghandler
    
    events = property(get_events)
    loghandler = property(get_loghandler, set_loghandler)
        
    #################################
    #Methods
    #################################
    def append_event(self, msg, filename, err, _type):
        """Add an event to the events' list"""
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
        event = Event(msg, filename, err, _type, location, date)
        self._events.append(event)
        if self._loghandler is not None:
            self._loghandler.add_event_to_store(event)
    
    def save_to_disk(self, destination):
        """Save the event list to a plaintext file"""
        EventPlainTextWriter(self._events, destination)