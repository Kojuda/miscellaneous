from pymongo import MongoClient
import traceback, logging, sys
from MongoLeaks import parser

# pprint library is used to make the output look more pretty
#from pprint import pprint
#db=client.admin
# Issue the serverStatus command and print the results
#serverStatusResult=db.command("serverStatus")
#pprint(serverStatusResult)

#db.createCollection("mycol", { capped : true, autoIndexID : true, size : 6142800, max : 10000 } )


class Database(object) :
    "Signleton implementation of the database."

    __instance = None
    __client = None
    __db = None

    def getInstance(cls):
        """ Static access method. """

        if cls.__instance == None:
            logging.error("No current instance of the database.");sys.exit("No current instance of the database.")
        return cls.__instance

    def getDB(cls):
        """ Static access to the current DB. """

        return cls.__db

    def __init__(self, url):
        if Database.__instance != None:
            raise Exception("This class is a singleton!")
        else :
            try :
                Database.client = self.__connect_db(url)
            except Exception as e:
                logging.error(traceback.format_exc())
                parser.print_help()#parser.print_help(sys.stderr)
                sys.exit("Verify the URL or the database's connectivity.")
            try :
                Database.db = self.__init_db(self.client)
            except Exception as e:
                parser.print_help()#parser.print_help(sys.stderr)
                logging.error(traceback.format_exc());sys.exit("Impossible to init the database.")

            self.base_leak_doc =  {
                        "filename" : "",
                        "line_number" : "",
                        "plateform" : "",
                        "first_name" : "",
                        "last_name" : "",
                        "birth_date" : "",
                        "nationality" : "",
                        "country_residence" : "",
                        "work" : "",
                        "pseudonym" : "",
                        "account_id" : "",
                        "gender" : "",
                        "email" : {
                            "raw" : "",
                            "tld" : "",
                            "domain" : ""
                        },
                        "location" : "",
                        "phone_number" : {
                            "raw" : "",
                            "ind" : "",
                            "number" : "",
                            "zone" : "",
                            "carrier" : ""

                        },
                        "raw_id" : ""
                        
                    }
            Database.__instance = self

    def __connect_db(self, url : str) -> object :
        """Connect to the database."""

        try :

            client = MongoClient(url)
            return client
        except Exception as e:
            logging.error(traceback.format_exc())
            parser.print_help()#parser.print_help(sys.stderr)
            sys.exit("Verify the URL or the database's connectivity.")

    def __init_db(self, client : object) :
        """Init the database with its collections."""

        try :

            if "db_leaks" not in client.list_database_names() :
                db=client["db_leaks"]
            else :
                logging.info("Retrieving existing database.")
                db=client.db_leaks
            collist = db.list_collection_names()
            colnames = ["leaks", "raw", "leak_imports"]
            for col in colnames :
                if col not in collist:
                    logging.info(f"The collection {col} does not exist.")
                    db.create_collection(col, capped = False, autoIndexID = True)
            return db
        except Exception as e:
            logging.error(traceback.format_exc())
            parser.print_help()#parser.print_help(sys.stderr)
            sys.exit("Impossible to init the database.")

      
