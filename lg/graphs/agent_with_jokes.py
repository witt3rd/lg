#
import operator
from typing import Annotated, List, TypedDict

from dotenv import load_dotenv
from langchain_community.chat_models.litellm import ChatLiteLLM
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.graph import StateGraph

from lg.joke_graph import SubGraphState, joke_graph

#


load_dotenv()

#

llm = ChatLiteLLM(model="groq/Llama3-70b-8192")


class AssistantState(TypedDict):
    conversation: Annotated[List, operator.add]


assistant_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful assistant"),
        MessagesPlaceholder(variable_name="conversation"),
    ]
)


def add_to_conversation(message):
    return {"conversation": [message]}


main_builder = StateGraph(AssistantState)
main_builder.add_node("assistant", assistant_prompt | llm | add_to_conversation)


def get_user_message(state: AssistantState):
    last_message = state["conversation"][-1]
    # Convert to sub-graph state
    return {"messages": [last_message]}


def get_joke(state: SubGraphState):
    final_joke = state["messages"][-1]
    return {"conversation": [final_joke]}


main_builder.add_node("joke_graph", get_user_message | joke_graph | get_joke)


def route(state: AssistantState):
    if "joke" in state["conversation"][-1][-1]:
        return "joke_graph"
    return "assistant"


main_builder.set_conditional_entry_point(
    route,
)
main_builder.set_finish_point("assistant")
main_builder.set_finish_point("joke_graph")
graph = main_builder.compile()


if __name__ == "__main__":
    for step in graph.stream(
        {"conversation": [("user", "Tell a joke about time travel")]}
    ):
        print(step)
    for step in graph.stream({"conversation": [("user", "How YOU doin?")]}):
        print(step)
