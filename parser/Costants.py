import re
from pathlib import Path
WORD_REGEX = re.compile(r"\w+", re.UNICODE)
EMOJI_REGEX = re.compile(
    "[\U0001F000-\U0001FAFF"   # emoji principali (facce, animali, oggetti, bandiere...)
    "\u2600-\u27BF"            # simboli vari
    "\uFE0F"                   # segnale invisibile "mostra come emoji"
    "\u200D]"                  # unione invisibile delle emoji composte
)
MULTIPLE_BLANK_LINES_REGEX = re.compile(r"\n{3,}") #finds 3 or more consecutive newlines
INVISIBLE_CHARS_REGEX = re.compile(r"[\u200b\u200c\u200d\ufeff\u00ad]") #finds invisible chars in the list of chars with length = 0
                                                                        #\u200b(space), \u200c(non joiner es."ciao" == "ci\u200cao" )\u200d (joiner a larghezza zero used for emoji unified es 👨 + ZWJ + 👩 + ZWJ + 👧 = 👨‍👩‍👧)
                                                                        #\ufeff (BOM should be in the text if:
                                                                        #1)concatenate two files that both start with the BOM
                                                                        #2)text copied from editors or web pages that include the BOM
                                                                        #\u00ad] (soft hyphen): invisible hyphen marking where a word may be split
                                                                        #across lines. It often remains in text copied from PDFs or web pages
SPACES_AND_CONTROL_REGEX = re.compile(r"[ \t\x00-\x08\x0b\x0c\x0e-\x1f\x7f]+") # 1 or more of chars in the list:\t(tab),[\x00-\x08](list of bites from 0 to 8),
                                                                               #\x0b(vertical tab),\x0c\x0e-\x1f , (list of bites from 14 to 31),\x7f (DEL)"
READABLE_CHARS = set("qwertyuiopasdfghjklzxcvbnm,.-;:_òà1234567890'|!$€%&/()=?^@#é*[}]è{ù+°ì`’‘«»“”…–—<>~ó\"£\\")                                                                              
CONTROL_CHARS_REGEX = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]") # same control chars as above, but WITHOUT space and tab (used for CSV, where tabs are kept)
CONTROL_BYTES_REGEX = re.compile(rb"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]") # raw bytes pattern: it works only on `bytes`, not on `str`.
FILENAME_DATE_PATTERNS = [
    (re.compile(r"\b(\d{4})[ /.-](\d{2})[ /.-](\d{2})\b"), ("year", "month", "day")),   # 2024-03-15, 2024_03_15, 2024.03.15 and combination of separators
    (re.compile(r"\b(\d{2})[ /.-](\d{2})[ /.-](\d{4})\b"), ("day", "month", "year")),   # 15-03-2024, 15_03_2024, 15.03.2024 and combination of separators
    (re.compile(r"\b(\d{4})(\d{2})(\d{2})\b"), ("year", "month", "day")),               # 20240315
]
EXCERPT_LENGTH = 60
BINARY_FILE_NOTE = "BINARY FILE: CONTENT NOT READABLE."
FILE_NORMALIZED_EMPTY_NOTE = "After normalization, the file is empty."
UNREADABLE_CHARS_NOTE = "Some characters could not be read or belong to other languages"
CSV_DELIMITERS = [",", ";", "\t"]
CSV_EXCERPT_MAX_COLUMNS = 20
EXTENSIONS = [".txt", ".csv", ".md"]
SESSION_FILE = Path(__file__).parent / "session.json"  # name of the history file of the sessions

