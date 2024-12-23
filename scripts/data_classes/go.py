from dataclasses import dataclass
from typing import Optional, List


@dataclass(frozen=True)
class GOTerm:
    go_id: str  # GO Term ID, e.g., GO:0005902
    db: str  # Source database, e.g., UniProtKB
    aspect: str  # GO Aspect (C: Cellular Component, P: Biological Process, F: Molecular Function)


@dataclass
class Evidence:
    evidence_code: str  # Evidence code, e.g., IEA
    reference: str  # GO Reference, e.g., GO_REF:0000107
    date: str  # Annotation date, e.g., 20241014
    assigned_by: str  # Data source, e.g., UniProt
    gene_obj_type: str  # protein


@dataclass
class GeneToGOTermRelation:
    gene_name: str
    go_id: str
    relation: str  # Relationship type, e.g., located_in
    evidences: List[Evidence]
