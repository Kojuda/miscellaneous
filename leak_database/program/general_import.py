import import_scripts, os
from program.database import Database
from pymongo import collection
import phonenumbers, logging, re
from phonenumbers import geocoder
from phonenumbers import carrier

class Importation(Database) :
    """General class to handle importation of leak files."""

    ACCEPTED_EXT=["txt"]

    def __init__(self, script, fleaks, url):
        self.script = script
        self.fleaks = fleaks
        self.url_database = url
        self.custom_importation()
        # self.rec_fol_listing()

    def rec_fol_listing(self, folder=None) :
        """Function to iterate through the different files of a leak folder."""
        if folder is None:
            folder = self.fleaks
        files=os.scandir(folder)
        for filename in files:
            if os.path.isdir(filename):
                self.rec_fol_listing(filename)
            elif filename.is_file() :
                #Verifiy if the file has already been extracted
                fname=filename.path.split("\\")[-1]
                cursor = Database._db.get_collection(Database.col_leak_imports).find({"filename" : fname})
                #Looking special function of cursor from the debugger
                if cursor.count() == 0 :
                    self.extract(filename)
                else :
                    print(f"{filename.path} has already been imported.")
            else :
                print(f"{filename.path} is not a file.")

    def extract(self, filename : str):
        """Function to implement in order to describe a specific parsing of a leak file."""

        raise NotImplementedError("Please Implement this method.")

    @staticmethod
    def parse_phone(pnumber : str, doc : object) -> object :
        """Parse phone number with the phonenumbers library."""
        try :
            parsed_number=phonenumbers.parse(pnumber, None)
            if phonenumbers.is_possible_number(parsed_number) :
                int_number=phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.INTERNATIONAL); doc["phone_number"]["raw"] = int_number
                zone_phone=geocoder.description_for_number(parsed_number, "en"); doc["phone_number"]["zone_phone"] = zone_phone
                pcarrier=carrier.name_for_number(parsed_number, "en"); doc["phone_number"]["carrier"] = pcarrier
                doc["phone_number"]["ind"]=parsed_number.country_code
                doc["phone_number"]["number"]=parsed_number.national_number
                return doc
            else :
                logging.info(f"Not a phone number : {pnumber}");print(f"Not a phone number : {pnumber}")
                return doc
                
        except phonenumbers.phonenumberutil.NumberParseException as e:
            logging.error(f"Can't parse supposed phone number : {pnumber}");print(f"Can't parse supposed phone number : {pnumber}")
            return doc

    @staticmethod
    def parse_email(r_email : str, doc : object) -> object :
        """Parse emails with the phonenumbers library."""
        if r_email != "" :
            doc["email"]["raw"]=r_email
            _=r_email.split("@")[1].split(".")
            doc["email"]["tld"]=_[-1]
            doc["email"]["domain"]=_[-2]
            return doc
        else :
            return doc

    def custom_importation(self) :
        """Function to call a specified script of importation. The script must be put
        inside the ./import_scripts folder of the project."""

        #exec(f"from program.{script} import *")
        exec("import import_scripts.{}".format(self.script.split(".")[-2].split("/")[-1]))
        #a="import import_scripts.{}".format(self.script.split(".")[-2].split("/")[-1])
        
        exec("import_scripts.{}.entry_point(self.script, self.fleaks, self.url_database)".format(self.script.split(".")[-2].split("/")[-1]))