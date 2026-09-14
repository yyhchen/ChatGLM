"""Basic Chainlit chat demo for an OpenAI-compatible local service."""

import json
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import chainlit as cl
from openai import AsyncOpenAI


CONFIG_PATH = Path(__file__).with_name("config.json")


def load_config() -> Tuple[Dict[str, Any], Optional[str]]:
    """Load local credentials while keeping real configuration out of Git."""
    try:
        with CONFIG_PATH.open("r", encoding="utf-8") as file:
            config = json.load(file)
    except FileNotFoundError:
        return {}, "未找到 config.json。请复制 config.example.json 为 config.json 后再启动。"
    except json.JSONDecodeError as error:
        return {}, f"config.json 不是合法 JSON（第 {error.lineno} 行）。请参考 config.example.json。"

    if not isinstance(config, dict):
        return {}, "config.json 的根节点必须是 JSON 对象。请参考 config.example.json。"

    missing = [key for key in ("API_KEY", "BASE_URL") if not str(config.get(key, "")).strip()]
    if missing:
        return {}, f"config.json 缺少配置项：{', '.join(missing)}。请参考 config.example.json。"

    return config, None


config, CONFIG_ERROR = load_config()
client = (
    AsyncOpenAI(api_key=config["API_KEY"], base_url=config["BASE_URL"])
    if CONFIG_ERROR is None
    else None
)

cl.instrument_openai()

settings = {
    "max_tokens": 512,
    "temperature": 0.1,
    "top_p": 0.9,
}


@cl.set_starters
async def set_starters():
    return [
        cl.Starter(
            label="早晨例行程序构想",
            message="你能帮我创建一个个性化的早晨例行程序吗？这能帮助我在一天中提高生产力。先问我关于我现在的习惯以及哪些活动能在早上给我带来活力。",
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
        cl.Starter(
            label="邀请朋友参加婚礼的短信",
            message="写一条短信，邀请朋友下个月作为我的伴郎参加婚礼。我希望保持非常简短和随意的风格，并提供一个婉拒的选项。",
            icon="/public/write.svg",
        ),
    ]


@cl.set_chat_profiles
async def chat_profile():
    return [
        cl.ChatProfile(
            name="Qwen2-0.5B-Instruct",
            markdown_description="由本地 OpenAI 兼容服务提供的 **Qwen2-0.5B-Instruct**。",
            icon="/public/qwen.png",
        ),
        cl.ChatProfile(
            name="Qwen2-72B-Instruct",
            markdown_description="由本地 OpenAI 兼容服务提供的 **Qwen2-72B-Instruct**。",
            icon="/public/qwen.png",
        ),
        cl.ChatProfile(
            name="glm-4-0520",
            markdown_description="由本地 OpenAI 兼容服务提供的 **glm-4-0520**。",
            icon="/public/google.png",
        ),
        cl.ChatProfile(
            name="GraphRAG-latest-global",
            markdown_description="由兼容服务公开的 GraphRAG 全局查询模型。",
            icon="/public/microsoft.png",
        ),
        cl.ChatProfile(
            name="Llama3",
            markdown_description="由本地 OpenAI 兼容服务提供的 **Llama3**。",
            icon="/public/meta.png",
        ),
    ]


@cl.on_chat_start
async def start_chat():
    if CONFIG_ERROR:
        cl.user_session.set("setup_error", CONFIG_ERROR)
        await cl.Message(content=CONFIG_ERROR).send()
        return

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
        await cl.Message(content="聊天客户端尚未初始化。请检查 config.json 后重试。").send()
        return

    message_history = cl.user_session.get("message_history", [])
    message_history.append({"role": "user", "content": message.content})
    model = cl.user_session.get("chat_profile") or config.get("MODEL_ID")

    if not model:
        await cl.Message(content="未选择模型。请从聊天模式中选择模型，或在 config.json 中设置 MODEL_ID。").send()
        return

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
