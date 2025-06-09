README

1) Use extract_from_haushalt-pdf.py to get the data from pdfs; at the beginning of the script, there are a couple of inputs that need to be specified like the file where the budget docs can be found and the output. you can also limit the number of pages the code processes within a budget doc if you want to test sth. the current max, 4000 pages, will cover an entire budget doc.

2) !!! Replace "1 ." with "1." in the column "Zweckbestimmung". This is the one manual adjustment happening in the budget spreadsheet.

3) Use that csv and create_id_map.py to generate unique ids and add them to the budget item. This produces a new output file. The script currently considers a title to be the same if "einzelplan", "kapitel" and "code" are an exact match and "zweckbestimmung" is a 70% match. This can be adjusted through adjusting the "similiarity_threshold" variable.

4) Recommended: Run a manual check on IDs. Check for lots of disappearing and new IDs, check for whether an ID is double booked for a year, esp on admin costs. A neat way to run this check is to put IDs in rows, years in columns and check for which years an ID has a value. Sort by "ep" for the best overview. 

5) Import the resulting budget data into the KPIsheet. Do so via an Abfrage so that updates in the csv file, for instance with ID corrections, can be reflected in the data in KPIsheet.xlsx.

6) If you need to add additional items, you can use add_ids_to_new_items.py and then join them with the existing date using joining_csv_files.py
Wichtig:


+++Notes+++
- ep32 in 2016 und 2017 werden nicht eingelesen, der pdf-reader erkennt die titelcodes nicht richtig.
- items in ep14 for 2016 and 2017 where missing and have been added semi-manually. if sth seems off, check the corresponding csv file for the added items

+Geänderte IDs+
- Bürgergeld
- DATI (ehemals Hightechstrategie)
- Innovative Softwaresysteme; künstliche Intelligenz (ep 30, kap 4)
- Entwicklung digitaler Technologien (ep 9, kap 1)
- Forschungs- und Entwicklungsvorhaben: Erneuerbare Energien
- Innovative und digitalisierte Materialforschung (ep 30, kap 4, Titel 683 26-165)
- Querschnittsaufgabe Energieeffizienz
- Maßnahmen im Rahmen der Freizeitbetreuung 10036

