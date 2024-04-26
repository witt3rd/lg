"""Bionic bot"""

import operator
import os
from typing import Annotated, TypedDict, Union

from dotenv import load_dotenv
from langchain_core.agents import AgentAction, AgentFinish
from langgraph.checkpoint.sqlite import SqliteSaver

from .tool_registry import ToolRegistry

#

load_dotenv()
DB_DIR = os.getenv("DB_DIR", "./.db")

#


class BotState(TypedDict):
    input: str
    user_name: str
    bot_out: Union[AgentAction, AgentFinish, None]
    intermediate_steps: Annotated[list[tuple[AgentAction, str]], operator.add]


class Bot:
    """
    The bot class is the main class that will be used to interact with the user.
    """

    def __init__(self, user: str) -> None:
        self.user = user
        self.tool_registry = ToolRegistry()
        self.saver = SqliteSaver.from_conn_string(f"sqlite:///{DB_DIR}/bot.db")
