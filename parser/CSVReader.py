import csv
import io
import re
import unicodedata
from pathlib import Path
from typing import Optional

from .Costants import (
    EMOJI_REGEX,
    INVISIBLE_CHARS_REGEX,
    MULTIPLE_BLANK_LINES_REGEX,
    CONTROL_CHARS_REGEX,
    CSV_DELIMITERS,
    CSV_EXCERPT_MAX_COLUMNS,
)
from .DocumentReader import DocumentReader


class CSVReader(DocumentReader):
  """Specialization for CSV files."""

  EXTENSIONS = [".csv"]

  @staticmethod
  def normalize_text(text: str) -> str:
    """Same rules as TextReader.normalize_text, but TABS ARE KEPT."""
    text = unicodedata.normalize("NFC", text)  # normalize Unicode characters (NFC form)
    text = EMOJI_REGEX.sub("", text)  # delete emoji
    text = INVISIBLE_CHARS_REGEX.sub("", text)  # delete invisible chars
    text = text.replace("\r\n", "\n").replace("\r", "\n")  # unify line breaks to \n
    text = CONTROL_CHARS_REGEX.sub("", text)  # delete control chars, tabs are kept
    text = re.sub(r" {2,}", " ", text)  # collapse only spaces
    text = "\n".join(line.strip(" ") for line in text.split("\n"))
    text = MULTIPLE_BLANK_LINES_REGEX.sub("\n\n", text)
    return text.strip("\n")  # tabs at the edges are kept (they can be empty columns)

  @staticmethod
  def detect_delimiter(header_line: str) -> str:
    """The system finds which delimiter of the list is used: the one that appears most often, "best = max(counts, key=counts.get)"
    Args:
    header_line: str, the header line of the file
    Returns:
    best: str, the separator with the highest count."""
    counts = {d: header_line.count(d) for d in CSV_DELIMITERS}
    best = max(counts, key=counts.get)
    return best if counts[best] > 0 else ","

  @staticmethod
  def create_excerpt(text: str) -> str:
    """First data row as a string of 'column: value' pairs, max 20 columns."""
    first_line = text.strip().split("\n", 1)[0]
    if not first_line:
      return ""
    reader = csv.reader(io.StringIO(text), delimiter=CSVReader.detect_delimiter(first_line))
    rows = (row for row in reader if row)
    header = next(rows, None)
    first_row = next(rows, None)
    if first_row is None:
      return ""
    dict_excerpt = {}
    for column, value in list(zip(header, first_row))[:CSV_EXCERPT_MAX_COLUMNS]:
      dict_excerpt[column] = value
    excerpt = "\n".join(f"{column}: {value}" for column, value in dict_excerpt.items())
    if len(header) > CSV_EXCERPT_MAX_COLUMNS:
      excerpt += "\n..."
    return excerpt

  @staticmethod
  def get_date(text: str, file_name: str) -> Optional[str]: #text is used in txt and md files, file_name is used in csv files
    return CSVReader.find_date_from_title(Path(file_name).stem)

  @staticmethod
  def find_date_from_title(stem: str) -> Optional[str]:
    """The system finds the first date in the title"""
    return DocumentReader.find_date(stem.replace("_", " "))  # '_' is a word char: it hides dates like clienti_20240101
