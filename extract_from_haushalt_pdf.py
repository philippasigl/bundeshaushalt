import pdfplumber
import pandas as pd
import os
import re
from datetime import datetime
from collections import defaultdict
import unicodedata
import winsound
import sys
from memory_profiler import memory_usage

###INPUTS###
pdf_directory = "./haushaltsplaene_pdfs_test"  # Definiere das Verzeichnis mit den PDFs
filename = "test.csv"  # Definiere den Namen der CSV-Datei // IMPORTANT: settings so that data is ADDED to the existing file, not overwritten
budget_items = [] # Liste für die extrahierten Daten

MAX_PAGES = 10 # Wie viele Seiten maximal durchsucht werden sollen. Zähler beginnt erst am Anfang der Einzelpläne!
###END INPUTS###

SECOND_LINE_CODE_PATTERN = re.compile(r"^-\d{3}") #to check whether an item is a budget item or not
CODE_PATTERN = re.compile(r"^(F \d{3} \d{2}-\d{3})|(\d{3} \d{2}-\d{3})") #to check whether the code in its entirety is valid
YEAR_PATTERN = re.compile(r"\b(20\d{2})\b") #to find the year of the respective budget file
EINZELPLAN_AND_KAPITEL_PATTERN = re.compile(r"\b\d{4}\b") #to find the einzelplan and kapitel for a specific page
END_OF_LINE_PATTERN = re.compile(r"-\s?$") #to remove "-" used at line breaks in the zweckbestimmung

def extract_einzelplan_and_kapitel(sorted_lines):

    if len(sorted_lines) > 1:  #ensure there is at least a second line
        second_line_words = sorted_lines[1][1]  #get the words of the second line
        second_line_text = " ".join(word["text"] for word in second_line_words).strip() #extract the text only

        match = re.search(EINZELPLAN_AND_KAPITEL_PATTERN, second_line_text) #search for a four-digit code in the second line (first two are the ep, second the kapitel)
        if match:
            return match.group(0)[:2], match.group(0)[2:]  #split the four-digit code into einzelplan and kapitel
        
    return None, None #if no match is found


def set_flag_left_or_right_page(sorted_lines):
    start = 0
    end = 0
    if len(sorted_lines) > 1:  # Ensure there is a second line
        second_line_words = sorted_lines[1][1]  # Get the words of the second line
        for word in second_line_words:
            if re.match(EINZELPLAN_AND_KAPITEL_PATTERN, word["text"]):  # Match a four-digit code
                start=word["x0"]
                end=word["x1"]  
    if start < 40:
        return "left"
    if end > 500:
        return "right"
    
    # If no page side is determined, raise an error
    return None


def group_and_sort_lines(words):
    
    lines = defaultdict(list) # Use defaultdict to automatically create lists

    for word in words:
        top = round(word["top"], 0) #round to no decimals, the pdfs are too imprecise to work with decimals
        lines[top].append(word)  # No need to check if top exists, since defaultdict

    return sorted(lines.items())


def find_code(first_line_text, second_line_text):
    
    first_line_code = "" #only take the code from the first line
    count=0

    #find the code by counting the digits (as some codes have a leading "F")
    for letter in first_line_text:
        first_line_code += letter
        if letter.isdigit():
            count+=1
        if count == 5:
            break  # Stop concatenating when "-" is reached

    # Add the code from the second line
    code = first_line_code + second_line_text.strip()[0:4]

    return code

def find_zweckbestimmung(first_line_words, second_line_words, third_line_words, page_side):
    
    #find by the position of the words in the first and second line; sometimes there is a third line, which is not included here
    x0_position = 0
    x1_position = 0

    if page_side == "left":
        x0_position = 65
        x1_position = 358
    else:
        x0_position = 90
        x1_position = 383
    
    zweckbestimmung = ""
    for index, word in enumerate(first_line_words):
        if word["x0"] > x0_position and word["x1"] < x1_position:
            zweckbestimmung += word["text"] + " "

    #remove "-" used at line breaks 
    zweckbestimmung = re.sub(END_OF_LINE_PATTERN, "", zweckbestimmung)

    for index, word in enumerate(second_line_words):
        if word["x0"] > x0_position and word["x1"] < x1_position:
            zweckbestimmung += word["text"] + " "

    #remove "-" used at line breaks 
    zweckbestimmung = re.sub(END_OF_LINE_PATTERN, "", zweckbestimmung)

    if third_line_words is not None:
        for index, word in enumerate(third_line_words):
            if word["x0"] > x0_position and word["x1"] < x1_position:
                zweckbestimmung += word["text"] + " "

    # Normalize text to handle special characters like umlauts
    zweckbestimmung = unicodedata.normalize("NFKC", zweckbestimmung.strip())

    return zweckbestimmung


def save_to_csv(batch, filename):
    df = pd.DataFrame(batch, columns=["year", "ep", "kapitel", "code", "zweckbestimmung", "soll_value"])
    df.to_csv(filename, sep=";", index=False, mode="a", header=not os.path.exists(filename), encoding="utf-8")


def process_budget_items(sorted_lines, year, einzelplan_number, kapitel, page_side):

    x0_position = 0 
    x1_position = 0  
    
    if page_side == "left":
        x0_position = 366
        x1_position = 420
    else:
        x0_position = 390
        x1_position = 440
    
    first_line_words = None
    #index required to find potential third lines of budget items
    i = 0

    for top, second_line_words in sorted_lines:
        
        second_line_text = " ".join(word["text"] for word in second_line_words)

        #if a first line exists and the second line starts with "-ddd", i.e. the lines concerned include a budget item
        if first_line_words is not None and re.match(SECOND_LINE_CODE_PATTERN, second_line_text.strip()[0:4]):
            first_line_text = " ".join(word["text"] for word in first_line_words)
            
            # Check for third_line_words before processing second_line_words; check based on 
            third_line_words = None
            if i + 1 < len(sorted_lines):
                next_top, next_words = sorted_lines[i + 1]
                if int(next_top - top) == 11:
                    third_line_words = next_words

            #find code
            code = find_code(first_line_text, second_line_text)

            #if the code contains a valid format, go find the zweckbestimmung
            if re.match(CODE_PATTERN, code):
                zweckbestimmung = find_zweckbestimmung(first_line_words, second_line_words, third_line_words, page_side)

                # Extract budget value
                budget_value = ""
                for index, word in enumerate(first_line_words):
                    if word["x0"] > x0_position and word["x1"] < x1_position:
                        budget_value += word["text"]
                    else:
                        continue
                    
                # If no budget value is found, assign "-" (sometimes "-" is used, but sometimes there is just a blank space)
                if budget_value == "-":
                    budget_value = "0"
                elif budget_value == "":
                    budget_value = "0"
                else:
                    try:
                        budget_value = budget_value.strip()
                    except ValueError:
                        print(f"Invalid budget value: {year} {einzelplan_number} {kapitel} {code} {budget_value}")
                    
                if all([year, einzelplan_number, kapitel, code, zweckbestimmung, budget_value]):
                    budget_items.append({
                    'year': year,
                    'ep': einzelplan_number,
                    'kapitel': kapitel,
                    'code': code,
                    'zweckbestimmung': zweckbestimmung,
                    'soll_value': int(budget_value)
                })
                else:
                    print(f"Incomplete data for ", year, " ", einzelplan_number, " ", kapitel, " ", code, " ", zweckbestimmung, " ", budget_value)
        
                # Save data in batches
                if len(budget_items) >= 100:
                    save_to_csv(budget_items, filename)
                    budget_items.clear()

        # Update the first line
        first_line_words = second_line_words
        i += 1
        second_line_words = None
        second_line_text = None
        first_line_text = None

    return 


def process_pdf(pdf_file): # Hier deine Verarbeitung der Seite (z.B. Text extrahieren)
    with pdfplumber.open(pdf_file) as pdf:

            # Überprüfe, ob die Datei eine PDF-Datei ist
            if pdf_file.endswith(".pdf"):
                pdf_path = os.path.join(pdf_directory, pdf_file)
                print(f"Verarbeite {pdf_path}")

                # Extract the year from the file name (assuming the year is a 4-digit number in the file name)
                year_match = re.search(YEAR_PATTERN, pdf_file)  # Adjust regex if needed
                year = year_match.group(1) if year_match else "Unknown"

                #find start page of the budget items to accelerate the process
                start_page = 0
                for page_number, page in enumerate(pdf.pages):
                    try:
                        text = page.extract_text()
                        if not text or "0101" not in text:
                            continue
                        else:    
                            start_page = page_number
                            break
                    except Exception as e:
                        print(f"Error reading page {page_number + 1} of {pdf_file}: {e}")
                        continue

                ##only for testing: how many pages to iterate through
                limit_iter_to = MAX_PAGES

                #process each individual page in the file
                for page_number in range(start_page - 1, len(pdf.pages)):
                    try:
                        page = pdf.pages[page_number] #get the page
                        words = page.extract_words() #extract words from the page
                        sorted_lines = group_and_sort_lines(words) #group and sort lines
                        einzelplan_number, kapitel = extract_einzelplan_and_kapitel(sorted_lines) # Extract Einzelplan and Kapitel 

                        page_side = ""
                        # if the page doesn't contain budget items, skip it
                        if einzelplan_number is None or kapitel is None:
                            continue
                        else:
                            #find out if the page is a left or right page so the location of the budget value can be determined 
                            page_side = set_flag_left_or_right_page(sorted_lines)
                            if page_side is None:
                                continue
                            else:
                                process_budget_items(sorted_lines, year, einzelplan_number, kapitel, page_side)

                                ##limiting the number of pages with budget items processed for testing
                                limit_iter_to -= 1
                                if limit_iter_to == 0:
                                    break

                                ##for testing
                                if page_number % 500 == 0:
                                    print("Verarbeite Seite ", page_number, " des Haushalts", year, "Einzelplan ", einzelplan_number, " Kapitel ", kapitel, " Zeit ", datetime.now().strftime("%H:%M"))
                                    print(f"Memory usage is at: {memory_usage()[0]} MB")
            
                    except UnicodeDecodeError as e:
                        print(f"Encoding error on page {page_number + 1} of {pdf_file}: {e}")
                        continue  # Skip the problematic page
                    except Exception as e:
                        print(f"Error processing page {page_number + 1} of {pdf_file}: {e}")
                        continue  # Skip the problematic page
                    finally:
                        page = None
                        words = None
                        sorted_lines = None

            # Trigger garbage collection after processing the PDF
            import gc
            gc.collect()

            return


def process_files(pdf_files):
    
    for pdf_file in pdf_files:
        try:
            process_pdf(pdf_file)
        except Exception as e:
            print(f"Error processing file {pdf_file}: {e}")
            continue

    print("All PDF files have been processed.")


###execute the code###
# Record the start time
start_time = datetime.now()
print("Start time:", start_time.strftime("%Y-%m-%d %H:%M"))

pdf_files = [os.path.join(pdf_directory, f) for f in os.listdir(pdf_directory) if f.endswith(".pdf")]
process_files(pdf_files)

# Final save
if budget_items:
    save_to_csv(budget_items,filename)

print(f"Daten sind in {filename} gespeichert.")

# Calculate and print the elapsed time
end_time = datetime.now()
print("Finished in:", end_time - start_time)

#Makes a noise when done
winsound.Beep(1000, 1000)

