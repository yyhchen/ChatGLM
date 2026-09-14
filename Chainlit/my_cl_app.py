"""Per-session LangChain Agent demo for Chainlit.

This example creates a fresh memory and AgentExecutor for every Chainlit
session. It requires an OpenAI-compatible API key and may access LangChain Hub
and DuckDuckGo when the chat starts.
"""

import asyncio
import os
from typing import Optional, Tuple

import chainlit as cl
from langchain import hub
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.memory import ConversationBufferMemory
from langchain_community.tools.ddg_search import DuckDuckGoSearchRun
from langchain_openai import ChatOpenAI


MODEL_NAME = os.getenv("OPENAI_MODEL", "glm-4-airx")
OPENAI_BASE_URL = os.getenv(
    "OPENAI_BASE_URL", "https://open.bigmodel.cn/api/paas/v4/"
)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY")

if LANGCHAIN_API_KEY:
    os.environ["LANGCHAIN_API_KEY"] = LANGCHAIN_API_KEY


def build_agent_executor() -> Tuple[Optional[AgentExecutor], Optional[str]]:
    if not OPENAI_API_KEY:
        return None, "未设置 OPENAI_API_KEY。请设置密钥后重新启动 Agent 示例。"

    try:
        llm = ChatOpenAI(
            temperature=0.95,
            model=MODEL_NAME,
            openai_api_key=OPENAI_API_KEY,
            openai_api_base=OPENAI_BASE_URL,
        )
        tools = [DuckDuckGoSearchRun(max_results=2)]
        prompt = hub.pull("hwchase17/openai-functions-agent")
        memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            output_key="output",
        )
        agent = create_tool_calling_agent(llm=llm, tools=tools, prompt=prompt)
        return AgentExecutor(agent=agent, tools=tools, memory=memory), None
    except Exception as error:
        return (
            None,
            f"Agent 初始化失败：{type(error).__name__}。请检查模型服务、网络和 LangChain Hub 配置。",
        )


@cl.on_chat_start
async def on_chat_start():
    agent_executor, setup_error = build_agent_executor()
    cl.user_session.set("agent_executor", agent_executor)
    cl.user_session.set("setup_error", setup_error)

    if setup_error:
        await cl.Message(content=setup_error).send()
    else:
        await cl.Message(content="Agent 已就绪，可使用网络搜索工具。").send()


@cl.on_message
async def on_message(message: cl.Message):
    if setup_error := cl.user_session.get("setup_error"):
        await cl.Message(content=setup_error).send()
        return

    agent_executor = cl.user_session.get("agent_executor")
    if agent_executor is None:
        await cl.Message(content="Agent 尚未初始化，请重新打开此聊天模式。").send()
        return

    response_message = cl.Message(content="")
    await response_message.send()

    try:
        result = await asyncio.to_thread(
            agent_executor.invoke,
            {"input": message.content},
        )
        answer = result["output"]
    except Exception as error:
        response_message.content = f"Agent 请求失败：{type(error).__name__}。请检查模型服务与网络连接。"
        await response_message.update()
        return

    for character in answer:
        await response_message.stream_token(character)
    await response_message.update()
