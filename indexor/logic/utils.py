import os
from sqlobject import connectionForURI

from fs.entities import MetaDir
from logic.midput.settings import CATALOGDIR

def clean_catalog_dir():
    for file_ in os.listdir(CATALOGDIR):
        if file_.split(".")[-1] == "db-journal":
            os.remove(CATALOGDIR + file_)
    for file_ in os.listdir(CATALOGDIR):
        con_str = "sqlite://" + CATALOGDIR + file_
        conn = connectionForURI(con_str)
        metadircount = MetaDir.select(connection = conn).count()
        if metadircount == 0:
            os.remove(CATALOGDIR + file_)
        