
from langchain_core.prompts import PromptTemplate
def get_cypher_generation_prompt():
    cypher_generation_template_str = """
Task:
Generate Cypher query for a Neo4j graph database.

Instructions:
Use only the provided relationship types and properties in the schema.
Do not use any other relationship types or properties that are not provided.

Schema:
{schema}

Note:
Do not include any explanations or apologies in your responses.
Do not respond to any questions that might ask anything other than
for you to construct a Cypher statement. Do not include any text except
the generated Cypher statement. Make sure the direction of the relationship is
correct in your queries. Make sure you alias both entities and relationships
properly. Do not run any queries that would add to or delete from
the database.

Gene, Map, Compound, their names are stored in aliases. When you are searching, remember to
use the list of aliases to find.

Query Gene->GO Term, do remember return relations, as very important information on relations. 

Examples:
# 1. To retrieve the diseases associated with Gene 'MAPK8':
MATCH (d:Disease)-[r:ASSOCIATED_WITH]->(g:Gene)
WHERE 'MAPK8' IN g.aliases
RETURN DISTINCT properties(d)

# 2. To find all pathways linked to a specific Compound 'C01319':
MATCH (d:Disease)-[:ASSOCIATED_WITH]->(c:Compound)
WHERE "C01319" IN c.aliases
RETURN DISTINCT properties(d)

# 3. To list genes associated with the Disease 'Colorectal cancer':
MATCH (g:Gene)<-[r:ASSOCIATED_WITH]-(d:Disease)
WHERE d.name = "Colorectal cancer
return properties(g)

# 4. Which group are associated with Alzheimer's disease?
MATCH (d:Disease)-[:ASSOCIATED_WITH]->(c:GroupNode)-[r]->(g)
WHERE d.name = "Alzheimer's disease"
RETURN DISTINCT 
    properties(c), 
    properties(r), 
    properties(g)

# 5. What are the entities directly related to the gene MAPK8?
MATCH (n:Gene)-[:RELATION]->(target)
WHERE 'MAPK8' IN n.aliases AND 
      (target:Gene OR target:Compound OR target:GroupNode OR target:Map)
RETURN DISTINCT properties(n) AS gene, properties(target) AS related_entity

# 6.What are the GO terms associated with the gene alias 'PKLR'
MATCH (g:Gene)-[r:GO_RELATION]->(go:GO_Term)
where 'PKLR' in g.aliases
RETURN distinct properties(r),properties(go)

Use existing strings and values from the schema provided. 

The question is:
{question}
"""

    cypher_generation_prompt = PromptTemplate(
        input_variables=["schema", "question"], template=cypher_generation_template_str
    )
    return cypher_generation_prompt