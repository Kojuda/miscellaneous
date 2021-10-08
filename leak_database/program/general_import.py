import import_scripts, os
from program.database import Database


class Importation(Database) :

    ACCEPTED_EXT=["txt"]

    __db=super().getDB()

    def __init__(self, script, fleaks):
        self.script = script
        self.fleaks = fleaks
        self.importation()
        # self.rec_fol_listing()

    def rec_fol_listing(self) :
        files=os.scandir(self.fleaks)
        for filename in files:
            if os.path.isdir(filename):
                self.rec_fol_listing(filename)
            elif filename.is_file() :
                if :
                self.extract(filename)
            else :
                print(f"{filename.path} is not a file.")

    def extract(self):
        raise NotImplementedError("Please Implement this method.")


    def importation(self) :
        #exec(f"from program.{script} import *")
        exec("import_scripts.{}.entry_point()".format(self.script.split(".")[-2]))