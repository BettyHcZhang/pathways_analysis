from dataclasses import dataclass
from typing import List

from scripts.data_classes.entries import BaseEntry


@dataclass
class Disease:
    id: str
    name: str  # Disease name, e.g., "Type II diabetes mellitus"
    pathway: str  # Pathway number, e.g., "04930"
    image: str  # Disease pathway image URL
    link: str  # Disease pathway information link
    entry_items: List[BaseEntry]
