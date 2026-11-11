# Document-Normalizer
    
    **Warning:** this program renames and overwrites your original files. 'session.json. does not store the original text, so make a backup first.


    Document-Normalizer normalizes title end text of the documents in a folder and saves each session in a history that you can search. 
    
    ## Requirements
    
    Python 3.10 or later. No external libraries are needed.

    ## Installation

    From the Document-Normalizer folder:

        pip install .

    Then start the program with:

        python -m parser

    ## Commands in notebook ativated

        python -m parser normalize file_di_esempio --yes
        python -m parser normalize file_di_esempio --no
        python -m parser search mario
        python -m parser list
        python -m parser list --ext csv
        python -m parser stats

    ##Args Comands 
    
      prog: "python -m parser"
      values: file_di_esempio (folder)
      --yes: y
      --no: n
      comand: ["normalize", "search", "list", "stats"]

    ##Usage after istallation

    1. The program asks whether you want normalize a folder or search in 'session.json' a document by keywords, or press 'l' to list the documents, 't' for statistics. 
    2. If you choose to normalize, the program scans the folder and its subfolders, and classifizes allowed and disallowed files:
        - Allowed files: .txt, .md, .csv
        - disallowed files: any others
    3. the program asks whether you want to apply the changes:
        - if  you answer no, program skips normalization and opens the search.
        - if answer yes, the program normalizes the allowed files, saves the processed documents in 'session.json', prints how many documents were processed and which were discarded and why, and opens the search.

     ## Search
    You can search the history by keyword or a part of word in the following fields:
    
    - title
    - file_name
    - original_path
    - new_path
    - excerpt
    - changes
    - ext
    - date
    
    ##Limits 

     - The program reads only valid utf-8 files
     - A file containing any of bites [\x00-\x08\x0b\x0c\x0e-\x1f\x7f] count as binary even if is valid utf-8. This exclude file that look look empty but are full of control bites before normalization or unserchable word as ca\x00sa which looks like  "casa" but after search it is non found. 
     - A .txt, .md or .csv file that becomes empty after normalization is skipped, not indexed, and listed among the discarded files with the reason "empty after normalization".

    ## Adding a format

    Write a class that inherits DocumentReader, with EXTENSIONS, normalize_text, create_excerpt and get_date, and add it to READERS in __main__.py.

    ##Project files

    "__main__.py": menu, commands, normalization loop, session saving, search, list and statistics.
    "Classes.py": defines "Session" and "Document" classes.
    "Costants.py": defines costants used in other modules
    "DocumentReader.py": scans folders, read and write file, count words for all formats
    "TextReader.py": normalizes txt and md files, create excerpts, find the date.
    "CSVReader.py": normalizes csv, detects the delimiter, create excerpts.
