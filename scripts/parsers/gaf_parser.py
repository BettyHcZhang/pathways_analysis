import xml.etree.ElementTree as ET
from typing import List, Dict

from scripts.data_classes import *


class GAFParser:
    def __init__(self, gaf_file_path: str):
        self.gaf_file_path = gaf_file_path
        self.gene_go_term_relations: List[GeneToGOTermRelation] = []
        self.go_term_collects: Dict[str, GOTerm] = {}
        self.go_term_set = set()

    def parse(self):
        with open(self.gaf_file_path, 'r') as file:
            for line in file:
                if line.startswith("!"):
                    continue
                fields = line.strip().split("\t")
                if len(fields) < 15:
                    continue
                relation_obj = self._create_gene_annotation(fields)
                self.gene_go_term_relations.append(relation_obj)
        return self.gene_go_term_relations, self.go_term_set

    def _get_go_term(self, go_term_id: str, go_term_aspect: str = None) -> GOTerm:
        if go_term_id not in self.go_term_collects:
            go_term = GOTerm(go_id=go_term_id, db="", aspect=go_term_aspect)
            self.go_term_collects[go_term_id] = go_term
        return self.go_term_collects[go_term_id]

    def _create_gene_annotation(self, fields: list) -> GeneToGOTermRelation:
        gene_symbol = fields[2]

        db = fields[0]
        relation = fields[3]
        go_id = fields[4]
        reference = fields[5]
        evidence_code = fields[6]
        aspect = fields[8]
        gene_obj_type = fields[11]
        date = fields[13]
        assigned_by = fields[14]

        go_term = GOTerm(go_id=go_id, db=db, aspect=aspect)
        self.go_term_set.add(go_term)

        evidence = Evidence(
            evidence_code=evidence_code,
            reference=reference,
            date=date,
            assigned_by=assigned_by,
            gene_obj_type=gene_obj_type
        )

        relation_obj = GeneToGOTermRelation(
            gene_name=gene_symbol,
            go_id=go_id,
            relation=relation,
            evidences=[evidence]
        )
        return relation_obj