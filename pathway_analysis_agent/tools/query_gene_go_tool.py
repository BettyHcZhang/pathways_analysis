import os

from langchain.tools import tool
from pathway_analysis_agent.chains.cypher_query_chain import create_cypher_chain
from pathway_analysis_agent.templates.cypher_generation_template import get_cypher_generation_prompt

cypher_chain = create_cypher_chain(get_cypher_generation_prompt())

@tool("query_gene_go_term_tool", return_direct=True)
def query_gene_go_term_tool(query: str) -> str:
    """
This tool generates and executes a Cypher query to retrieve gene, GO-Term and return the data to you.
"""
    try:
        response = cypher_chain.invoke(query)
        print('response:', response)
        return response.get("result")
    except Exception as e:
        print(f"OpenAI API returned an error: {e}")
