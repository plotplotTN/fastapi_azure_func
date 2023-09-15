
import os 
from utils.htm_to_json.traducter2 import traducter2

if __name__ == "__main__":
    for subdir, dirs, files in os.walk('C:/Users/Imène BETOUCHE/Downloads/bordereaux_csv'):
        if 'toprint.htm' in files:
            # Charger le contenu HTML dans BeautifulSoup
            with open(os.path.join(subdir,"toprint.htm"), "r", encoding="iso-8859-1") as file:
                result = traducter2(file=file)
                print(result)
                
    pass