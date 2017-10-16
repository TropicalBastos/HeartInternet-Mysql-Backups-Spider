from os import listdir
from datetime import datetime
import json

#maintains the backups by imposing a limit and deleting
#oldest backups

class Maintainer(object):

    def __init__(self, dest):
        self.dest = dest
        with open("config.json", "r") as config:
            self.limit = json.load(config)["limit"]

    def maintain(self):
        self.checkDir()

    def checkDir(self):
        backups = listdir(self.dest)
        file_count = len(backups)
        if file_count >= self.limit:
            #TODO delete oldest backup
            print("delete oldest backup here")

    def deleteOldest(self, backupsDir):
        for backup in backupsDir:
            print(backup)

