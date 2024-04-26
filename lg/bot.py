"""Bionic bot"""

import operator
import os
from typing import Annotated, TypedDict, Union

from dotenv import load_dotenv
from langchain_core.agents import AgentAction, AgentFinish
from langchain_core.load import dumps
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import END, StateGraph

from .tool_registry import ToolRegistry

#

load_dotenv()
DB_DIR = os.getenv("DB_DIR", "./.db")

#


class BotState(TypedDict):
    input: str
    user_name: str
    agent_out: Union[AgentAction, AgentFinish, None]
    intermediate_steps: Annotated[list[tuple[AgentAction, str]], operator.add]


def new_user_flow(state):
    print("> new_user_flow")
    print(dumps(state, pretty=True))
    return {"agent_out": AgentFinish(return_values={}, log="")}


def existing_user_flow(state):
    print("> existing_user_flow")
    print(dumps(state, pretty=True))
    return {"agent_out": AgentFinish(return_values={}, log="")}


def router(state):
    print("> router")
    print(dumps(state, pretty=True))
    return "new_user_flow"


class Bot:
    """
    The bot class is the main class that will be used to interact with the user.
    """

    def __init__(self, user_name: str) -> None:
        self.user_name = user_name
        self.tool_registry = ToolRegistry()
        os.makedirs(DB_DIR, exist_ok=True)
        bot_db = os.path.join(DB_DIR, "bot.db")
        self.saver = SqliteSaver.from_conn_string(bot_db)

        graph = StateGraph(BotState)
        graph.add_node("new_user_flow", new_user_flow)
        graph.add_node("existing_user_flow", existing_user_flow)
        graph.add_edge("new_user_flow", END)
        graph.add_edge("existing_user_flow", END)
        graph.set_conditional_entry_point(
            condition=router,
            conditional_edge_mapping={
                "new_user_flow": "new_user_flow",
                "existing_user_flow": "existing_user_flow",
            },
        )
        self.graph = graph.compile(self.saver)


if __name__ == "__main__":
    bot = Bot("user")
    thread = {"configurable": {"thread_id": "2"}}
    bot.graph.invoke({"input": "hello"}, thread)
