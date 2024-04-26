"""Bionic bot"""

import operator
import os
from typing import Annotated, TypedDict, Union

from dotenv import load_dotenv
from langchain_core.agents import AgentAction, AgentFinish
from langchain_core.load import dumps
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import END, StateGraph

from .tool_registry import ToolRegistry

#

load_dotenv()
DB_DIR = os.getenv("DB_DIR", "./.db")

#

llm = ChatOpenAI(temperature=0, streaming=True, model="gpt-4-turbo")


class ChatRouter(BaseModel):
    """Call this if you are able to route the user to the appropriate representative."""

    choice: str = Field(description="should be one of: user, workflow")


system_message = """
You are a `digital double` of the user.  You are an extension and reflection of the user.

You should interact tersely with them to try to figure out how you can route their message:

- User understanding: learn about the user, inform them of what you have learned about them, adapt to their styles and preferences. Call the router with `user`
- Workflows: your main job is to offload tasks from the user.  You do this with workflows.  If the user is asking about creating, updating, performing, or the status of a task or workflow, then call the router with `workflow`

Ask youself: is the user message about the user?  something the like, something they've done or want to do (aspirations), dreams, experiences, preferences, etc.?  If so, then route to user understanding ('user').
Otherwise, if the user message is not about themselves (user understanding) or about tasks (workflows), then respond directing them to one of these topics.
"""


def get_messages(messages):
    return [SystemMessage(content=system_message)] + messages


chat_router_chain = get_messages | llm.bind_tools([ChatRouter])

#


def load_user_profile(user_name: str) -> str | None:
    path = os.path.join(DB_DIR, f"{user_name}.txt")
    if os.path.exists(path):
        with open(path, "r") as f:
            return f.read()


def save_user_profile(user_name: str, user_profile: str) -> None:
    path = os.path.join(DB_DIR, f"{user_name}.txt")
    with open(path, "w") as f:
        f.write(user_profile)


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
