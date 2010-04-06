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

import os, sys, glob, fnmatch

## Added 10 Jan 2008
from distutils.core import setup, Extension
import distutils.command.install_data

def find_data_files(srcdir, *wildcards, **kw):
    # get a list of all files under the srcdir matching wildcards,
    # returned in a format to be used for install_data
    def walk_helper(arg, dirname, files):
        if '.svn' in dirname:
            return
        names = []
        lst, wildcards = arg
        for wc in wildcards:
            wc_name = opj(dirname, wc)
            for f in files:
                filename = opj(dirname, f)

                if fnmatch.fnmatch(filename, wc_name) and not
                os.path.isdir(filename):
                    names.append(filename)
        if names:
            lst.append((dirname, names))

    file_list = []
    recursive = kw.get('recursive', True)
    if recursive:
        os.path.walk(srcdir, walk_helper, (file_list, wildcards))
    else:
        walk_helper((file_list, wildcards),
                    srcdir,
                    [os.path.basename(f) for f in glob.glob(opj(srcdir, '*'))])
    return file_list

## This is a list of files to install, and where:
## Make sure the MANIFEST.in file points to all the right 
## directories too.

files = find_data_files('indexor/', '*.*')

setup(name = "indexor",
    version = constants.VERSION,
    description = constants.DESC,
    author = constants.AUTHOR,
    author_email = constants.EMAIL,
    license = "GNU GPLv3",
    url = constants.SITE,
    packages = ['indexor'],

    data_files = files,

    ## Borrowed from wxPython too:
    ## Causes the data_files to be installed into the modules directory.
    ## Override some of the default distutils command classes with my own.
    #cmdclass = { 'install_data':    wx_smart_install_data },

    #'fontypython' and 'fp' are in the root.
    scripts = ["scripts/indexor"],
    #long_description = fontypythonmodules.strings.long_description,
    #classifiers = [
    #  'Development Status :: 4 - Beta',
    #  'Environment :: X11 Applications :: GTK',
    #  'Intended Audience :: End Users/Desktop',
    #  'Intended Audience :: Developers',
    #  'License :: OSI Approved :: GNU General Public License (GPL)',
    #  'Operating System :: POSIX :: Linux',
    #  'Programming Language :: Python',
    #  'Topic :: Desktop Environment',
    #  'Topic :: Text Processing :: Fonts'
    #  ]
)
