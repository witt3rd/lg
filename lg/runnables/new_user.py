"""Bionic bot"""

from langchain.prompts import PromptTemplate
from langchain.schema import StrOutputParser
from langchain_community.chat_models.litellm import ChatLiteLLM

from .shared import DD_BOILERPLATE

#


llm = ChatLiteLLM(
    model="groq/Llama3-70b-8192",
    max_tokens=1000,
)


new_user_system_message = f"""
{DD_BOILERPLATE}

You are just meeting {{user_name}} for the first time.

Tell them what your role is and how you can help them.

You can also ask them about their role and how you can help them by offloading tasks and workflows.
"""

prompt = PromptTemplate.from_template(new_user_system_message)


new_user_chain = prompt | llm | StrOutputParser()

if __name__ == "__main__":
    print(new_user_chain.invoke({"user_name": "John"}))
