import os
import re
import json
from datetime import datetime

from bs4 import BeautifulSoup

from utils.htm_to_json.fonction_to_traduct import *


class Traducter:


    def __init__(self,file) -> None:
        
        soup = BeautifulSoup(file.read(), "lxml")
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
                        values = [td.text.strip() for td in inner_filters.find_all("td")]
                    else:
                        values = [tds[1].text.strip()]
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


        # Localisez d'abord la section 'Variables Colonne'
        periodes_section = soup.find("h2", id="colonne").find_next_sibling("table")
        # Ensuite, localisez la 2ème table (la table imbriquée) à l'intérieur
        inner_periodes = periodes_section.find("table")

        periodes = [td.text.strip() for td in inner_periodes.find_all('td') if td.text.strip()]
        periodes_finales = []
        verif, liste_index = are_consecutives_values(periodes)
        compte = 0
        if verif:
            for i in liste_index :
                i = i - compte
                nombre_mois_successifs = consecutive_months_count(periodes[i:])
                del periodes[i+1:i+nombre_mois_successifs]
                compte += nombre_mois_successifs - 1

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
                "ecart": ecart})

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

            if "Demande" in tr.text:
                demande = tr.find_next('td').find_next('td').text

            if "Réseau" in tr.text:
                reseau = tr.find_next('td').find_next('td').text
            
            if "Format" in tr.text:
                format_value = tr.find_next('td').find_next('td').text.strip()
                formats.append(format_value)

        format1, format2 = formats

        filter_final = transformation_filtre(filters_dict)

        regroupement = {}
        if soup.find("h2", id="regroup") is not None:
            regroup_section = soup.find("h2", id="regroup").find_next_sibling("table")
            
            # Récupérer le nom de la variable
            champ_group = regroup_section.find_all("tr")[1].find("td").text.strip()
            
            inner_regroup = regroup_section.find("table")
            # Récupérer le nom de regroupement
            group_name = inner_regroup.find("td", class_="tdright").text.strip()
            
            # Récupérer toutes les valeurs associées
            values_table = inner_regroup.find("table")
            regroup_values = [td.text.strip() for td in values_table.find_all("td")]

            regroupement[champ_group] = {"nom": group_name, "Valeurs": regroup_values}

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
            "format": format1,
            "format2": format2,
            "demande": demande,
            "regroupement": regroupement,
        }

        self.json_output = json_output
        return None

    
