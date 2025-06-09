import os
import pandas as pd
from rapidfuzz import process, fuzz  # Use rapidfuzz for similarity matching
from datetime import datetime

csv_filename = "budget4.csv"  # Replace with the actual filename
csv_filepath = os.path.join(os.getcwd(), csv_filename)
output_file = "budget4 with IDs8.csv"

SIMILARITY_THRESHOLD_STRING = 50  # Minimum similarity percentage for the string
SIMILARITY_THRESHOLD_CODE = 80  # Minimum similarity percentage for the code
HIGH_SIMILARITY_THRESHOLD_STRING = 70  # Higher similarity threshold for the string
#the ones that need to remain exact: Baumaßnahmen
MATCH_EXACT = ["Entgelte für Arbeitskräfte mit befristeten Verträgen, sonstige Beschäftigungsentgelte (auch für Auszubildende) sowie Aufwendungen für", 
               "Entgelte der Arbeitnehmerinnen und Arbeitnehmer",
               "Vermischte Einnahmen",
               "Aus- und Fortbildung",  
               "Dienstreisen",
               "Vermischte Verwaltungsausgaben",
               "Erwerb von Geräten, Ausstattungs- und Ausrüstungsgegenständen für Verwaltungszwecke (ohne IT)",
               "Bewirtschaftung der Grundstücke, Gebäude und Räume",
               "Mieten und Pachten",
               "Baumaßnahmen von mehr als 1 000 000 € im Einzelfall", 
               "Baumaßnahmen von mehr als 2 000 000 € im Einzelfall", 
               "Baumaßnahmen von mehr als 6 000 000 € im Einzelfall",
               "Außergewöhnlicher Aufwand aus dienstlicher Veranlassung in besonderen Fällen",
               "Trennungsgeld, Fahrtkostenzuschüsse sowie Umzugskostenvergütungen",
               "Konferenzen, Tagungen, Messen und Ausstellungen",
               "Einnahmen aus Sponsoring, Spenden und Ähnlichen freiwilligen Geldleistungen",
               "Beteiligung an den Versorgungslasten des Bundes",
               "Öffentlichkeitsarbeit",
               "Ausgaben für Vorhaben, die aus Spenden, Sponsoring und ähnlichen freiwilligen Geldleistungen finanziert werden", 
               "Versorgungsbezüge",
               "Zuführung an die Versorgungsrücklage",
               "Erwerb von Anlagen, Geräten, Ausstattungs- und Ausrüstungsgegenständen sowie Software im Bereich Informationstechnik", 
               "Verrechnungsausgaben gemäß § 61 BHO außerhalb der Tit. 981.1 und 981.7",
               "Verrechnungseinnahmen gemäß § 61 BHO außerhalb der Tit. 381.1 und 381.7",
               "Nicht aufteilbare sächliche Verwaltungsausgaben",
               "Erwerb von Fahrzeugen",
               "Zuweisungen an den Versorgungsfonds",
               "Verbrauchsmittel, Haltung von Fahrzeugen und dgl.",
               "Kleine Neu-, Um- und Erweiterungsbauten",
               "Mieten und Pachten im Zusammenhang mit dem Einheitlichen Liegenschaftsmanagement",
               "Unterhaltung der Grundstücke und baulichen Anlagen",
               "Geschäftsbedarf und Kommunikation sowie Geräte, Ausstattungs- und Ausrüstungsgegenstände, sonstige Gebrauchsgegenstände, Software,",
               "Aufträge und Dienstleistungen im Bereich Informationstechnik",
               "Erlöse aus der Veräußerung von beweglichen Sachen",
               "Gebühren, sonstige Entgelte",
               "Bezüge und Nebenleistungen der beamteten Hilfskräfte",
               "Gerichts- und ähnliche Kosten",
               "Forschung, Untersuchungen und Ähnliches",
               "Geschäftsbedarf und Datenübertragung sowie Geräte, Ausstattungs- und Ausrüstungsgegenstände, Software, Wartung",
               "Einnahmen aus Vermietung, Verpachtung und Nutzung",
               "Vermischte Personalausgaben",
               "Sachverständige",
               "Miete für Datenverarbeitungsanlagen, Geräte, Ausstattungs- und Ausrüstungsgegenstände, Maschinen, Software",
               "Beihilfen aufgrund der Beihilfevorschriften",
               "Leistungen von Bundesbehörden zur Durchführung von Aufträgen",
               "Geschäftsbedarf und Kommunikation sowie Geräte, Ausstattungs- und Ausrüstungsgegenstände, sonstige Gebrauchsgegenstände",
               "Behördenspezifische fachbezogene Verwaltungsausgaben (ohne IT)",
               "Veröffentlichung und Dokumentation",
               "Fürsorgeleistungen und Unterstützungen einschließlich Inanspruchnah- me von besonderen Fachdiensten/-kräften",
               "Fürsorgeleistungen einschließlich Inanspruchnahme von besonderen Fachdiensten/-kräften",
               "Öffentlichkeitsarbeit",
               "Sachverständige, Ausgaben für Mitglieder von Fachbeiräten und ähnlichen Ausschüssen",
               "Leistungen an Bundesbehörden zur Durchführung von Aufträgen",
               "Einnahmen aus Veröffentlichungen",
               "Einnahmen aus Prämienzahlungen der Bundesanstalt für Immobilienaufgaben",
               "Geldstrafen, Geldbußen und Gerichtskosten",
               "Ausgaben für Mitglieder von Fachbeiräten und ähnlichen Ausschüssen",
               "Erwerb von Geräten, Ausstattungs- und Ausrüstungsgegenständen",
               "Bezüge der Anwärterinnen und Anwärter sowie Nebenleistungen der Be- amtinnen und Beamten auf Widerruf im Vorbereitungsdienst",
               "Zahlungsverpflichtungen aus Verstößen gegen EU-Recht",
               "Ausgaben für Aufträge und Dienstleistungen",
               "Ausgaben für Vorhaben, die aus Spenden, Sponsoring und ähnlichen freiwilligen Geldleistungen finanziert werden",
               "Außergewöhnlicher Aufwand aus dienstlicher Veranlassung in besonderen Fällen",
               "Erwerb von Datenverarbeitungsanlagen, Geräten, Ausstattungs- und Ausrüstungsgegenständen, Software",
               "Reisen in Angelegenheiten der Personalvertretungen und der Gleichstellungsbeauftragten sowie in Vertretung der Interessen schwerbehinderter",
               "Sonstige Dienstleistungsaufträge an Dritte",
               "Veröffentlichungen und Fachinformationen",
               "Inanspruchnahme überbetrieblicher betriebsärztlicher und sicherheitstechnischer Dienste, von Betriebsärztinnen und Betriebsärzten",
               "Mitgliedsbeiträge und sonstige Zuschüsse an Verbände, Vereine und ähnliche Institutionen geringeren Umfangs",
               "Förderung des Vorschlagwesens",
               "Entgelte für Wissenschaftlerinnen und Wissenschaftler",
               "Leistungen an Bundesbehörden zur Durchführung von ressortübergreifenden Aufgaben",
               "Unfallversicherung Bund und Bahn",
               "Leistungen von Bundesbehörden zur Durchführung von ressortübergreifenden Aufgaben",
               "Zweckgebundene Zuweisungen an die Länder für Mitgliedseinrichtungen der Wissenschaftsgemeinschaft Gottfried Wilhelm Leibniz e. V. (WGL)",
               "Erstattungen des Bundes für Versorgungslasten",
               "Unfallkasse des Bundes",
               "Zuschüsse für Investitionen",
               "Mitgliedsbeiträge und sonstige Zuschüsse für laufende Zwecke im Ausland geringeren Umfangs",
               "Fürsorgeleistungen und Unterstützungen",
               "Erwerb von Geräten, Ausstattungs- und Ausrüstungsgegenständen für Verwaltungszwecke",
               "Einnahmen aus Zuschüssen von der EU",
               "Beiträge an internationale Organisationen",
               "Erstattung von Verwaltungsausgaben",
               "Nicht aufteilbare Personalausgaben",
               "Studienbeihilfen für Nachwuchskräfte geringeren Umfangs",
               "Erstattung von Verwaltungsausgaben aus dem Inland",
               "Mitgliedsbeiträge und sonstige Zuschüsse für laufende Zwecke im Inland geringeren Umfangs",
               "Abfindungen und Erstattungen des Bundes für Versorgungslasten",
               "Darlehen",
               "Zinseinnahmen von Ländern",
               "Zuschüsse zur Deckung laufender Aufwendungen",
               "Einnahmen aus Zuschüssen der Europäischen Union",
               "Erschließungsbeiträge",
               "Internationale Zusammenarbeit",
               "Tilgungsbeträge von Ländern",
               "Abgeltung von Ansprüchen nach dem Urheberrecht",
               "Erwerb von Geräten, Ausstattungs- und Ausrüstungsgegenständen für Neu- und Erweiterungsbauten",
               "Förderung von Investitionen in nationale Projekte des Städtebaus",
               "Sonstige Erstattungen aus dem Inland",
               "Wissenschaftliche Sammlungen und Bibliotheken",
               "Betrieb",
               "Investitionen",
               "Kriegsopferfürsorge"]

                   
def assign_unique_ids_for_first_year(df, unique_id):
    """
    Adds all items for the first year in the dataset to value_to_id_map and assigns each item a unique ID.
    """
    #find the first year
    first_year = df["year"].min()

    # Filter rows for the first year
    first_year_items = df[df["year"] == first_year].copy()
    
    # Assign unique IDs and add to value_to_id_map
    for index, row in first_year_items.iterrows():
        unique_id += 1
        df.at[index, "id"] = unique_id
    
    return df, unique_id

##execute code##
start_time = datetime.now()
print("Start time:", start_time.strftime("%Y-%m-%d %H:%M"))

try:
    # Read the CSV file
    df = pd.read_csv(csv_filepath, sep=";", encoding = "utf-8")  # Adjust encoding/sep if needed

    #assign an ID column
    df["id"] = None

    #assign start number for IDs
    unique_id = 0

    #assign unique IDs to the first year in the file
    df, unique_id = assign_unique_ids_for_first_year(df, unique_id)

    #to del
    print("Unique ID count: ", unique_id)

    # Sort the DataFrame by year, ep, kapitel, and code in ascending order
    df = df.sort_values(by=["year", "ep", "kapitel", "code"], ascending=[True, True, True, True])

    # Get the list of unique years in the dataset
    years = sorted(df["year"].unique())
    
    # Initialize a dictionary to track used IDs for each year
    used_ids_by_year = {year: set() for year in years}

    # Loop through each year starting from the second year
    for i in range(1, len(years)):
        current_year = years[i]
        print(f"🔄 Processing year {current_year}...")

        # Filter rows for the current year
        current_year_items = df[df["year"] == current_year]

        # Precompute previous_year_items
        previous_year_items = pd.concat(
            [df[df["year"] == years[j]].copy() for j in range(i - 1, -1, -1)],
            ignore_index=True
        )
        previous_year_items["normalized_code"] = previous_year_items["code"].str.replace("F ", "")

        #1: check for the perfect match in all prior years
        for index, row in current_year_items.iterrows():
            #to ensure items still get the same ID, whether spending has been "flexibilisiert" or not.
            current_code = row["code"].replace("F ", "")
            exact_match = (
                (previous_year_items["ep"] == row["ep"]) &
                (previous_year_items["kapitel"] == row["kapitel"]) &
                (previous_year_items["normalized_code"] == current_code) &
                (previous_year_items["zweckbestimmung"] == row["zweckbestimmung"])
            )

            if exact_match.any():
                matching_row = previous_year_items[exact_match].iloc[0]
                if matching_row["id"] not in used_ids_by_year[current_year]:
                    df.at[index, "id"] = matching_row["id"]
                    used_ids_by_year[current_year].add(matching_row["id"])
                  
        # 2-6: Process remaining items that do not have an ID assigned
        for index, row in current_year_items.iterrows():
            # Skip items that already have an ID assigned
            if pd.notna(df.at[index, "id"]):
                continue

            current_code = row["code"].replace("F ", "")
            match_found = False
                
            #2: Check for items from 2016 with kapitel reshuffling from 1 to 12
            if row["year"] == 2016 and row["kapitel"] == 12:
                # Filter previous_year_items to only include rows with the same ep and kapitel == 1
                filtered_previous_year_items = previous_year_items[
                    (previous_year_items["ep"] == row["ep"]) &
                    (previous_year_items["kapitel"] == 1)
                ]

                # Iterate through the filtered rows
                for _, prev_row in filtered_previous_year_items.iterrows():
                    previous_code = prev_row["normalized_code"]
                    if (
                        row["ep"] == prev_row["ep"] and
                        1 == prev_row["kapitel"] and
                        current_code == previous_code and
                        row["zweckbestimmung"] == prev_row["zweckbestimmung"]
                    ):
                        if prev_row["id"] not in used_ids_by_year[current_year]:
                            df.at[index, "id"] = prev_row["id"]
                            used_ids_by_year[current_year].add(prev_row["id"])
                            match_found = True
                            break
                    
                # If there is a match, skip the code below and go to the next item
                if match_found:
                    continue

            #3: for items whose codes have to match exactly
            if row["zweckbestimmung"] in MATCH_EXACT: 
                previous_year_items["combined_code"] = (
                    previous_year_items["ep"].astype(str) + "-" +
                    previous_year_items["kapitel"].astype(str) + "-" +
                    previous_year_items["normalized_code"]
                )
                current_combined = f"{row['ep']}-{row['kapitel']}-{current_code}"

                # Compute similarity for combined codes
                previous_year_items["combined_similarity"] = previous_year_items["combined_code"].apply(
                    lambda x: fuzz.ratio(current_combined, x)
                )
                # Filter for high similarity in combined codes
                high_similarity_match = previous_year_items[
                    previous_year_items["combined_similarity"] >= SIMILARITY_THRESHOLD_CODE
                ]
                if not high_similarity_match.empty:
                    # Iterate through the filtered rows to check for an exact match in zweckbestimmung
                    for _, prev_row in high_similarity_match.iterrows():
                        if row["zweckbestimmung"] == prev_row["zweckbestimmung"]:  # Exact match for zweckbestimmung
                            if prev_row["id"] not in used_ids_by_year[current_year]:
                                df.at[index, "id"] = prev_row["id"]
                                used_ids_by_year[current_year].add(prev_row["id"])
                                match_found = True
                                break

                    if match_found == True:
                        continue
                    else:        
                        unique_id+=1
                        df.at[index, "id"] = unique_id
                        used_ids_by_year[current_year].add(unique_id)
                        continue     
                else:        
                    unique_id+=1
                    df.at[index, "id"] = unique_id
                    used_ids_by_year[current_year].add(unique_id)
                    continue                  
                                                                      
            #4: check whether it is a code that matches exactly and a string that matches roughly
            previous_year_items["zweck_similarity"] = previous_year_items["zweckbestimmung"].apply(
                lambda x: fuzz.ratio(row["zweckbestimmung"], x)
            )
            fuzzy_match = (
                (previous_year_items["ep"] == row["ep"]) &
                (previous_year_items["kapitel"] == row["kapitel"]) &
                (previous_year_items["normalized_code"] == current_code) &
                (previous_year_items["zweck_similarity"] >= SIMILARITY_THRESHOLD_STRING)
            )

            if fuzzy_match.any():
                matching_row = previous_year_items[fuzzy_match].iloc[0]
                if matching_row["id"] not in used_ids_by_year[current_year]:
                    df.at[index, "id"] = matching_row["id"]
                    used_ids_by_year[current_year].add(matching_row["id"])
                    continue

            #5: check wether it is a code that matches except for two digits (changed plan, chapter or title) and a string that matches very closely
            previous_year_items["combined_code"] = (
                previous_year_items["ep"].astype(str) + "-" +
                previous_year_items["kapitel"].astype(str) + "-" +
                previous_year_items["normalized_code"]
            )
            current_combined = f"{row['ep']}-{row['kapitel']}-{current_code}"

            # Compute similarity for combined codes
            previous_year_items["combined_similarity"] = previous_year_items["combined_code"].apply(
                lambda x: fuzz.ratio(current_combined, x)
            )

            # Filter for high similarity in combined codes
            high_similarity_match = previous_year_items[
                previous_year_items["combined_similarity"] >= SIMILARITY_THRESHOLD_CODE
            ]

            if not high_similarity_match.empty:
                # Iterate through the filtered rows to check for high similarity in zweckbestimmung
                for _, prev_row in high_similarity_match.iterrows():
                    result_string = process.extractOne(row["zweckbestimmung"], [prev_row["zweckbestimmung"]], scorer=fuzz.ratio)
                    if result_string and result_string[1] >= HIGH_SIMILARITY_THRESHOLD_STRING:
                        if prev_row["id"] not in used_ids_by_year[current_year]:
                            df.at[index, "id"] = prev_row["id"]
                            used_ids_by_year[current_year].add(prev_row["id"])
                            match_found = True
                            break

                if match_found:
                    continue
                
            #6: if nothing yielded a match, add a new id
            unique_id+=1
            df.at[index, "id"] = unique_id
            used_ids_by_year[current_year].add(unique_id)

except Exception as e:
    print(f"❌ Failed to process {csv_filename}: {e}")

try:
    # Prepare the output data
    output_data = df[["id", "year", "ep", "kapitel", "code", "zweckbestimmung", "soll_value"]]

    # Save the result to a CSV file
    output_filepath = os.path.join(os.getcwd(), output_file)
    output_data.to_csv(output_filepath, index=False, sep=";")

    print(f"✅ Processed data saved to: {output_filepath}")
    print(f"🔢 Total number of unique IDs: {df['id'].nunique()}")
except Exception as e:
    print(f"❌ Failed to save the CSV file: {e}")

# Calculate and print the elapsed time
end_time = datetime.now()
print("Finished in:", end_time - start_time)