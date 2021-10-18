#
#Author : Danny Kohler 
#Date : 2021/10/07


import os, argparse, datetime, re, sys
from itertools import chain, combinations
os.chdir(os.path.dirname(r"{}".format(str(os.path.abspath(__file__)))))


RESULT_FOLDER="script_results"
BANNED_EXT=["py", "gz", "xlsx", "json", "js", "exe"]
ACCEPTED_EXT=["txt"]
PWD="."
BANNED_FOLDER=["program"]


parser = argparse.ArgumentParser(description='Program to search through different leak files.')
parser.add_argument('-s','--string', type=str, help='General string to search (email, phone number, pseudonyms, ...). Example "John Marston".', required=False, nargs=1)
#parser.add_argument('-w','--whois', action="store_true", help='Use IPNETINFO to complete CSV file.', required=False)
parser.add_argument('-p','--phone', type=str, help='Phone number with indicative (Example : "+IND XXXXXXXXXXXX...").', required=False, nargs=1)
args = vars(parser.parse_args())


#logs.lparse(args["path"][0])

def word_combination(wlist:list) -> list :
    """Create a list of lists containing all word combinations."""

    if wlist and len(wlist)>1:
        return chain(*map(lambda x: combinations(wlist, x), range(1, len(wlist)+1)))
    else :
        return wlist
        
def reg_phone(str_phone:str) -> object:
    """ Create several regexes to search variants."""

    [ind, nph]=str_phone.strip("+").split(" ")
    #Cut off the local 0
    #Create regexes for 3 cases : with IND and without 0, without IND and with 0, without IND and 0
    formats=[\
        "(?P<ind>{})? ?0?(?P<num>{})".format(ind, ' ?'.join(list(nph.rstrip('0'))))
        ]
    return re.compile(f'({"|".join(formats)})')

def reg_name(nstr:str) -> object :
    """Create several regexes to search variants of pseudonyms and names.
    Consider several orders of the words. Being case-insensitive."""

    elements=nstr.split(" ")
    combs=word_combination(elements)
    lregex=[]
    for comb in combs :
        if len(comb) > 1 :
            lregex.append("(?i:{})".format('[\.\- _,;:]?'.join(comb))) #Here to change character seperation between the words
        elif len(comb) == 1 :
            lregex.append("(?i:{})".format(comb))
        else :
            pass
    
    return re.compile('({})'.format("|".join(lregex)))

def rec_fol_listing(path) :
    files=os.scandir(path)
    for filename in files:
        if os.path.isdir(filename):
            rec_fol_listing(filename)
        elif filename.is_file() and (filename.path.split(".")[-1] in ACCEPTED_EXT or "." not in filename.path.split("\\")[-1]) :
            retrieved_lines=[]
            print(f"Analyzing {filename.path}. . .")
            f = open(filename.path, 'r', encoding='utf-8', errors='ignore')
            lines = f.readlines()
            for line, nline in zip(lines, range(1, len(lines)+1)) :
                result=request.search(line)
                if result :
                    print(f"Matched line : {line}")
                    csv_result=f"{filename.path},{nline},{result.group(0)},{line}"
                    retrieved_lines.append(csv_result)
            if len(retrieved_lines) > 0 :
                fresult.write("\n".join(retrieved_lines))
                fresult.flush()
            fresult.write("TEST")
            
            f.close()
        else :
            print(f"Extension of {filename.path} is not handled.")

if __name__ == "__main__" :

    if  args["string"] :
        request = reg_name(args["string"][0])
    elif  args["phone"] :
        request = reg_phone(args["phone"][0])
    else :
        parser.print_help()#parser.print_help(sys.stderr)
        sys.exit("None request has been submitted.")
    print(request)
    os.chdir(r"{}".format(str(PWD)))
    cT = datetime.datetime.now()
    time_doc=f"{str(cT.year)}-{str(cT.month)}-{str(cT.day)}_{str(cT.hour)}-{str(cT.minute)}-{str(cT.second)}"

    if not os.path.exists(RESULT_FOLDER) :
        os.makedirs(RESULT_FOLDER, exist_ok=False)
    directory = '.'
    fname=f"{RESULT_FOLDER}/results_{time_doc}.txt"
    fresult = open(f"{fname}", "w")

    rec_fol_listing(directory)

    fresult.close()
    