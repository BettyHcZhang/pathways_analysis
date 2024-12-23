import operator
import os
from typing import TypedDict, Annotated

# import matplotlib.pyplot as plt
# from PIL import Image
# import io
from langchain_core.tools import render_text_description
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START
from langgraph.prebuilt import tools_condition  # this is the checker for the if you got a tool back
from langchain_core.messages import HumanMessage, AnyMessage, ToolMessage, AIMessage, SystemMessage
from langgraph.prebuilt import ToolNode

from pathway_analysis_agent.templates.react_template import get_react_prompt_template
from pathway_analysis_agent.tools.query_gene_diseases_pathway_go import query_gene_diseases_pathway_tool
from pathway_analysis_agent.tools.query_gene_go_tool import query_gene_go_term_tool

from pathway_analysis_agent.tools.query_gene_interactions import query_gene_interaction_downstream_tool

# Create LLM
llm = ChatOpenAI(model=os.getenv("openai_model"), openai_api_key=os.getenv('openai_api_key'), temperature=0,
                 max_tokens=None)

tools = [query_gene_diseases_pathway_tool, query_gene_interaction_downstream_tool, query_gene_go_term_tool]
llm_with_tools = llm.bind_tools(tools)

tool_names = ", ".join([t.name for t in tools])

prompt_template_str = get_react_prompt_template(render_text_description(list(tools)), tool_names)


# Node
def reasoner(state):
    query = state["query"]
    messages = state["messages"]
    # System message
    # messages[-1].content
    state["current_turn"] += 1
    if len(messages) == 0:
        messages = [prompt_template_str]
        message = HumanMessage(content=query)
        messages.append(message)
        result = [llm_with_tools.invoke(messages)]
    else:
        sys_msg = SystemMessage(content=prompt_template_str)
        message = HumanMessage(content=query)
        messages.append(message)
        result = [llm_with_tools.invoke([sys_msg] + messages)]
    return {"messages": result}


class GraphState(TypedDict):
    """State of the graph."""
    query: str
    final_answer: str
    current_turn: int
    # intermediate_steps: Annotated[list[tuple[AgentAction, str]], operator.add]
    messages: Annotated[list[AnyMessage], operator.add]


class ConfigSchema(TypedDict):
    r: float


# Graph
workflow = StateGraph(GraphState, ConfigSchema)

# Add Nodes
workflow.add_node("reasoner", reasoner)
workflow.add_node("tools", ToolNode(tools))  # for the tools

# Add Edges
workflow.add_edge(START, "reasoner")

workflow.add_conditional_edges(
    "reasoner",
    # If the latest message (result) from node reasoner is a tool call -> tools_condition routes to tools
    # If the latest message (result) from node reasoner is a not a tool call -> tools_condition routes to END
    tools_condition,
)

workflow.add_edge("tools", "reasoner")

react_graph = workflow.compile()

# Show
# graph_image_data = react_graph.get_graph(xray=True).draw_mermaid_png()
# Convert byte data to Image
# image = Image.open(io.BytesIO(graph_image_data))
# # Display the image
# plt.imshow(image)
# plt.axis('off')  # Hide axes
# plt.show()

example_query_list = ["find the diseases associated with Gene 'MAPK8'",
                      "find the diseases associated with Gene 'GCK' , also find other entities related to this disease",
                      "what are the entities interact with Gene SOCS4",
                      "what is the go-term about gene 'SOCS4'",
                      "Analyze the cascade downstream effects of 'GCK' on Type II diabetes mellitus."
                      ]

if __name__ == '__main__':
    response = react_graph.invoke({
        "query": example_query_list[-1],
        "messages": [],
        "current_turn": 0
    })

    for m in response['messages']:
        m.pretty_print()
