import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from Costants import SESSION_FILE


@dataclass
class Session:
  """It represents a complete normalization session, which is indexed in the history in the 'session.json' file with the following attributes:
    session_id: int (the KEY of the session)
    session_date: datetime (date and time when the session ended)
    documents: dict[str, Any] = field(default_factory=dict) (dictionary that holds the metadata of the documents during the normalization session)"""

  session_id: int
  session_date: datetime
  documents: dict[str, Any] = field(default_factory=dict)

  @property
  def last_session(self) -> int:
    """The system reads the JSON file 'session.json' and finds the last session saved in the history
    Returns:
    int: the maximum value of session_id that the system has found"""
    try:
      with open(SESSION_FILE, "r", encoding="utf-8") as file:
        content = json.load(file)
        if isinstance(content, list):
          max_id = max((s.get("session_id", 0) for s in content), default=0)
        else:
          max_id = 0
        return max_id
    except (FileNotFoundError, json.JSONDecodeError):
      return 0


@dataclass
class Document:
  document_id: str
  new_title: str
  original_title: str
  word_count: int
  excerpt: str
  new_content: str
  format: str
  path: str
  original_content: Optional[str] = None
  date: Optional[str] = None

  @property
  def title_changed(self) -> bool:
    """True if the title has changed"""
    return Path(self.original_title).stem != self.new_title

  @property
  def text_changed(self) -> bool:
    """True if the content changes after the normalization"""
    return self.original_content != self.new_content

  @property
  def changes_made(self) -> str:
    """The system checks whether the title or the text has changed.

    If changes were made during the normalization, the property records the kind of changes.

    Returns:
      str: descriptive string of the detected changes"""
    changes = []
    if self.title_changed:
      changes.append("title changed")
    if self.text_changed:
      changes.append("text changed")
    if changes:
      return "Changes made: " + ", ".join(changes)
    else:
      return "No changes made"
