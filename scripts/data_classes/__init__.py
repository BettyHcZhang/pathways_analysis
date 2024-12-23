from .disease import Disease
from .go import GOTerm, Evidence, GeneToGOTermRelation
from .entries import GroupEntryNode, MapEntry, CompoundEntry, GeneEntry, GeneRelation, BaseEntry

__all__ = [
    'Disease',
    'GOTerm', 'Evidence', 'GeneToGOTermRelation',
    'GeneEntry', 'GeneRelation', 'BaseEntry',
    'GroupEntryNode', 'MapEntry', 'CompoundEntry'
]