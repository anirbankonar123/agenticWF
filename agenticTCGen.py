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
model = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

PLAN_PROMPT = """You are an expert Quality Assurance person tasked with writing Test cases from User stories. \
Write the Test cases following "SMART" paradigm. \
."""

WRITER_PROMPT = """You are an expert Quality Assurance person tasked with writing Test cases from User Stories.\
Generate Test cases for each Acceptance criteria and from the Description \
Include non-functional test cases, as needed. \
Include positive and negative Test cases in the ratio 70:30.\
Utilize all the information below as needed: 

------

User Story: {userstory}
Description: {description}
Acceptance Criteria: {acceptancecriteria}"""

REFLECTION_PROMPT = """You are a Domain Expert evaluating the Test cases. \
Generate critique and recommendations for the Test cases. \
Provide detailed recommendations, including positive, negative scenarios, non-functional cases."""


from langchain_core.pydantic_v1 import BaseModel

class Queries(BaseModel):
    queries: List[str]

def plan_node(state: AgentState):
    messages = [
        SystemMessage(content=PLAN_PROMPT),
        HumanMessage(content=state['task'])
    ]
    response = model.invoke(messages)
    return {"plan": response.content}

def generation_node(state: AgentState):
    content = "\n\n".join(state['content'] or [])
    user_message = HumanMessage(
        content=f"{state['task']}\n\nHere is my plan:\n\n{state['plan']}")
    file1 = open("MyFile.txt", "r")
    str = file1.read()
    str = str[7:-4]
    json_list = []
    json_list.append(json.loads(str))

    userstory=json_list[0][5]['UserStory']
    description=json_list[0][5]['Description']
    acceptancecriteria=json_list[0][5]['AcceptanceCriteria']

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

thread = {"configurable": {"thread_id": "1"}}
for s in graph.stream({
    'task': "generate Test cases from the User stories",
    "max_revisions": 2,
    "revision_number": 1,
}, thread):
    print(s)



