from os import listdir
from datetime import datetime
import json
import shutil

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
            self.deleteOldest(backups)

    def deleteOldest(self, backups):
        backupDates = []
        for backup in backups:
            backupDates.append(datetime.strptime(backup, "%d-%m-%Y"))
        earliest = min(backupDates)
        earliestFormat = earliest.strftime("%d-%m-%Y")
        shutil.rmtree(self.dest + "/" + earliestFormat)
        print("File " + earliestFormat + " has been removed successfully!")


