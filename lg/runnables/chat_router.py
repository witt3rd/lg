"""Bionic bot"""

from langchain_core.messages import SystemMessage
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_openai import ChatOpenAI

from .shared import DD_BOILERPLATE

#


llm = ChatOpenAI(temperature=0, streaming=True, model="gpt-4-turbo")


class ChatRouter(BaseModel):
    """Call this if you are able to route the user to the appropriate representative."""

    choice: str = Field(description="should be one of: user, workflow")


chat_router_system_message = f"""
{DD_BOILERPLATE}

You should interact tersely with them to try to figure out how you can route their message:

- User understanding: learn about the user, inform them of what you have learned about them, adapt to their styles and preferences. Call the router with `user`
- Workflows: your main job is to offload tasks from the user.  You do this with workflows.  If the user is asking about creating, updating, performing, or the status of a task or workflow, then call the router with `workflow`

Ask youself: is the user message about the user?  something the like, something they've done or want to do (aspirations), dreams, experiences, preferences, etc.?  If so, then route to user understanding ('user').
Otherwise, if the user message is not about themselves (user understanding) or about tasks (workflows), then respond directing them to one of these topics.
"""


def get_messages(messages):
    return [SystemMessage(content=chat_router_system_message)] + messages


chat_router_chain = get_messages | llm.bind_tools([ChatRouter])
