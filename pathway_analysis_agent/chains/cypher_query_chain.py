import os
from langchain_community.graphs import Neo4jGraph
from langchain_neo4j import GraphCypherQAChain, Neo4jGraph
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

def create_cypher_chain(cypher_prompt, qa_generation_prompt=None, llm_model=None):
    """
    Create a Cypher Chain for querying a Neo4j graph database.

    :param cypher_prompt: PromptTemplate for generating Cypher queries
    :param qa_prompt_template: PromptTemplate for generating human-readable responses (optional)
    :param llm_model: OpenAI model to use for LLM interactions (default to environment variable)
    :return: GraphCypherQAChain instance
    """

    graph = Neo4jGraph(
        url=os.getenv("NEO4J_URI"),
        username=os.getenv("NEO4J_USERNAME"),
        password=os.getenv("NEO4J_PASSWORD"),
        database=os.getenv('NEO4J_NAME')
    )
    graph.refresh_schema()

    llm_model = llm_model or ChatOpenAI(model=os.getenv("openai_model"), temperature=0, openai_api_key=os.getenv("openai_api_key"))

    return GraphCypherQAChain.from_llm(
        top_k=os.getenv('NEO4J_TOP_K'),
        graph=graph,
        verbose=True,
        validate_cypher=False,
        llm=llm_model,
        qa_prompt=None,
        cypher_prompt=cypher_prompt,
        #qa_llm=ChatOpenAI(model=os.getenv("openai_model"), temperature=0, openai_api_key=os.getenv("openai_api_key")),
        cypher_llm=ChatOpenAI(model=os.getenv("openai_model"), temperature=0, openai_api_key=os.getenv("openai_api_key")),
        return_direct=True,
        allow_dangerous_requests=True
    )
