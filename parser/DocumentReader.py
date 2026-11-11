import re
from datetime import datetime
from pathlib import Path
from typing import Optional

from .Costants import FILENAME_DATE_PATTERNS, CONTROL_BYTES_REGEX, BINARY_FILE_NOTE, WORD_REGEX


class DocumentReader:
  """Methods valid for every allowed format (TXT, MD, CSV)."""

  # ---------- folder and file list ----------
  @staticmethod
  def open_document_list(input_path: Optional[str] = None) -> dict[int, Path]:
    """Recursively explores a directory chosen by the user."""
    if input_path is None:
      input_path = input("Which folder do you want to analyze? ")
    folder_path = Path(input_path)
    if not folder_path.is_dir():
      print("The given folder does not exist or is not valid.")
      return {}
    document_list = {
      number: path
      for number, path in enumerate(folder_path.rglob("*"), start=1)
      if path.is_file() and not path.is_symlink()
    }
    skipped_links = sum(1 for path in folder_path.rglob("*") if path.is_symlink())
    if skipped_links:
      print(f"Symbolic links skipped: {skipped_links}")
    return document_list

  @staticmethod
  def allowed_extensions(document_list: dict[int, Path], extensions) -> dict[int, tuple[str, str]]:
    """Returns only the files with an allowed extension."""
    return {
      number: (path.name, path.suffix.lower())
      for number, path in document_list.items()
      if path.suffix.lower() in extensions
    }

  @staticmethod
  def disallowed_extensions(document_list: dict[int, Path], extensions) -> dict[int, tuple[str, str]]:
    """Returns the files excluded because of a disallowed extension."""
    return {
      number: (path.name, path.suffix.lower())
      for number, path in document_list.items()
      if path.suffix.lower() not in extensions
    }

  @staticmethod
  def documents_by_format(allowed_files: dict[int, tuple[str, str]], extension: str) -> dict[int, tuple[str, str]]:
    return {number: data for number, data in allowed_files.items() if data[1] == extension}

  @staticmethod
  def count_words(text: str) -> int:
    """The system counts the words in the text"""
    return len(WORD_REGEX.findall(text))

  @staticmethod
  def valid_dates(text: str) -> list:
    found = []
    for pattern, order in FILENAME_DATE_PATTERNS:  # tries all 3 formats
      for match in pattern.finditer(text):
        parts = dict(zip(order, match.groups()))
        year, month, day = int(parts["year"]), int(parts["month"]), int(parts["day"])
        if not 1900 <= year <= 2100:
          continue
        try:  # because some dates don't exist, e.g. 2026-02-31 or 2026-13-31
          datetime(year, month, day)
        except ValueError:
          continue
        found.append((match.start(), year, month, day, order, match.group(0)))
    return found

  @staticmethod
  def find_date(text: str) -> Optional[str]:
    """The system finds the first valid date in the text"""
    found = DocumentReader.valid_dates(text)
    if not found:
      return None
    _pos, year, month, day, order, _text = min(found)  # first date found
    if order[0] == "day" and day <= 12 and order[1] == "month" and month <= 12:  # because the system doesn't know if it's the day or the month
      return f"{year:04d}-{month:02d}-{day:02d} uncertain format"
    return f"{year:04d}-{month:02d}-{day:02d}"

  @staticmethod
  def title_from_filename(stem: str) -> str:
    """Build a title from the file name, with all valid dates moved to the end."""
    work = stem.replace("_", " ").replace("-", " ")
    found_dates = [(text, f"{year:04d}-{month:02d}-{day:02d}") for _pos, year, month, day, _order, text in DocumentReader.valid_dates(work)]
    title = work
    for date_text, _iso in found_dates:  # remove every valid date
      title = title.replace(date_text, " ")
    words = re.split(r"[\s.\-]+", title)  # split on one or more consecutive spaces, dots or hyphens
    title = " ".join(word.capitalize() for word in words if word)  # capitalize each word and join them
    unique_dates = sorted({iso for _text, iso in found_dates}, reverse=True)  # dates without repetitions, the youngest first
    title = f"{title} {' '.join(unique_dates)}".strip()
    return title if title else stem

  @staticmethod
  def read_text(file_path: Path) -> tuple[str, bool]:
    """Read the file as bytes, check whether it is a binary file and, if it is not, decode it to text. Returns (text, is_binary)."""
    # Read the whole file as raw bytes (no interpretation yet). Returns (text, is_binary).
    data = file_path.read_bytes()

    # Even a single control byte (including the null byte) means a binary file.
    if CONTROL_BYTES_REGEX.search(data):
      return BINARY_FILE_NOTE, True

    try:
      return data.decode("utf-8"), False
    except UnicodeDecodeError:
      return BINARY_FILE_NOTE, True

  @staticmethod
  def write_text(file_path: Path, text: str) -> None:
    """Rewrite the file in utf-8, the only encoding that read_text reads."""
    with open(file_path, "w", encoding="utf-8", newline="") as f_out:  # newline="": line breaks are written as they are
      f_out.write(text)

  @staticmethod
  def unique_path(file_path: Path, new_path: Path) -> Path:
    """Return new_path, or "title (n).ext" where n is the first free number if another file already has that name."""
    candidate = new_path
    n = 1
    while candidate.exists() and not candidate.samefile(file_path):  # samefile: a change of case only (report -> Report) is not a duplicate
      candidate = new_path.with_name(f"{new_path.stem} ({n}){new_path.suffix}")
      n += 1
    return candidate
