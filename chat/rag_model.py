import os
import json
import openai
from dotenv import load_dotenv, find_dotenv

_ = load_dotenv(find_dotenv())
openai.api_key = os.environ.get("OPEN_API_KEY")
from langchain_openai import ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.tools.retriever import create_retriever_tool
from langchain_core.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
    HumanMessagePromptTemplate,
)
from langchain_core.messages import SystemMessage
from langchain.memory import ConversationBufferMemory
from langchain_core.agents import AgentActionMessageLog, AgentFinish
from langchain.agents.format_scratchpad import format_to_openai_function_messages
from langchain.agents import AgentExecutor

from .response import Response


class RAG:
    def __init__(self):
        self.persist_directory_derm = "Chroma/derma"
        self.embedding = OpenAIEmbeddings()
        
        self.vectordb_derm = Chroma(
            persist_directory=self.persist_directory_derm,
            embedding_function=self.embedding,
        )
        self.derm_retriever = self.vectordb_derm.as_retriever()
        self.memory = ConversationBufferMemory(memory_key="chat_history")
        self.llm = ChatOpenAI(model="gpt-3.5-turbo-0125", temperature=0)
        self.initial_mem = []

        self.llm_final = self.bind_tools()
        self.prompt_final = self.define_prompt()
        self.agent_final = (
                {
                    "input": lambda x: x["input"],
                    # Format agent scratchpad from intermediate steps
                    "chat_history": lambda x: x["chat_history"],
                    "agent_scratchpad": lambda x: format_to_openai_function_messages(
                        x["intermediate_steps"]
                    ),
                }
                | self.prompt_final
                | self.llm_final
                | self.parse
            )
        self.tools_final = self.defined_tools()
        self.agent_executor = AgentExecutor(tools=[self.tools_final], agent=self.agent_final, verbose=True)
        
        
    def defined_tools(self):
        tool = create_retriever_tool(
            self.derm_retriever,
            "derm_retriever",
            "Searches and returns information related to dermatological diseases and other related information",
        )
        return tool

    def define_prompt(self):
        prompt = ChatPromptTemplate.from_messages(
            [
                SystemMessage(
                    content="""You are a professional dermatologist. You will be provided with \
            patient's input query based on which your goal is to generate \
            response as accurately as possible based on the context provided.\
            The user may ask a follow up question for which you can access the chat history \
            to answer the follow up based on what they have previously asked you.
            If you don't know the answer, just say that you don't know."""
                ),
                MessagesPlaceholder(variable_name="chat_history"),
                HumanMessagePromptTemplate.from_template("{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ]
        )
        return prompt

    def parse(self, output):
        # If no function was invoked, return to user
        if "function_call" not in output.additional_kwargs:
            print("no function")
            return AgentFinish(
                return_values={"output": output.content}, log=output.content
            )

        # Parse out the function call
        function_call = output.additional_kwargs["function_call"]
        print(output.additional_kwargs)
        name = function_call["name"]
        inputs = json.loads(function_call["arguments"])

        # If the Response function was invoked, return to the user with the function inputs
        if name == "Response":
            print("tool name: ", name)
            return AgentFinish(return_values=inputs, log=str(function_call))
        # Otherwise, return an agent action
        else:

            return AgentActionMessageLog(
                tool=name, tool_input=inputs, log="", message_log=[output]
            )

    def bind_tools(self):
        tools = self.defined_tools()
        llm_with_tools = self.llm.bind_functions([tools, Response])
        return llm_with_tools
    
    def manage_memory(self, memory, query, response):
        memory.save_context({"input": f"{query}"}, {"output": f"{response}"})


