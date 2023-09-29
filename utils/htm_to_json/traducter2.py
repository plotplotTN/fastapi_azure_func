import os
import re
import json
from datetime import datetime
import warnings
from bs4 import BeautifulSoup

from utils.htm_to_json.fonction_to_traduct import *


class Traducter:


    def __init__(self,file) -> None:
        
        soup = BeautifulSoup(file.read(), "lxml")

        for tr in soup.find_all('tr'):
            if 'Demande' in tr.text:
                self.demande = tr.find_next('td').find_next('td').text

        filters_dict = {}
        if soup.find("h2", id="filtre") is not None:
            filters_section = soup.find("h2", id="filtre").find_next_sibling("table")
            rows = filters_section.find_all("tr")[1:]  # Ignorons l'en-tête

            for row in rows:
                tds = row.find_all("td")
                if len(tds) >= 2:  # Au moins deux cellules dans la ligne (Variable et Filtre)
                    key = tds[0].text.strip()

                    inner_filters = tds[1].find("table")
                    if inner_filters:
                        # Récupérez chaque valeur à partir des <TD> de la table imbriquée
                        values = [td.text for td in inner_filters.find_all("td")]
                    else:
                        values = [tds[1].text.strip()]
                    
                    # if any(val.count('\xa0') >= 3 for val in values):
                    #     warnings.simplefilter(action="always")
                    #     warnings.warn(f'Le filtre de la demande {self.demande}doit être finalisé manuellement. \n'
                    #                   "Si le filtre est déjà présent dans regroupement, alors déjà traité et garder uniquement le nom du regroupement. \n"
                    #                   "Sinon, effectuer un filtre avec des 'and' et des 'or' correctement imbriqués.")
                    #     break
                    # else :
                    values = [val.strip() for val in values]

                    # if any(">" in val or "<" in val or "De" in val for val in values):
                    #     warnings.simplefilter(action="always")
                    #     warnings.warn(f'Le filtre de la demande {self.demande} doit être vérifié. \n'
                    #                 "Des opérations mathématiques peuvent être mises au lieu d'opérations sémantiques (et vice versa).")

                    if key in mapping_bordereau_to_table_snowflake:
                        key = mapping_bordereau_to_table_snowflake[key]
                    if key not in filters_dict:
                        filters_dict[key] = []
                    filters_dict[key].extend(values)


        # Extraction des informations
        date_arrete = soup.find_all("td", align="left")[0].text.split()[-1]
        # Conversion de la date
        date_arrete = datetime.strptime(date_arrete, '%d/%m/%Y').strftime('%Y-%m-%d')
        # Pour extraire uniquement l'année
        an_date_arrete = datetime.strptime(date_arrete, '%Y-%m-%d').strftime('%Y')


        # Localisez d'abord la section 'Variables Ligne'
        attributes_section = soup.find("h2", id="ligne").find_next_sibling("table")
        # Ensuite, localisez la 2ème table (la table imbriquée) à l'intérieur
        inner_attributes = attributes_section.find("table")

        # Extraction des attributs et de leur renommage
        attributes = []
        rename = []
        for row in inner_attributes.find_all("tr"):
            if row.td:
                original_name = row.td.text.split(" ")[0]
                if original_name in mapping_bordereau_to_table_snowflake:
                    new_name = mapping_bordereau_to_table_snowflake[original_name]
                    attributes.append(new_name)
                else:
                    attributes.append(original_name)

                if "Renommé en" in row.td.text:
                    renamed = row.td.text.split("Renommé en ")[1].split(")")[0]
                    rename.append(renamed)
                else:
                    rename.append(original_name)
        rename = ["DATE"] + rename + ["DATE_ARRETE", "VOLUME", "JO"]

        # Localisez d'abord la section 'Variables Colonne'
        periodes_section = soup.find("h2", id="colonne").find_next_sibling("table")
        # Ensuite, localisez la 2ème table (la table imbriquée) à l'intérieur
        inner_periodes = periodes_section.find("table")

        periodes = [td.text.strip() for td in inner_periodes.find_all('td') if td.text.strip()]
        truncated = [False for _ in range(len(periodes))]
        periodes_finales = []
        verif_month, liste_index_month = are_consecutives_values(periodes)
        verif_trim, liste_index_trim = are_consecutives_values(periodes, val1="1 Trim.", val2="2 Trim.")
        verif_sem, liste_index_sem = are_consecutives_values(periodes, val1="1 Sems.", val2="2 Sems.")
        
        if verif_month:
            compte = 0
            for i in liste_index_month :
                i = i - compte
                nombre_mois_successifs = consecutive_months_count(periodes[i:])
                del periodes[i+1:i+nombre_mois_successifs]
                del truncated[i+1:i+nombre_mois_successifs]
                if nombre_mois_successifs != 12:
                    truncated[i] = True
                compte += nombre_mois_successifs - 1

        if verif_trim:
            compte = 0
            for i in liste_index_trim :
                i = i - compte
                nombre_trim_successifs = consecutive_trim_count(periodes[i:])
                del periodes[i+1:i+nombre_trim_successifs]
                del truncated[i+1:i+nombre_trim_successifs]
                if nombre_trim_successifs != 4:
                    truncated[i] = True
                compte += nombre_trim_successifs - 1
        
        if verif_sem:
            compte = 0
            for i in liste_index_sem :
                i = i - compte
                nombre_sem_successifs = consecutive_sems_count(periodes[i:])
                del periodes[i+1:i+nombre_sem_successifs]
                del truncated[i+1:i+nombre_sem_successifs]
                if nombre_sem_successifs != 2:
                    truncated[i] = True
                compte += nombre_sem_successifs - 1

        for i, periode in enumerate(periodes):
            if '\x97' in periode :
                periode_cat = 'prov'
            else:
                periode_cat = 'def'
            
            years = re.findall(r"(\d{4})", periode)
            year = years[-1]
            ecart = int(an_date_arrete) - int(year)
            periode_type = mapping_period(periode, periode_cat)
            periodes_finales.append({
                "periode_type": periode_type,
                "periode_cat": periode_cat,
                "ecart": ecart,
                "truncated": truncated[i]
                })

        date_arrete = fonction_date_arrete(date_arrete, periodes_finales[0]["periode_cat"])

        formats = []
        for tr in soup.find_all('tr'):
            if 'type de travail' in tr.text:
                type_de_travail = tr.find_next('td').find_next('td').text
                values_travail = [val.strip() for val in type_de_travail.split('et')]
                values_travail = [format_element(val) for val in values_travail]
                filters_dict['CODE_TYPE_TRAVAIL'] = values_travail
            
            if 'Univers' in tr.text:
                univers = tr.find_next('td').find_next('td').text
                values_uni = [val.strip() for val in univers.split('et')]
                values_uni_final = []
                for val in values_uni:
                    values_uni_final.extend(decompo_element(val))
                filters_dict['NOM_UNIVERS'] = values_uni_final

            if "Réseau" in tr.text:
                reseau = tr.find_next('td').find_next('td').text.strip()
                filters_dict['RAISON_SOCIALE'] = [reseau]
            
            if "Format" in tr.text:
                format_value = tr.find_next('td').find_next('td').text.strip()
                formats.append(format_value)

        format_fichier, format_stat_ou_comm = formats

        filter_final = transformation_filtre(filters_dict)

        regroupement = {}
        if soup.find("h2", id="regroup") is not None:
            regroup_section = soup.find("h2", id="regroup").find_next_sibling("table")
            
            # Récupérer le nom de la variable
            champ_group = regroup_section.find_all("tr")[1].find("td").text.strip()
            
            inner_regroup = regroup_section.find("table")
            group_names = [td.text.strip() for td in inner_regroup.find_all("td", class_="tdright")]

            regroupement[champ_group] = []

            for i, values_table in enumerate(inner_regroup.find_all("table")):
                regroup_values = [td.text.strip() for td in values_table.find_all("td")]
                regroupement[champ_group].append({"nom": group_names[i], "Valeurs": regroup_values})
            regroupement = format_regroupement(regroupement)
        
        renommage = {}
        if soup.find("h2", id="renommage") is not None:
            rename_section = soup.find("h2", id="renommage").find_next_sibling("table")
            
            # Récupérer le nom de la variable
            champ_rename = rename_section.find_all("tr")[1].find("td").text.strip()
            
            inner_rename = rename_section.find("table")
            rename_names = [td.text.strip() for td in inner_rename.find_all("td", class_="tdright")]

            renommage[champ_rename] = []

            for i, values_table in enumerate(inner_rename.find_all("table")):
                rename_values = [td.text.strip() for td in values_table.find_all("td")]
                renommage[champ_rename].append({"nom": rename_names[i], "Valeurs": rename_values})
            renommage = format_regroupement(renommage)

        # amenagement = {}
        # if soup.find("h2", id="amenager") is not None:
        #     amenagement_section = soup.find("h2", id="amenager").find_next_sibling("table")
        #     amenagement = html_to_dict(amenagement_section)

        json_output = {
            "date_arrete": date_arrete,
            "periodes": periodes_finales,
            "attributes": attributes,
            "filters": filter_final,
            "rename": rename,
            "reseau": reseau,
            "format_fichier": format_fichier,
            "format_stat_ou_comm": format_stat_ou_comm,
            "demande": self.demande,
            "regroupement": regroupement,
            "renommage": renommage,
        }

        self.json_output = json_output
        return None

    
