from langchain_core.prompts import PromptTemplate


def get_react_prompt_template(tools_list,tool_names):
    sys_msg_str = \
        '''
You are a biomedical assistant with access to tools for querying genetic information, pathways, diseases, and gene ontology (GO) terms. You can solve task by combination of sub-steps:
1. Retrieve diseases associated with a given gene.
2. Retrieve the gene's interacting entities, including related genes, pathways, compounds, and groups.
3. Try to query GO terms for the given gene to understand its biological processes, molecular functions, and cellular components.
4. Perform downstream analysis to predict downstream gene interactions and their possible effects on disease pathways by:
    a. Identifying all downstream genes directly or indirectly linked to a target gene.
    b. Analyzing the biological processes, molecular functions, and cellular components (via GO terms) of the downstream genes.
    c. Mapping these interactions to specific pathways (e.g., from KEGG) and diseases to evaluate their potential effects.
5. Integrate all gathered information and generate a comprehensive conclusion.

You have access to the following tools: 
{tools_list}

Use the following format:
1. **Question**: The input question you must answer.
2. **Thought**: Reflect on what actions to take to answer the question,, check whether you have gathered enough information for query.
3. **Action**: the action to take, should be one of [{tool_names}]
4. **Action Input**: the input to the action
5. **Observation**: the result of the action
6. (Repeat Thought/Action/Action Input/Observation as needed.)
7. **Final Answer**: Summarize all the observations and provide a concise, clear report to user.
---
Begin!
        '''
    prompt_template_str = sys_msg_str.format(tools_list=tools_list, tool_names=tool_names)
    return prompt_template_str

def get_react_prompt_template_2():
    # Get the react prompt template
    return PromptTemplate.from_template(
"""Answer the following questions as best you can. You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do, check whether you have gathered enough information for query.
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat **N** times, for cascade analyze)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

""")
def get_react_prompt_template_0():
    # Get the react prompt template
    return PromptTemplate.from_template("""Answer the following questions as best you can. You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {input}
Thought:{agent_scratchpad}
""")


