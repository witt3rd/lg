#!/usr/bin/env python
"""Example of a chat server with persistence handled on the backend.

For simplicity, we're using file storage here -- to avoid the need to set up
a database. This is obviously not a good idea for a production environment,
but will help us to demonstrate the RunnableWithMessageHistory interface.

We'll use cookies to identify the user. This will help illustrate how to
fetch configuration from the request.
"""

import os
from operator import itemgetter

from dotenv import load_dotenv
from langchain_community.chat_models.litellm import ChatLiteLLM
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

#

load_dotenv()

DB_DIR = os.getenv("DB_DIR", "./.db")

#

llm = ChatLiteLLM(model="groq/Llama3-70b-8192")
output_parser = StrOutputParser()
analysis_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
- Text history analysis reveals personality, behavior, preferences.
- Language use indicates literacy, education, regionality, style complexity, sentence structure.
- Communication skills apparent through message clarity, response length, topic adherence.
- Personality traits inferred from communication style, emoji use, expressiveness.
- Interests, hobbies discernible via discussion topics.
- Emotional state gauged from mood expressions, texting patterns.
- Social network, relationships inferred from contact interactions.
- Cultural background shown through references to customs, festivals.
- Professional, academic interests indicated by specific topic discussions.
- Values, beliefs reflected in topic responses, discussions.
- Behavioral patterns observed in communication timing, responsiveness.
""".strip(),
        ),
        (
            "ai",
            """
Consider the conversation so far:
{messages}

And the user's profile:
{user_profile}

Can you infer anything new about the user that isn't already in the profile?
Indicate your edits to the user profile (add/update/delete).
No narrative, just pure user profile revisions.
""".strip(),
        ),
    ]
)
analysis_chain = analysis_prompt | llm | output_parser

consolidate_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
You are a bullet list editor.  You only respond with edited bullet lists.
""".strip(),
        ),
        (
            "ai",
            """
Consider the original user profile:
{user_profile}

Here are suggested revisions:
{user_profile_revisions}

Generate a new, consolidated user profile based on these revisions.
No narrative, just a bullet list of user profile traits.
""".strip(),
        ),
    ]
)
user_profile_runnable = (
    {
        "user_profile_revisions": analysis_chain,
        "user_profile": itemgetter("user_profile"),
    }
    | consolidate_prompt
    | llm
    | output_parser
)


if __name__ == "__main__":
    user_profile = """
(not provided)
""".strip()
    res = user_profile_runnable.invoke(
        {
            "messages": [
                ("user", "Hi!"),
                ("ai", "Hello! How can I help you today?"),
                (
                    "user",
                    "I need help making a demo for a big tchnical presentation in 1 week!",
                ),
                ("ai", "I can help with that! What are you presenting on?"),
                (
                    "user",
                    "We are starting a new venture in AI using advanced agents as 'digital doubles' of professionals.",
                ),
                (
                    "ai",
                    "That sounds interesting! What kind of help do you need with the demo?",
                ),
                (
                    "user",
                    "I need to show how our agents can be used to automate tasks in a professional setting.",
                ),
                (
                    "ai",
                    "Got it! I can help you with that. What kind of tasks do you want to automate?",
                ),
            ],
            "user_profile": user_profile,
        }
    )

    print(res)
