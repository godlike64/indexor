import sqlobject

from logic.input.dbmanager import CATALOGDIR
from fs.entities import FileAbstract, MetaDir
from constants import ICONS, MIMES

class Crawler(object):

    def __init__(self, searchhandler, filename):
        self._searchhandler = searchhandler
        self._filename = filename
        con_str = "sqlite://" + CATALOGDIR + filename
        self._con = sqlobject.connectionForURI(con_str)
        self._metadir = MetaDir.select(connection = self._con)[0]

    def get_name(self):
        return self._metadir.name

    def get_target(self):
        return self._metadir.target

    name = property(get_name)
    target = property(get_target)


    def search(self, term):
        results = FileAbstract.select("""file_abstract.name LIKE '%""" + term + """%'""", connection = self._con)
        for file in results:
            index = self.find_text(file.name, term)
            name2 = file.name.decode("utf-8")
            str2 = file.__str__().decode("utf-8")
            text2 = term.decode("utf-8")
            namemarkup = name2[0:index]
            namemarkup += "<b>"
            namemarkup += name2[index:index + len(text2)]
            namemarkup += "</b>"
            namemarkup += name2[index + len(text2):len(name2)]
            namemarkup += "\n" + str2
            node = [ICONS[MIMES[file.mimetype]], namemarkup.replace("&", "&amp;"), file.strsize, file.__str__(), file.parent, file.size, self._filename, file.name]
            #self._searchhandler.lssearch.append([ICONS[MIMES[file.mimetype]], namemarkup.replace("&", "&amp;"),
            #                       file.strsize, file.__str__(), file.parent,
            #                       file.size])
            self._searchhandler.notify_and_add(self, node)

    def find_text(self, name, text):
        """Returns the result of the search with lowercase values."""
        return name.lower().find(text.lower())
