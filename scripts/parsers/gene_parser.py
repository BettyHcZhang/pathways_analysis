import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import List, Optional

from scripts.data_classes import *
from scripts.parsers.gaf_parser import GAFParser
from scripts.parsers.gene_connection_manager import GeneConnectionManager
from scripts.parsers.kgml_parser import KGMLParser


@dataclass
class GeneParser:
    kgml_file_path: Optional[List[str]] = None
    gaf_file_path: str = '../data/goa_human.gaf'

    def __post_init__(self):
        if self.kgml_file_path is None:
            self.kgml_file_path = [
                '../data/KEGG_data/KGML/hsa04930.xml',
                '../data/KEGG_data/KGML/hsa05010.xml',
                '../data/KEGG_data/KGML/hsa05012.xml',
                '../data/KEGG_data/KGML/hsa05210.xml'
            ]

    def parse_all(self):
        # Parse KGML
        kgml_parser = KGMLParser(self.kgml_file_path)
        diseases, gene_entry_list, gene_relation_list = kgml_parser.parse()

        # Parse GAF
        gaf_parser = GAFParser(self.gaf_file_path)
        gene_go_relations, go_term_set = gaf_parser.parse()

        # Establish connections
        connection_manager = GeneConnectionManager(gene_entry_list, gene_go_relations)
        gene_to_annotation_dict = connection_manager.establish_connections()
        connection_manager.display_connections()
        return diseases, gene_entry_list, gene_relation_list, gene_to_annotation_dict, go_term_set


if __name__ == '__main__':
    parser = GeneParser()
    parser.parse_all()
