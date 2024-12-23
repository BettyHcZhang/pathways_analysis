from scripts.neo4j_importer import Neo4jImporter
from scripts.parsers import GeneParser

if __name__ == '__main__':
    parser = GeneParser()

    importer = Neo4jImporter()

    importer.import_all_data(parser)
