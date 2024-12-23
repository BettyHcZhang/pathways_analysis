import xml.etree.ElementTree as ET
from typing import List

from scripts.data_classes import *


class KGMLParser:
    def __init__(self, kgml_file_paths: List[str]):
        self.kgml_file_paths = kgml_file_paths
        self.diseases: List[Disease] = []
        self.gene_entry_list: List[BaseEntry] = []
        self.gene_relation_list: List[GeneRelation] = []

    def parse(self):
        for path in self.kgml_file_paths:
            self._parse_each_file(path)
        return self.diseases, self.gene_entry_list, self.gene_relation_list

    def _parse_each_file(self, path: str):
        entry_dict = {}
        tree = ET.parse(path)
        root = tree.getroot()
        number = root.get('number')

        # Parse entries
        for entry in root.findall('entry'):
            type_str = entry.get('type')
            if type_str == 'group':
                base_entry = self._parse_group_entry(entry, entry_dict, number)
            else:
                base_entry = self._parse_regular_entry(entry)
            self.gene_entry_list.append(base_entry)
            entry_dict[entry.get("id")] = base_entry

        # Parse relations
        for relation in root.findall('relation'):
            gr = self._parse_relation(entry_dict, relation)
            self.gene_relation_list.append(gr)

        # Parse disease
        self._parse_disease(entry_dict, root.attrib)

    def _parse_disease(self, entry_dict, pathway_attrs):
        disease = Disease(
            id=pathway_attrs.get("number", ""),
            name=pathway_attrs.get("title", ""),
            pathway=pathway_attrs.get("name", ""),
            image=pathway_attrs.get("image", ""),
            link=pathway_attrs.get("link", ""),
            entry_items=list(entry_dict.values())
        )
        self.diseases.append(disease)

    def _parse_relation(self, entry_dict, relation) -> GeneRelation:
        relation_type = relation.get("type")
        subtypes = [{"name": s.get("name"), "value": s.get("value")} for s in relation.findall('subtype')]
        return GeneRelation(
            entry1=entry_dict[relation.get("entry1")],
            entry2=entry_dict[relation.get("entry2")],
            relation_type=relation_type,
            subtypes=subtypes
        )

    def _parse_group_entry(self, entry, entry_dict, file_number):
        entry_id = entry.get("id")
        name = f'anonymous{file_number}:{entry_id}'
        component_list = entry.findall('component')
        gene_list = [entry_dict[c.get('id')] for c in component_list]
        return GroupEntryNode(name=name, type='Group', components=gene_list)

    def _parse_regular_entry(self, entry) -> MapEntry | CompoundEntry | GeneEntry:
        names = entry.get('name')
        gene_type = entry.get('type').capitalize()
        gene_link = entry.get('link')
        graphics = entry.find('graphics')
        aliases_str = graphics.get('name', '') if graphics is not None else ''
        if entry.get('type') == 'map':
            return MapEntry(names, gene_type, gene_link, [aliases_str])
        elif entry.get('type') == 'compound':
            return CompoundEntry(names, gene_type, gene_link, [aliases_str])
        else:
            return GeneEntry(
                name=names,
                aliases=[a.strip() for a in aliases_str.split(',')],
                type=gene_type,
                link=gene_link
            )
