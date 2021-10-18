from program.database import Database
from program.general_import import Importation
import traceback, sys, os, time
import logging, copy
import multiprocessing as mp
# from multiprocessing import Process, Manager
# from multiprocessing.managers import BaseManager
from pymongo import MongoClient
import ctypes




CORES=8

class Custom_Importation(Importation) :
    """Class to handle a custom script to import a specific leak format."""

    db=Database.getDB()

    def __init__(self, script, fleaks, url):
        #super().__init__(script, fleaks)
        self.script = script
        self.fleaks = fleaks
        self.url_database = url
        self.rec_fol_listing()
    
    @staticmethod
    def process_connect_DB(url) :
        client=MongoClient(url)
        db=client["db_leaks"]
        return db
    
    def buf_count_newlines_gen(fname : str) -> int:
        """Most efficient function to count the number of lines from a file."""
        def _make_gen(reader):
            b = reader(2 ** 16)
            while b:
                yield b
                b = reader(2 ** 16)

        with open(fname, "rb") as f:
            count = sum(buf.count(b"\n") for buf in _make_gen(f.raw.read))
        return count

    def extract(self, filename : object, multiproc = True) :
        """Overriding function to parse specific leak file.
        Multiprocessing is available."""


        if not multiproc :

            if (filename.path.split(".")[-1] in self.ACCEPTED_EXT or "." not in filename.path.split("\\")[-1]) :
                print(f"Analyzing {filename.path}. . .")
                f = open(filename.path, 'r', encoding='utf-8', errors='ignore')
                lines = f.readlines()
                documents=self.parse_lines(lines, filename)
                
                f.close()
                Database.getDB().get_collection(Database.col_leaks).insert_many(documents)
                Database.getDB().get_collection(Database.col_leak_imports).insert({
                    "leak_name" : self.script.split("/")[-1].split(".")[-2],
                    "filename" : filename.path.split("\\")[-1]
                    })
            else :
                    print(f"Extension of {filename.path} is not handled.")
        else :
            # BaseManager.register('sharedDB', Database)
            # manager = BaseManager()
            # manager.start()
            # shared_db = manager.sharedDB()

            # manager=Manager()
            # ns=manager.Namespace()
            # ns.db = Database.getDB()
            pool = mp.Pool(CORES)
            jobs = []

            #create jobs
            lock=False

            # shared_url=manager.Value("s", self.url_database)

            print("Multiprocessing with {} cores.\nAnalyzing {}. . .".format(CORES, filename.path))
            tot_lines = sum(1 for _ in open(filename.path, 'r', encoding='utf-8', errors='ignore'))
            for chunkStart,chunkSize in self.chunkify(filename.path):
                jobs.append( pool.apply_async(
                    self.process_wrapper,
                    (
                        chunkStart,
                        chunkSize,
                        filename.path,
                        self.url_database,
                        tot_lines,
                        lock
                    )
                ))
            
            #wait for all jobs to finish
            for job in jobs:
                job.get()
            
            #clean up
            pool.close()

            Database.getDB().get_collection(Database.col_leak_imports).insert({
                "leak_name" : self.script.split("/")[-1].split(".")[-2],
                "filename" : filename.path.split("\\")[-1]
                })

    def process_wrapper(self, chunkStart, chunkSize, filename, url="mongodb://127.0.0.1:27017", tot_lines=None, lock=False):
        """Function to give to a process in order to create parallelism."""

        db=self.process_connect_DB(url)

        if (filename.split(".")[-1] in self.ACCEPTED_EXT or "." not in filename.split("\\")[-1]) :
            f = open(filename, 'r', encoding='utf-8', errors='ignore')
            f.seek(chunkStart)
            lines = f.read(chunkSize).splitlines()
            documents=self.parse_lines(lines, filename, db, lock)
            f.close()
            db.get_collection(Database.col_leaks).insert_many(documents)
            print("Total of lines : {}".format(tot_lines))
        else :
            print(f"Extension of {filename} is not handled.")


    def chunkify(self,fname,size=1024*1024*10):
        """Explode the file into several chunks of lines."""

        fileEnd = os.path.getsize(fname)
        with open(fname,'r', encoding='utf-8', errors='ignore') as f:
            chunkEnd = f.tell()
            while True:
                chunkStart = chunkEnd
                f.seek(chunkStart+size, 0) #os.SEEK_SET
                f.readline()
                chunkEnd = f.tell()
                yield chunkStart, chunkEnd - chunkStart
                if chunkEnd > fileEnd:
                    break

    def parse_lines(self, lines : list, filename : str, shared_db : object,  lock = False) :
        retrieved_documents=[]
        retrieved_rdocus=[]
        retrieved_raw_ids=[]
        lenlines=len(lines)
        line_partial_flag=False;line_partial="";tmp_count=0
        for line, nline in zip(lines, range(1, len(lines)+1)) :
            #Remove the creating hour because of the separators
            line=line.replace("12:00:00", "")
            tmp_count=+line.count(":")
            #Resolve case where the line is broken by \n. 12 is number of fields. 
            if tmp_count < 11 :
                line_partial=line_partial+line.strip("\n")
                line_partial_flag=True
            elif tmp_count ==11 :
                tmp_count=0
                if  line_partial_flag :
                    line = line_partial + line.strip("\n")
                    line_partial_flag = False
                    line_partial = ""
                try :
                    #Insert the line inside the raw collection and retrieve the raw_id
                    # raw_id= shared_db.get_collection(Database.col_raw).insert({"data" : line}) #Database.getDB()
                    raw_id =
                    retrieved_raw_ids.append(raw_id)
                    #Create empty doc to fill. 
                    doc = copy.deepcopy(Database.base_leak_doc)
                    doc["filename"] = filename.split("\\")[-1]
                    line=line.split(":"); doc["line_number"] = nline
                    pnumber=f"+{line[0]}"
                    doc = self.parse_phone(pnumber, doc)
                    doc= self.parse_email(line[10], doc)
                    doc["leak_name"]= ""
                    doc["first_name"] = line[2]
                    doc["last_name"] = line[3]
                    doc["gender"] = line[4]
                    doc["platform"] = "Facebook"
                    doc["work"] = line[8]
                    doc["country_residence"] = line[6]
                    doc["birth_date"] = line[11]
                    doc["raw_id"] = raw_id
                    retrieved_documents.append(doc)
                except IndexError as e :
                    _="Line {} from {} has a problem : {}\n{}".format(nline, filename, line,traceback.format_exc() )
                    logging.error(_);print(_)
                except KeyboardInterrupt as e:
                    print("Cleaning raw collection from errors.")
                    shared_db.get_collection(Database.col_raw).delete_many(retrieved_raw_ids)
                    logging.error(traceback.format_exc())
                    sys.exit(f"Running code has been interrupted by the user : {e}")
                except Exception as e :
                    #Cleaning in case of error.
                    print("Cleaning raw collection from errors.")
                    shared_db.get_collection(Database.col_raw).delete_many({ "_id" : retrieved_raw_ids})
                    logging.error(traceback.format_exc())
                    sys.exit(f"Unkown error during parsing of a file : {e}")
                if nline % 10000 == 0 :
                    print(f"Line : {nline} / {lenlines} (Process : {mp.current_process()})")
            else :
                _ = f"Incoherent number of ':' at line {nline} of {filename}."
                logging.debug(_);print(_)
        return retrieved_documents




def entry_point(script :str , fleaks : str, url : str) :
    Custom_Importation(script, fleaks, url)
