import xml.etree.ElementTree as ET
from collections import defaultdict
from typing import List

from scripts.data_classes import *

class GeneConnectionManager:
    def __init__(self, gene_entries: List[BaseEntry], gene_go_relations: List[GeneToGOTermRelation]):
        self.gene_entries = gene_entries
        self.gene_go_relations = gene_go_relations
        self.gene_to_annotation_dict = defaultdict(list)

    def establish_connections(self):
        # Map gene_symbol to GO relations
        symbol_to_annotation = {rel.gene_name: rel for rel in self.gene_go_relations}

        # Map aliases in gene_entries to annotations
        for gene_entry in self.gene_entries:
            if isinstance(gene_entry, GeneEntry):
                for alias in gene_entry.aliases:
                    if alias in symbol_to_annotation:
                        self.gene_to_annotation_dict[gene_entry.name].append(symbol_to_annotation[alias])
        return self.gene_to_annotation_dict
    def display_connections(self):
        for gene_entry, annotations in self.gene_to_annotation_dict.items():
            print(f"Alias '{gene_entry}' matches with GAF annotation: {len(annotations)}")
