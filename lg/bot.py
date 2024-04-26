"""Bionic bot"""

import operator
import os
from typing import Annotated, TypedDict, Union

from dotenv import load_dotenv
from langchain_core.agents import AgentAction, AgentFinish
from langchain_core.load import dumps
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import END, StateGraph

from .runnables.chat_router import chat_router_chain
from .tool_registry import ToolRegistry
from .user_profile import load_user_profile, save_user_profile

#

load_dotenv()
DB_DIR = os.getenv("DB_DIR", "./.db")

#


class BotState(TypedDict):
    input: str
    user_name: str
    user_profile: str
    agent_out: Union[AgentAction, AgentFinish, None]
    intermediate_steps: Annotated[list[tuple[AgentAction, str]], operator.add]
    reply: str


def new_user_flow(state):
    print("> new_user_flow")
    print(dumps(state, pretty=True))
    new_state = state.copy()
    new_state["user_profile"] = "new"
    new_state["agent_out"] = AgentFinish(return_values={}, log="")
    return new_state


def existing_user_flow(state):
    print("> existing_user_flow")
    print(dumps(state, pretty=True))
    msgs = [HumanMessage(content=state["input"])]
    res = chat_router_chain.invoke(msgs)
    print(res)
    new_state = state.copy()
    new_state["reply"] = res.content
    new_state["agent_out"] = AgentFinish(return_values={}, log="")
    return new_state


def router(state):
    print("> router")
    print(dumps(state, pretty=True))
    if state["user_profile"] is None or state["user_profile"] == "":
        return "new_user_flow"
    return "existing_user_flow"


#


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
        graph.add_edge("new_user_flow", "existing_user_flow")
        graph.add_edge("existing_user_flow", END)
        graph.set_conditional_entry_point(
            condition=router,
            conditional_edge_mapping={
                "new_user_flow": "new_user_flow",
                "existing_user_flow": "existing_user_flow",
            },
        )
        self.graph = graph.compile(self.saver)
        self.thread_id = "0"
        self.user_profile = load_user_profile(user_name)

    def user_says(self, message: str) -> str:
        """
        This method is used to pass the user's message to the bot.
        """
        thread = {"configurable": {"thread_id": self.thread_id}}
        res = self.graph.invoke(
            input={
                "input": message,
                "user_name": self.user_name,
                "user_profile": self.user_profile,
            },
            config=thread,
        )
        print(res)
        save_user_profile(self.user_name, res["user_profile"])
        return res["reply"]


if __name__ == "__main__":
    bot = Bot("user")
    bot.user_says("hello")
