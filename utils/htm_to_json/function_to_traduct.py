import re
from datetime import datetime

def mapping_period(value):

    if re.search(r"^(Fév\.|Mars |Avr\.|Mai |Juin |Jul\.|Août |Sep\.|Oct\.|Nov\.|Déc\.)@", value):
        return "mois_an" 
    
    elif re.search(r"^Jan\. à @", value) :
        return "cumul_an"
    
    elif re.search(r"à", value) :
        return "cumul_12_mois_an"
    
    elif re.search(r"Ann\.", value):
        return "an_moins_1"
    # Périodes trimestrielles
    elif re.search(r"^[1|2|3|4] Trim\.", value):
        trimester_mapping = {
            "1 Trim.": "trimestre1",
            "2 Trim.": "trimestre2",
            "3 Trim.": "trimestre3",
            "4 Trim.": "trimestre4"
        }
        return trimester_mapping[re.search(r"^[1|2|3|4] Trim\.", value).group()]
    
    # Périodes semestrielles
    elif re.search(r"^[1|2] Sems\.", value):
        semester_mapping = {
            "1 Sems.": "semestre1",
            "2 Sems.": "semestre2"
        }
        return semester_mapping[re.search(r"^[1|2] Sems\.", value).group()]
    
    elif re.search(r"^Jan\.@", value):
        return "moisX12_an"
    
    else:
        return None


def are_consecutives_values(lst, val1="Jan.@", val2="Fév.@") :
    verif = False
    liste_index = []
    for i in range(len(lst) - 1):
        if val1 in lst[i] and val2 in lst[i+1]:
            verif = True
            liste_index.append(i)
    if verif:
        return True, liste_index
    else :
        return False, None


def fonction_date_arrete (date, periode_cat) :
    if periode_cat == "def" :
        date = datetime.strptime(date, '%Y-%m-%d')
        if date.month == 1 :
            return datetime(date.year - 1, 12, 1).strftime('%Y-%m-%d')
        else :
            return datetime(date.year, date.month - 1, 1).strftime('%Y-%m-%d')
    else :
        return date


def format_element(element):
    return element + ' ' * (5 - len(element))


def decompo_element(element) :
    if element.endswith("FR"):
        return "FRANCE"
    elif element.endswith("OM"):
        return "DOM"


def clean_string(s):
    # Remplace les sauts de ligne et les espaces consécutifs par un seul espace
    s = re.sub(r'\n+', ' ', s)
    return re.sub(r'\s+', ' ', s).strip()


def html_to_dict(soup):

    # The outer table contains rows that represent each variable.
    outer_table_rows = soup.select('table > tbody > tr')
    
    result = {}
    
    for row in outer_table_rows[1:]:

        is_colspan_here = False

        # Get all td elements in the current row
        tds = row.find_all('td')

        for td in tds:
            if td.has_attr('colspan') and td['colspan'] == "2":
                is_colspan_here = True
        # Extract the variable name, which is the content of the first <td> in each row.
        variable_name = row.td.text.strip()
        
        # The details for each variable are in a sub-table. We extract the rows of this sub-table.
        inner_table_rows = row.select('table > tbody > tr')
        
        details = []
        if is_colspan_here :
            for inner_row in inner_table_rows :
                libelle = inner_row.select_one('td:nth-of-type(1)').text.strip()
                valeur = inner_row.select_one('td:nth-of-type(2)').text.strip()
                
                # Split the "valeur" on "ET" to handle multiple conditions.
                # Clean up the string to remove unwanted characters like "\n" and then split them.
                conditions = [clean_string(cond) for cond in valeur.split(" ET ")]
                
                details.append({
                    'libelle': libelle,
                    'valeur': conditions
                })
            
            result[variable_name] = details
        
    return result


def consecutive_months_count(months_list):
    # Dictionnaire pour convertir le nom du mois en numéro
    month_to_num = {
        'Jan.': 1, 'Fév.': 2, 'Mars': 3, 'Avr.': 4,
        'Mai': 5, 'Juin': 6, 'Jul.': 7, 'Août': 8,
        'Sep.': 9, 'Oct.': 10, 'Nov.': 11, 'Déc.': 12
    }
    
    # Extraire les mois et les années
    months_and_years = []
    for item in months_list:
        match = re.search(r"(\w+\.?)\s?@\s?(\d{4})", item)
        if match:
            month = month_to_num.get(match.group(1), 0)
            year = int(match.group(2))
            months_and_years.append((month, year))
    
    # Compter les mois consécutifs pour la même année
    max_count = 0
    count = 1
    for i in range(1, len(months_and_years)):
        if months_and_years[i][1] == months_and_years[i-1][1] and months_and_years[i][0] == months_and_years[i-1][0] + 1:
            count += 1
            max_count = max(max_count, count)
        else:
            break

    return max_count

#Permet de faire correspondre le nom de la colonne dans le bordereau avec le nom de la colonne dans la table snowflake
mapping_bordereau_to_table_snowflake = {
    "DEPART": "CODE_DEPARTEMENT",
}