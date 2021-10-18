
import os, argparse, sys
from pathlib import Path
import program.database
import functools, time
#import program.general_import
import logging

os.chdir(os.path.dirname(r"{}".format(str(os.path.abspath(__file__)))))

IMPORT="./import_scripts"
#logging.basicConfig(filename='./MongoLeaks.log', filemode="w", encoding='utf-8', level=logging.DEBUG, format='%(asctime)s:%(levelname)s:%(message)s')
#Logging
logging.basicConfig(
    handlers=[
        logging.FileHandler(
                        filename="./MongoLeaks.txt",
                        encoding='utf-8',
                        mode='a+'
                        )],
        format="%(asctime)s %(name)s:%(levelname)s:%(message)s",
        datefmt="%F %A %T",
        level=logging.DEBUG
)

#action="store_true"
parser = argparse.ArgumentParser(description='Program to manage a database containing different leaks.', conflict_handler="resolve")
parser.add_argument('-d','--database', type=str, help='URL used to connect to the database.\nExample : mongodb://127.0.0.1:27017/', required=False, nargs=1)
parser.add_argument('-p','--password', type=str, help='Password to connect to the database.', required=False, nargs=1)
parser.add_argument('-s','--script', type=str, help='Name of python script used to import under ./import.', required=False, nargs=1)
parser.add_argument('-i','--imports', type=str, help='Path of the folder containing the leaks to import.', required=False, nargs=1)
args = vars(parser.parse_args())

def timer(func):
    """Print the runtime of the decorated function"""
    @functools.wraps(func)
    def wrapper_timer(*args, **kwargs):
        start_time = time.perf_counter()    # 1
        value = func(*args, **kwargs)
        end_time = time.perf_counter()      # 2
        run_time = end_time - start_time    # 3
        print(f"Finished {func.__name__!r} in {run_time:.4f} secs")
        return value
    return wrapper_timer

#@timer

if len([_ for _ in (args["script"],args["imports"]) if _ is not None]) == 1:
    parser.error('--script and --imports must be given together')
    parser.print_help()#parser.print_help(sys.stderr)
    sys.exit()


if __name__ == "__main__" :
    [script, imp, url] = "{}/{}".format(IMPORT, args["script"][0]), args["imports"][0], args["database"][0]
    if args["database"][0] is not None :
        # BaseManager.register('sharedDB',program.database.Database(args["database"][0]))
        program.database.Database(args["database"][0])
        import program.general_import
        

        if Path(script).is_file() and script.split(".")[-1] == "py"  :
            if os.path.isdir(imp) :

                program.general_import.Importation(script, imp, url)
            else :
                sys.exit("Leak folder is not valid.")
        else :
            sys.exit("Importation script is not valid.")
    else : 
         sys.exit("You must provide the connection URL to the database.")
