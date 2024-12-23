import json
import os
from dataclasses import asdict
from math import ceil

from neo4j import GraphDatabase
from typing import List, Dict

from tqdm import tqdm

from dotenv import load_dotenv, find_dotenv

from scripts.data_classes import Disease, BaseEntry, GeneEntry, CompoundEntry, MapEntry, GroupEntryNode, GOTerm, \
    GeneRelation

load_dotenv(find_dotenv())


class Neo4jImporter:
    def __init__(self):
        """
        Initialize a connection to the Neo4j database.
        """
        self.driver = GraphDatabase.driver(os.getenv("NEO4J_URI"),
                                           auth=(os.getenv("NEO4J_USERNAME"), os.getenv("NEO4J_PASSWORD")))

        self.neo4j_db = os.getenv("NEO4J_NAME")

    @staticmethod
    def __batchify(iterable, batch_size=100):
        """
        Helper function to create batches from a list.
        """
        for i in range(0, len(iterable), batch_size):
            yield iterable[i:i + batch_size]

    def __get_db_session(self):
        return self.driver.session(database=self.neo4j_db)

    def __execute_batch_query(self, query: str, data: List[Dict], batch_size: int = 100):
        """
        Execute a batch query with the provided data and batch size.
        :param query: Cypher query to execute.
        :param data: List of data items to process in batches.
        :param batch_size: Number of items to include in each batch.
        """
        with self.__get_db_session() as session:
            for batch in tqdm(self.__batchify(data, batch_size), desc="Executing batch query"):
                session.run(query, batch)

    def create_constraints(self):
        """
        Create unique constraints for nodes in the Neo4j database.
        This ensures data consistency and prevents duplication.
        :param importer: An instance of Neo4jImporter.
        """
        queries = [
            "CREATE CONSTRAINT IF NOT EXISTS FOR (g:Gene) REQUIRE g.name IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (go:GO_Term) REQUIRE go.go_id IS UNIQUE"
        ]
        with self.__get_db_session() as session:
            for query in queries:
                session.run(query)

    def create_diseases(self, disease_list: List[Disease]):
        """
        Create Disease nodes in Neo4j from a list of Disease objects.
        """
        # Step 1: Prepare the data in the correct format for batch insertion
        data = [asdict(disease) for disease in disease_list]

        # Step 2: Use UNWIND for batch insertion
        query = """
               UNWIND $diseases AS disease
               MERGE (d:Disease {id: disease.id})
               SET d.name = disease.name,
                   d.pathway = disease.pathway,
                   d.image = disease.image,
                   d.link = disease.link
           """

        with self.__get_db_session() as session:
            session.run(query, diseases=data)

    def create_pathway_relationship(self, disease_list: List[Disease]):
        """
        Create relationships between Disease nodes and pathway items (entry_items) in batches with progress tracking.
        """
        print('create_pathway_relationship, with disease_list, count:', len(disease_list))

        # Flatten relationships into a list of tuples
        relationships = [[disease.id, ele.name, ele.type] for disease in disease_list for ele in disease.entry_items]

        query = """
                UNWIND $relationships AS rel
                MATCH (d:Disease {id: rel[0]}), (g {name: rel[1], type: rel[2]})
                MERGE (d)-[:ASSOCIATED_WITH]->(g)
                """
        with self.__get_db_session() as session:
            for entry_batch in tqdm(self.__batchify(relationships),
                                    desc=f"Processing Relationships of diseases"):
                session.run(query, relationships=entry_batch)

        print('DONE create_pathway_relationship, with disease_list, count:', len(disease_list))

        print('DONE create_pathway_relationship, with disease_list, count:', len(disease_list))

    def create_gene(self, gene_entry_list: List[BaseEntry]):
        print('gene_entry_list count:', len(gene_entry_list), 'inserting...')
        gene_entries = [entry for entry in gene_entry_list if isinstance(entry, GeneEntry)]
        self.__batch_insert_gene_entries(gene_entries, 'Gene')
        compound_entries = [entry for entry in gene_entry_list if isinstance(entry, CompoundEntry)]
        self.__batch_insert_gene_entries(compound_entries, 'Compound')
        map_entries = [entry for entry in gene_entry_list if isinstance(entry, MapEntry)]
        self.__batch_insert_gene_entries(map_entries, 'Map')

        # Separate GroupNode and other types
        anonymous_entries = [entry for entry in gene_entry_list if isinstance(entry, GroupEntryNode)]
        self.insert_group_entry(anonymous_entries)

    def __batch_insert_gene_entries(self, gene_entries: List[BaseEntry], label: str = "Gene", batch_size: int = 100):
        """
        Batch inserts GeneEntry objects into the database with the specified label.

        :param gene_entries: List of GeneEntry objects to insert.
        :param label: The label to apply to the nodes in the database (default: "Gene").
        :param batch_size: The number of entries to process in each batch (default: 100).
        """
        query = f"""
                UNWIND $entries AS entry
                MERGE (g:{label} {{name: entry.name}})
                SET g.type = entry.type,
                    g.link = entry.link,
                    g.aliases = entry.aliases
             """
        print(f"Inserting {label} entries...")
        input_entries = [
            {
                'name': entry.name,
                'type': entry.type,
                'link': entry.link,
                'aliases': entry.aliases
            }
            for entry in gene_entries
        ]

        with self.__get_db_session() as session:
            for entry_batch in tqdm(self.__batchify(gene_entries, batch_size), desc=f"Processing {label} Entries"):
                session.run(query, entries=input_entries)

    def insert_group_entry(self, anonymous_entries):
        with self.__get_db_session() as session:
            for anonymous_entry in tqdm(anonymous_entries, desc="Processing Anonymous Entries"):
                # Insert GroupNode node
                query = """
                                MERGE (a:GroupNode {name: $name})
                                SET a.type = $type
                        """
                session.run(query, name=anonymous_entry.name, type=anonymous_entry.type)
            # Batch insert components for GroupNode
            print("Creating relationships for GroupNode components...")
            for anonymous_entry in tqdm(anonymous_entries, desc="Processing Anonymous Components"):
                for component in anonymous_entry.components:
                    component_query = """
                                       MERGE (a:GroupNode {name: $name})
                                       MERGE (b {name: $component_name, type:$component_type})
                                       MERGE (a)-[:CONTAINS]->(b)
                                   """
                    session.run(component_query, name=anonymous_entry.name, component_name=component.name,
                                component_type=component.type)

    def create_relationships_with_subtypes_batch(self, gene_relation_list: List[GeneRelation]):
        """
        Batch creates relationships between nodes with subtypes as a property.
        :param gene_relation_list: List of dictionaries, each containing:
            - entry1_name: Name of the first gene
            - entry2_name: Name of the second gene
            - relation_type: Type of the relationship
            - subtypes: List of subtypes as dictionaries with 'name' and 'value'
        """
        query = """
        UNWIND $relations AS rel
        MERGE (a {name: rel.entry1_name, type:rel.entry1_type})
        MERGE (b {name: rel.entry2_name, type:rel.entry2_type})
        WITH a, b, rel
        
        UNWIND rel.subtypes AS subtype
        MERGE (a)-[r:RELATION {type: rel.relation_type, name: subtype.name, value: subtype.value}]->(b)
        RETURN a, r, b
        """
        insert_list = []
        for item in gene_relation_list:
            insert_list.append({
                "entry1_name": item.entry1.name,
                "entry1_type": item.entry1.type,
                "entry2_name": item.entry2.name,
                "entry2_type": item.entry2.type,
                "relation_type": item.relation_type,
                "subtypes": item.subtypes
            })

        with self.__get_db_session() as session:
            for batch in tqdm(self.__batchify(insert_list)):
                # Execute batch query
                session.run(query, relations=batch)

    def create_go_term(self, go_term_list: List[GOTerm]):
        """
        Create GO_Term nodes in the Neo4j database from a list of GOTerm objects using batch insertion.
        """
        query = """
                    UNWIND $go_terms AS go_term
                    MERGE (go:GO_Term {go_id: go_term.go_id})
                    SET go.db = go_term.db,
                        go.aspect = go_term.aspect
                    """

        go_terms_data = [asdict(gt) for gt in go_term_list]
        print('inserting GO Terms, count:', len(go_terms_data))

        with self.__get_db_session() as session:
            for batch in tqdm(self.__batchify(go_terms_data)):
                session.run(query, go_terms=batch)
            print('inserting GO Terms, count:', len(go_terms_data))

    def insert_gene_go_relations(self, gene_to_go_dict):
        """
        Insert Gene-to-GO relationships into the Neo4j database using batch insertion.
        Each relation includes a gene, a GO term, the relationship type, and associated evidence.
        """

        # Prepare data for batch insertion
        # Convert each GeneToGOTermRelation and its Evidence objects into dictionaries
        relations_data = []

        for gene, relations in gene_to_go_dict.items():
            for rel in relations:
                # Convert each Evidence to JSON string
                evidences_as_json = [json.dumps(ev.__dict__) for ev in rel.evidences]
                rel_dict = asdict(rel)
                rel_dict['gene_name'] = gene
                rel_dict['new_evidences'] = evidences_as_json  # This is a list of JSON strings
                relations_data.append(rel_dict)
        print("Inserting gene-GO relations, count:", len(relations_data))

        # Cypher query for batch insertion
        # Uses UNWIND to process the list of relations
        query = """
            UNWIND $relations AS rel
            MERGE (g:Gene {name: rel.gene_name})
            MERGE (go:GO_Term {go_id: rel.go_id})
            MERGE (g)-[r:GO_RELATION {type: rel.relation}]->(go)
            SET r.evidences = coalesce(r.evidences, []) + rel.new_evidences
        """
        # Execute the query in batches to avoid memory issues
        with self.__get_db_session() as session:
            for batch in tqdm(self.__batchify(relations_data)):
                session.run(query, relations=batch)

        print("Finished inserting gene-GO relations, count:", len(relations_data))

    def import_all_data(self,parser):
        diseases, gene_entry_list, gene_relation_list, gene_to_annotation_dict, go_term_set = parser.parse_all()
        print("DONE KG Process")
        self.create_constraints()
        self.create_diseases(diseases)
        self.create_gene(gene_entry_list)  # Insert gene entries into the Neo4j database
        self.create_pathway_relationship(diseases)  # Create relationships between diseases and genes
        self.create_relationships_with_subtypes_batch(gene_relation_list)

        self.create_go_term(list(go_term_set))  # Add GO_Term nodes and their attributes
        self.insert_gene_go_relations(gene_to_annotation_dict)  # Add GeneAnnotation nodes
