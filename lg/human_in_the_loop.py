import json
from typing import Literal

from dotenv import load_dotenv
from langchain import hub
from langchain.agents import create_openai_tools_agent
from langchain.load.dump import dumps
from langchain_community.tools.ddg_search.tool import DuckDuckGoSearchRun
from langchain_core.messages import FunctionMessage, HumanMessage
from langchain_core.messages.base import BaseMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import END, MessageGraph
from langgraph.prebuilt import ToolInvocation

#

load_dotenv()

#

tools = [DuckDuckGoSearchRun()]

# tool_executor = ToolExecutor(tools)

# We will set streaming=True so that we can stream tokens
# See the streaming section for more information on this.
llm = ChatOpenAI(temperature=0, streaming=True)

prompt = hub.pull("hwchase17/openai-functions-agent")

query_agent_runnable = create_openai_tools_agent(llm=llm, tools=tools, prompt=prompt)
# functions = [convert_to_openai_function(t) for t in tools]
# llm = llm.bind_functions(functions)
# model = model.bind_tools(tools)

inputs = {"input": "what are EHI embeddings?", "intermediate_steps": []}
agent_out = query_agent_runnable.invoke(inputs)
print(dumps(agent_out, pretty=True))


# Define the function that determines whether to continue or not
def should_continue(messages) -> Literal["end"] | Literal["continue"]:
    last_message = messages[-1]
    print(f"should_continue: {dumps(last_message, pretty=True)}")
    # If there is no function call, then we finish
    if "tool_calls" not in last_message.additional_kwargs:
        return "end"
    # Otherwise if there is, we continue
    return "continue"


# Define the function that calls the model
def call_model(messages) -> BaseMessage:
    print(f"call_model: {dumps(messages, pretty=True)}")
    response = llm.invoke(messages)
    print(f"call_model response: {dumps(response, pretty=True)}")
    # We return a list, because this will get added to the existing list
    return response


# Define the function to execute tools
def call_tool(messages) -> FunctionMessage:
    # Based on the continue condition
    # we know the last message involves a function call
    last_message = messages[-1]
    print(f"call_tool: {dumps(last_message, pretty=True)}")
    # We construct an ToolInvocation from the function_call
    tool_calls = last_message.additional_kwargs["tool_calls"]

    action = ToolInvocation(
        tool=tool_calls[0]["function"]["name"],
        tool_input=json.loads(tool_calls[0]["function"]["arguments"]),
    )
    # We call the tool_executor and get back a response
    response = tool_executor.invoke(action)
    print(f"Response: {dumps(response, pretty=True)}")
    # We use the response to create a FunctionMessage
    function_message = FunctionMessage(content=str(response), name=action.tool)
    # We return a list, because this will get added to the existing list
    return function_message


# Define a new graph
workflow = MessageGraph()

# Define the two nodes we will cycle between
workflow.add_node("agent", call_model)
workflow.add_node("action", call_tool)

# Set the entrypoint as `agent`
# This means that this node is the first one called
workflow.set_entry_point("agent")

# We now add a conditional edge
workflow.add_conditional_edges(
    # First, we define the start node. We use `agent`.
    # This means these are the edges taken after the `agent` node is called.
    "agent",
    # Next, we pass in the function that will determine which node is called next.
    should_continue,
    # Finally we pass in a mapping.
    # The keys are strings, and the values are other nodes.
    # END is a special node marking that the graph should finish.
    # What will happen is we will call `should_continue`, and then the output of that
    # will be matched against the keys in this mapping.
    # Based on which one it matches, that node will then be called.
    {
        # If `tools`, then we call the tool node.
        "continue": "action",
        # Otherwise we finish.
        "end": END,
    },
)

# We now add a normal edge from `tools` to `agent`.
# This means that after `tools` is called, `agent` node is called next.
workflow.add_edge("action", "agent")


thread = {"configurable": {"thread_id": "2"}}


def send_message(message: str) -> str:
    memory = SqliteSaver.from_conn_string(":memory:")

    # Finally, we compile it!
    # This compiles it into a LangChain Runnable,
    # meaning you can use it as you would any other runnable
    app = workflow.compile(checkpointer=memory, interrupt_before=["action"])

    inputs = [HumanMessage(content=message)]
    while True:
        for event in app.stream(inputs, thread):
            for v in event.values():
                print(f"Debug: {v}")
                finish_reason = v.response_metadata.get("finish_reason")
                if finish_reason == "stop":
                    return v.content
        inputs = None


if __name__ == "__main__":

    def ask(message: str) -> None:
        answer = send_message(message)
        print(f"--> {answer}")

    ask("hi! I'm bob")
    ask("what is my name?")
    ask("what's the weather in sf now?")
    ask("What is MSFT stock price?")
