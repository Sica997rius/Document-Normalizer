#  Document normalizer
   **REPOSITORY GIT HUB:**
   No requirement for run 

**Warning:** this program renames and overwrites your original files. 'session.json. does not store the original text, so make a backup first.


    Document-Normalizer normalizes title end text of the documents in a folder and saves each session in a history that you can search. 
    
##  Usage

    1. The program asks whether you want normalize a folder or search in 'session.json' a document by keywords. 
    2. If you choose to normalize, the program scans the folder and its subfolders, and classifizes allowed and disallowed files:
        - Allowed files: .txt, .md, .csv
        - disallowed files: any others
    3. the program asks whether you want to apply the changes:
        - if  you answer no, program skips normalization and opens the search.
        - if answer yes, the program runs three normalization loops (.txt .md .csv), saves the processed documents in 'session.json', and opens the search.
##  Search
    You can search the history by keyword or a part of word in the following fields:
    
    - title
    - file_name
    - original_path
    - new_path
    - excerpt
    - changes
    - date
    
 ##  Limits 

     - The program reads only valid utf-8 files
     - A file containing any of bites [\x00-\x08\x0b\x0c\x0e-\x1f\x7f] count as binary even if is valid utf-8. This exclude file that look look empty but are full of control bites before normalization or unserchable word as ca\x00sa which looks like  "casa" but after search it is non found. 
     - A .txt or .md file that becomes empty after normalization is skipped and not idexed but its Excerpt is "After normalization, the file is empty."
     - A .csv file that becomes empty after normalization is skipped and not idexed but its Excerpt is "After normalization, the file is empty."

##  Project files

    "__main__.py": starts program and runs normalization loops, session saving and the search.
    "Classes.py": defines "Session" and "Document" classes.
    "Costants.py": defines costants used in other modules
    "DocumentReader.py": scans folders, read and write file for all formats
    "TextReader.py": normalizes txt and md files, cout word and create excerpts.
    "CSVReader.py": normalizes csv, detects the delimiter, create excerpts.
