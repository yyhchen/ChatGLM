"""Password-protected Chainlit demonstration.

Set CHAINLIT_AUTH_USERNAME and CHAINLIT_AUTH_PASSWORD before running this
example. The demonstration intentionally refuses all logins when either value
is absent so that credentials are never committed to the repository.
"""

import hmac
import os

import chainlit as cl
from openai import AsyncOpenAI


AUTH_USERNAME = os.getenv("CHAINLIT_AUTH_USERNAME")
AUTH_PASSWORD = os.getenv("CHAINLIT_AUTH_PASSWORD")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "http://127.0.0.1:8080/v1")
DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "Qwen2-0.5B-Instruct")

client = (
    AsyncOpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL)
    if OPENAI_API_KEY
    else None
)

cl.instrument_openai()

settings = {
    "max_tokens": 512,
    "temperature": 0.1,
    "top_p": 0.9,
}


@cl.password_auth_callback
def auth_callback(username: str, password: str):
    if not AUTH_USERNAME or not AUTH_PASSWORD:
        return None

    if hmac.compare_digest(username, AUTH_USERNAME) and hmac.compare_digest(
        password, AUTH_PASSWORD
    ):
        return cl.User(
            identifier=username,
            metadata={"role": username, "provider": "credentials"},
        )
    return None


@cl.set_starters
async def set_starters():
    return [
        cl.Starter(
            label="早晨例行程序构想",
            message="你能帮我创建一个个性化的早晨例行程序吗？先问我现在的习惯和能带来活力的活动。",
            icon="/public/idea.svg",
        ),
        cl.Starter(
            label="像五岁小孩一样解释超导体",
            message="像对五岁小孩解释一样简单地说明什么是超导体。",
            icon="/public/learn.svg",
        ),
        cl.Starter(
            label="用于每日邮件报告的 Python 脚本",
            message="编写一个 Python 脚本来自动化发送每日邮件报告，并指导我如何设置。",
            icon="/public/terminal.svg",
        ),
    ]


@cl.set_chat_profiles
async def chat_profile():
    return [
        cl.ChatProfile(
            name="Qwen2-0.5B-Instruct",
            markdown_description="由配置的 OpenAI 兼容服务提供。",
            icon="/public/qwen.png",
        ),
        cl.ChatProfile(
            name="Qwen2-72B-Instruct",
            markdown_description="由配置的 OpenAI 兼容服务提供。",
            icon="/public/qwen.png",
        ),
        cl.ChatProfile(
            name="Gemma2",
            markdown_description="由配置的 OpenAI 兼容服务提供。",
            icon="/public/google.png",
        ),
        cl.ChatProfile(
            name="Phi-3",
            markdown_description="由配置的 OpenAI 兼容服务提供。",
            icon="/public/microsoft.png",
        ),
        cl.ChatProfile(
            name="Llama3",
            markdown_description="由配置的 OpenAI 兼容服务提供。",
            icon="/public/meta.png",
        ),
    ]


@cl.on_chat_start
async def on_chat_start():
    if client is None:
        message = "未设置 OPENAI_API_KEY。请设置 API Key 后重新启动此认证示例。"
        cl.user_session.set("setup_error", message)
        await cl.Message(content=message).send()
        return

    user = cl.user_session.get("user")
    identifier = user.identifier if user else "user"
    await cl.Message(content=f"Hello {identifier}").send()
    cl.user_session.set("setup_error", None)
    cl.user_session.set(
        "message_history",
        [{"role": "system", "content": "You are a helpful assistant."}],
    )


@cl.on_message
async def main(message: cl.Message):
    if setup_error := cl.user_session.get("setup_error"):
        await cl.Message(content=setup_error).send()
        return

    if client is None:
        await cl.Message(content="聊天客户端尚未初始化。").send()
        return

    message_history = cl.user_session.get("message_history", [])
    message_history.append({"role": "user", "content": message.content})
    model = cl.user_session.get("chat_profile") or DEFAULT_MODEL

    response_message = cl.Message(content="")
    await response_message.send()

    try:
        stream = await client.chat.completions.create(
            model=model,
            messages=message_history,
            stream=True,
            **settings,
        )
        async for part in stream:
            if token := part.choices[0].delta.content or "":
                await response_message.stream_token(token)
    except Exception as error:
        response_message.content = f"模型请求失败：{type(error).__name__}。请检查服务地址、模型名和密钥。"
        await response_message.update()
        return

    message_history.append({"role": "assistant", "content": response_message.content})
    await response_message.update()
