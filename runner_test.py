
import os 
from utils.htm_to_json.traducter2 import Traducter
import json

if __name__ == "__main__":
    for subdir, dirs, files in os.walk('C:/Users/thoma/Downloads/Téléchargement_Polarys/bordereaux_csv'):
        if 'toprint.htm' in files:
            # Charger le contenu HTML dans BeautifulSoup
            with open(os.path.join(subdir,"toprint.htm"), "r", encoding="iso-8859-1") as file:
                result = Traducter(file=file)
            with open(os.path.join(subdir,f"{result.demande}.json"), "w", encoding='utf-8') as outfile:
                json.dump(result.json_output, outfile, ensure_ascii=False, indent=4)
                
    pass
