import datetime, os, os.path, re
os.chdir(os.path.dirname(r"{}".format(str(os.path.abspath(__file__)))))

RESULT_FOLDER="result_parsing"
BANNED_EXT=["py", "gz"]
"""
Observed success flag : failure, fail, failed, success, valid, invalid, pass


Observed dates :
    
    Sep 25 12:12:15
    2020-11-03T13:22:10.55297073Z
    2020-09-25 12:12:12,062
    Tue, 03 Nov 2020 13:23:35 GMT
    2020-12-03 21:00:49 205902
    04 Nov 2020 09:52:18.026
    25/Feb/2021:21:23:01 +1100

Regexes dates :  


    19040211T23:12:43 |02111904T23:12:43 | 2-29-1904T23:12:43 PM GMT| 01/31/1905 | 2-29-1904 23:12:43 PM | 2021-04-31 23:12:43 PM | 2.291.1904 23:12:43 GMT| 1/9/1900 23:34 | 2/29/1904 23:12:43.564543254
    Sep 25 12:12:15 | Tue, 03 Nov 2020 13:23:35 GMT //
    25/Feb/2021:21:23:01 +1100 //


Attempts Regex :

^(?:.*?)?((?:[0-3]?[0-9] )?(?i:(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)) (?:20[0-9]{2} )?(?:[0-3]?[0-9] )?[0-9]{2}:[0-9]{2}:[0-9]{2})


"""

MONTHS="Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec"


DATES_REGEX_LIST= [\
    "^(?:.*?)?((?:[0-3]?[0-9] )?(?i:(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)) (?:20[0-9]{2} )?(?:[0-3]?[0-9] )?[0-9]{2}:[0-9]{2}:[0-9]{2})",
    "(?P<date>(?:(?P<day>3[01]|[12][0-9]|0?[1-9])[\/\.\-](?P<month>1[0-2]|0?[1-9]|(?i:(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)))|(?P<month2>1[0-2]|0?[1-9])[\/\.\-](?P<day2>3[01]|[12][0-9]|0?[1-9]))[\/\.\-](?P<year>[12][90][0-9]{2}|[1-9][0-9])|(?P<year3>[12][90][0-9]{2}|[1-9][0-9])[\/\.\-](?P<month3>0?[1-9]|1[0-2])[\/\.\-](?P<day3>3[01]|[12][0-9]|0?[1-9])|(?P<year4>[12][90][0-9]{2}|[1-9][0-9])(?P<month4>1[0-2]|0[1-9])(?P<day4>3[01]|[12][0-9]|0[1-9])|(?P<day5>3[01]|[12][0-9]|0[1-9])(?P<month5>1[0-2]|0[1-9])(?P<year5>[12][90][0-9]{2}|[1-9][0-9]))(?P<time>[ :T]?(?P<hour>[0-1]?[0-9]|2[0-3]):(?P<minutes>[0-5]?[0-9])(?::(?P<seconds>[0-5]?[0-9](?:\.\d+)?))?(?: ?(?P<meridiem>[aA][mM]|[pP][mM]))?(?: ?(?P<timezone>(?i:gmt|utc)))?(?: ?(?P<offset>[\-\+](?:1[0-9]|0?[1-9]|[0-1][0-9]{3})))?)?",\
    "^(?:.*?)?((?:[0-3]?[0-9] )?(?i:(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)) (?:20[0-9]{2} )?(?:[0-3]?[0-9] )?[0-9]{2}:[0-9]{2}:[0-9]{2})",
    ]
DATES_RE_COMPILED=[re.compile(_) for _ in DATES_REGEX_LIST]
print("|".join(DATES_REGEX_LIST).replace("^",""))
DATES_REGEX=re.compile("("+")|(".join(DATES_REGEX_LIST).replace("^","")+")")
IP_REGEX=re.compile("((?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?))")

SUCCESS=re.compile("(?=.* (?i:(failure|fail|failed|success|valid|invalid|pass)) .*$)")

def find_ip(line) :
    result=IP_REGEX.search(line)
    if result :
        return result.group(1)
    else :
        return False

def find_date(line) :
    result=DATES_REGEX.search(line)
    if result :
        return result.group(1)
    else :
        return ""

def find_success(line) :
    result=SUCCESS.search(line)
    if result :
        return result.group(1)
    else :
        return ""

def find_hostname(line) :
    return ""



def lparse(lpath) :
    os.chdir(r"{}".format(str(lpath)))
    cT = datetime.datetime.now()
    time_doc=f"{str(cT.year)}-{str(cT.month)}-{str(cT.day)}_{str(cT.hour)}-{str(cT.minute)}-{str(cT.second)}"

    if not os.path.exists(RESULT_FOLDER) :
        os.makedirs(RESULT_FOLDER, exist_ok=False)
    directory = '.'
    csv_filename=f"{RESULT_FOLDER}/parsed_csv_{time_doc}.csv"
    csv = open(f"{RESULT_FOLDER}/parsed_csv_{time_doc}.csv", "w")
    files=os.scandir(directory)
    for filename in files:
        retrieved_lines=[]
        if filename.is_file() and filename.path.split(".")[-1] not in BANNED_EXT :
            print(f"Analyzing {filename.path}. . .")
            f = open(filename.path, 'r', encoding='utf-8', errors='ignore')
            lines = f.readlines()
            for line, nline in zip(lines, range(1, len(lines)+1)) :
                current_f="";ip="";line_number="";date="";success="";hostname=""
                ip = find_ip(line)
                if ip :
                    current_f=filename
                    line_number=nline
                    date = find_date(line)
                    #origin=verify_ip_origin(ip)
                    #hostname=find_hostname(line)
                    success=find_success(line)
                    csv_line=f"{current_f.path};{line_number};{date};{ip};{hostname};{success}"
                    retrieved_lines.append(csv_line)
 
                else :
                    continue
            csv.write("\n".join(retrieved_lines))
            csv.write("TEST")
            f.close()
        else :
            print(f"{filename.path} is not a file.")


    csv.close()

    return f"{lpath}/{csv_filename}"
    

