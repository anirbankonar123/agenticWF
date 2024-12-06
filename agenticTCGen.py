from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated, List
import operator
from langgraph.checkpoint.sqlite import SqliteSaver
from langchain_core.messages import AnyMessage, SystemMessage, HumanMessage, AIMessage, ChatMessage
import json

memory = SqliteSaver.from_conn_string(":memory:")

class AgentState(TypedDict):
    task: str
    plan: str
    draft: str
    critique: str
    content: List[str]
    revision_number: int
    max_revisions: int


from langchain_openai import ChatOpenAI
model = ChatOpenAI(model="gpt-3.5-turbo", temperature=1.0)

PLAN_PROMPT = """You are an expert Quality Assurance person tasked with writing Test cases from User stories. \
Write the Test cases following "SMART" paradigm. 
Utilize all the information below as needed: \

------

User Story: {userstory}
Description: {description}
Acceptance Criteria: {acceptancecriteria}\
."""

WRITER_PROMPT = """You are an expert Quality Assurance person tasked with writing Test cases from User Stories.\
Generate Test cases for each Acceptance criteria and from the Description of User Story\
Each Test case should have Test steps, Expected results and pre-requisites.\
Include non-functional test cases, as needed. \
Include positive and negative Test cases .\
Identify negative test cases with Test case type field.\
Do not generate more than three negative Test cases .\
Generate Test cases in strict JSON format.\
Include Test Case IDs in each Test case for easy Readability.\
Generate 10 Test cases at the minimum.\
Utilize all the information below as needed: \

------

User Story: {userstory}
Description: {description}
Acceptance Criteria: {acceptancecriteria}"""

REFLECTION_PROMPT = """You are a Domain Expert evaluating the Test cases. \
Generate critique and recommendations for the Test cases. \
Provide detailed recommendations, including positive, negative scenarios, non-functional cases."""


def getUserStory(reqmnt_id):
    userstory=""
    description=""
    acceptancecriteria=""
    file1 = open("US_4.txt", "r")
    str = file1.read()
    #str = str[7:-4]
    json_list = []
    json_list.append(json.loads(str))

    #print(len(json_list[0]))
    for item in json_list[0]:
        #print(item['RequirementID'])
        if (item['RequirementID']==reqmnt_id):
            userstory = item['UserStory']
            description = item["Description"]
            acceptancecriteria = item["AcceptanceCriteria"]

    return userstory,description,acceptancecriteria

def plan_node(state: AgentState):
    userstory, description, acceptancecriteria = getUserStory("IKM-SRS-45")
    print("USER STORY INPUT:")
    print(userstory)
    messages = [
        SystemMessage(content=PLAN_PROMPT.format(userstory=userstory,description=description,acceptancecriteria=acceptancecriteria)),
        HumanMessage(content=state['task'])
    ]
    response = model.invoke(messages)
    return {"plan": response.content}



def generation_node(state: AgentState):
    content = "\n\n".join(state['content'] or [])
    user_message = HumanMessage(
        content=f"{state['task']}\n\nHere is my plan:\n\n{state['plan']}")

    userstory, description, acceptancecriteria = getUserStory("IKM-SRS-45")
    print("USER STORY INPUT:")
    print(userstory)

    messages = [
        SystemMessage(
            content=WRITER_PROMPT.format(userstory=userstory,description=description,acceptancecriteria=acceptancecriteria)
        ),
        user_message
        ]
    response = model.invoke(messages)
    return {
        "draft": response.content,
        "revision_number": state.get("revision_number", 1) + 1
    }

def reflection_node(state: AgentState):
    messages = [
        SystemMessage(content=REFLECTION_PROMPT),
        HumanMessage(content=state['draft'])
    ]
    response = model.invoke(messages)
    return {"critique": response.content}

def should_continue(state):
    if state["revision_number"] > state["max_revisions"]:
        return END
    return "reflect"

builder = StateGraph(AgentState)

builder.add_node("planner", plan_node)
builder.add_node("generate", generation_node)
builder.add_node("reflect", reflection_node)

builder.set_entry_point("planner")

builder.add_conditional_edges(
    "generate",
    should_continue,
    {END: END, "reflect": "reflect"}
)

builder.add_edge("planner", "generate")
builder.add_edge("reflect", "generate")

graph = builder.compile(checkpointer=memory)

file1 = open("TC_langgraph_8.txt", "w")

output={}
thread = {"configurable": {"thread_id": "1"}}
for s in graph.stream({
    'task': "generate Test cases from the given User story",
    "max_revisions": 3,
    "revision_number": 1,
}, thread):
    print(s)
    output.update(s)

file1.write(json.dumps(output))
file1.close()



