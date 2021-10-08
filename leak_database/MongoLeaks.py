import os, argparse, datetime, re, sys
import program.database
import program.general_import
import traceback, logging
from pymongo import MongoClient
os.chdir(os.path.dirname(r"{}".format(str(os.path.abspath(__file__)))))

IMPORT="./import_scripts"
logging.basicConfig(filename='./MongoLeaks.log', filemode="w", encoding='utf-8', level=logging.DEBUG, format='%(asctime)s:%(levelname)s:%(message)s')

#action="store_true"
parser = argparse.ArgumentParser(description='Program to manage a database containing different leaks.', conflict_handler="resolve")
parser.add_argument('-d','--database', type=str, help='URL used to connect to the database.\nExample : mongodb://127.0.0.1:27017/', required=False, nargs=1)
parser.add_argument('-p','--password', type=str, help='Password to connect to the database.', required=False, nargs=1)
parser.add_argument('-s','--script', type=str, help='Name of python script used to import under ./import.', required=False, nargs=1)
parser.add_argument('-i','--imports', type=str, help='Path of the folder containing the leaks to import.', required=False, nargs=1)
args = vars(parser.parse_args())

if len([_ for _ in (args.script,args.imports) if _ is not None]) == 1:
    parser.error('--script and --imports must be given together')
    parser.print_help()#parser.print_help(sys.stderr)
    sys.exit()


if __name__ == "__main__" :
    
    program.database.Database(args["database"][0])

    [script, imp] = "{}/{}".format(IMPORT, args["script"]), args["imports"]

    if script.is_file() and script.path.split(".")[-1] == "py"  :
        if os.path.isdir(imp) :

            program.general_import.Importation(script, imp)
        else :
            sys.exit("Leak folder is not valid.")
    else :
        sys.exit("Importation script is not valid.")
