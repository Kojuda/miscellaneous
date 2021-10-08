from program.general_import import Importation
import phonenumbers
import logging, copy

class Custom_Importation(Importation) :

    __db=super().getDB()

    def __init__(self):
        super().__init__()

    def extract(self, filename) :
        """Overriding function to parse specific leak file."""

        if (filename.path.split(".")[-1] in self.ACCEPTED_EXT or "." not in filename.path.split("\\")[-1]) :
            #TODO: verify if the file has already been imported inside the collection used for that
            retrieved_documents=[]
            print(f"Analyzing {filename.path}. . .")
            f = open(filename.path, 'r', encoding='utf-8', errors='ignore')
            lines = f.readlines()
            for line, nline in zip(lines, range(1, len(lines)+1)) :

                #Insert the line inside the raw collection and retrieve the raw_id
                raw_id=self.db.raw.insert({"data" : line})
                #Create empty doc to fill. 
                doc = copy.deepcopy(self.base_leak_doc)
                doc["filename"] = filename.path
                line=line.split(":"); doc["linenumber"] = nline
                try :
                    parsed_number=phonenumbers.parse(line[0], None)
                    if phonenumbers.is_possible_number(parsed_number) :
                        int_number=phonenumbers.format_number(line[0], phonenumbers.PhoneNumberFormat.INTERNATIONAL); doc["phonenumber"]["raw"] = int_number
                        zone_phone=phonenumbers.geocoder.description_for_number(parsed_number, "en"); doc["phonenumber"]["zone_phone"] = zone_phone
                        carrier=carrier.name_for_number(parsed_number, "en"); doc["phonenumber"]["carrier"] = carrier
                    else :
                        logging.info(f"Not a phone number : {line[0]}")
                        
                    
                except phonenumbers.phonenumberutil.NumberParseException as e:
                    logging.error(f"Can't parse supposed phone number : {line[0]}")
                
                doc["first_name"] = line[2]
                doc["last_name"] = line[3]
                doc["gender"] = line[4]
                doc["gender"] = "Facebook"
                doc["work"] = line[9]
                doc["country_residence"] = line[7]
                doc["raw_id"] = raw_id
                #doc["phonenumber"]["ind"] = 
                
            f.close()
        else :
                print(f"Extension of {filename.path} is not handled.")








def entry_point(script, fleaks) :
    Custom_Importation(script, fleaks)
