#
import operator
from typing import Annotated, List, TypedDict

from dotenv import load_dotenv
from langchain_community.chat_models.litellm import ChatLiteLLM
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.graph import END, StateGraph

#


load_dotenv()

#

llm = ChatLiteLLM(model="groq/Llama3-70b-8192")
# llm = ChatLiteLLM(model="ollama/phi3")
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You're the jokester. Respond with a joke, the best joke ever fashioned.",
        ),
        MessagesPlaceholder(variable_name="messages"),
    ],
)


critic_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You're the standup critic. Roast the bad joke."),
        MessagesPlaceholder(variable_name="messages"),
    ],
)


def update(out):
    return {"messages": [out]}


def replace_role(out):
    return {"messages": [("user", out.content)]}


#

## Build the subgraph


class SubGraphState(TypedDict):
    messages: Annotated[List, operator.add]


builder = StateGraph(SubGraphState)
builder.add_node("tell_joke", prompt | llm | update)
builder.add_node("critique", critic_prompt | llm | replace_role)


def route(state):
    return END if len(state["messages"]) >= 3 else "critique"


builder.add_conditional_edges("tell_joke", route)
builder.add_edge("critique", "tell_joke")
builder.set_entry_point("tell_joke")
joke_graph = builder.compile()

if __name__ == "__main__":
    for step in joke_graph.stream({"messages": [("user", "Tell a joke about pasta")]}):
        print(step)
