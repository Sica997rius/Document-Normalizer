import unicodedata

from Costants import (
    WORD_REGEX,
    READABLE_CHARS,
    EMOJI_REGEX,
    INVISIBLE_CHARS_REGEX,
    SPACES_AND_CONTROL_REGEX,
    MULTIPLE_BLANK_LINES_REGEX,
    EXCERPT_LENGTH,
    UNREADABLE_CHARS_NOTE,
)
from DocumentReader import DocumentReader


class TextReader(DocumentReader):
  """Methods valid for txt and md files"""

  @staticmethod
  def count_words(text: str) -> int:
    """The system counts the words in the text"""
    return len(WORD_REGEX.findall(text))

  @staticmethod
  def has_unreadable_chars(text: str) -> bool:
    """The system checks whether the text contains unreadable chars"""
    distinct_chars = set(text.lower())
    return any(ch not in READABLE_CHARS and not ch.isspace() for ch in distinct_chars)

  @staticmethod
  def normalize_text(text: str) -> str:
    """The system normalizes the text for md and txt"""
    text = unicodedata.normalize("NFC", text)  # normalize Unicode characters (NFC form)
    text = EMOJI_REGEX.sub("", text)  # delete emoji
    text = INVISIBLE_CHARS_REGEX.sub("", text)  # delete invisible chars
    text = text.replace("\r\n", "\n").replace("\r", "\n")  # unify line breaks to \n
    lines = [SPACES_AND_CONTROL_REGEX.sub(" ", line).strip() for line in text.split("\n")]  # clean spaces and control chars in each line
    text = "\n".join(lines)  # rebuild text from lines
    text = MULTIPLE_BLANK_LINES_REGEX.sub("\n\n", text)  # keep at most one blank line
    return text.strip()  # remove spaces at start and end

  @staticmethod
  def create_excerpt(text: str, length: int = EXCERPT_LENGTH) -> str:
    words = text.split()
    excerpt = " ".join(words[:length])
    if len(words) > length:
      excerpt += "..."
    if TextReader.has_unreadable_chars(text):
      excerpt = (excerpt + " " + UNREADABLE_CHARS_NOTE).strip()
    return excerpt
