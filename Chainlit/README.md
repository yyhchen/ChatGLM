# Chainlit 教学案例

本目录不是单一应用，而是一组围绕 Chainlit 和 OpenAI 兼容接口的独立教学示例。推荐先运行基础聊天，再进入多模式聊天、Agent 挂载和认证示例。

## 案例地图

| 文件 | 学习目标 | 启动方式 | 前置条件 |
| --- | --- | --- | --- |
| app.py | 最小流式聊天、聊天 Profile 和会话历史 | chainlit run app.py -w | OpenAI 兼容聊天服务、config.json |
| multi_chat.py | RAG、Agent、GraphRAG、文生图、图文对话的统一 UI | chainlit run multi_chat.py -w | 依所选模式启动对应服务、config.json |
| my_cl_app.py | 每会话独立的 LangChain Agent | 由 main.py 挂载 | 模型 API、网络搜索、LangChain Hub |
| main.py | FastAPI 挂载 Chainlit 的最小示例 | uvicorn main:app --reload | my_cl_app.py 的前置条件 |
| test.py | 使用环境变量的认证聊天示例 | chainlit run test.py -w | 认证变量与模型 API |

多模式聊天是根目录 README 推荐的主展示入口。它不会启动模型或 GraphRAG 服务，而是调用你已经启动的兼容接口。

## 环境

建议使用 Python 3.10 或更新版本，并为本目录单独创建环境：

~~~
cd Chainlit
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements-minimal.txt
~~~

Windows PowerShell 激活命令为 .venv\Scripts\Activate.ps1。

- requirements-minimal.txt 是当前教学入口的最小依赖集合。
- requirements.txt 是历史完整冻结环境，体积较大；只有需要复现实验时再使用。
- 本目录需要外部模型服务时，请在另一个终端或独立环境中启动它。

安装完成后，可以运行 `chainlit hello` 验证界面：

![Chainlit Hello 演示](../assets/chainlit_hello.png)

## 配置多模式聊天

复制模板，不要直接修改或提交真实配置：

~~~
cp config.example.json config.json
~~~

config.json 与 multi_chat.py、app.py 位于同一目录。基础聊天至少需要以下字段：

| 字段 | 用途 |
| --- | --- |
| BASE_URL | OpenAI 兼容聊天服务地址，例如 http://127.0.0.1:8080/v1 |
| API_KEY | 本地服务 token 或提供商密钥 |
| MODEL_ID | 未选择 Profile 时的默认模型名 |

按功能选择性填写：

| 功能 | 额外字段 | 默认服务地址 |
| --- | --- | --- |
| Qwen2-RAG | EMBEDDING_MODEL_NAME、EMBEDDING_BASE_URL，及 data/ 中的 TXT 文档 | 嵌入服务：http://127.0.0.1:8200/v1/embeddings |
| GraphRAG | GRAPHRAG_BASE_URL、API_KEY | http://127.0.0.1:20213/v1 |
| ImageGen | ZHIPU_API_KEY | 智谱图片生成 API |
| InternVL2 | INTERNVL_BASE_URL、INTERNVL_API_KEY、INTERNVL_MODEL_ID | http://127.0.0.1:8081/v1 |

模板中的 token、模型名和地址都只是示例。多模式聊天会在缺少配置、RAG 数据或服务初始化失败时显示下一步提示，而不是继续调用未初始化的客户端。

## 运行入口

### 1. 基础流式聊天

先确保 BASE_URL 指向运行中的兼容服务：

~~~
chainlit run app.py -w
~~~

在页面中选择一个服务实际公开的模型 Profile。若服务只提供一个模型，也可以在 config.json 中设置 MODEL_ID。

基础 OpenAI 兼容聊天示例：

![OpenAI 兼容聊天演示](../assets/chainlit_openaidemo.png)

### 2. 多模式聊天

~~~
chainlit run multi_chat.py -w
~~~

可选模式和教学重点：

- Qwen2：直接调用聊天模型并保存会话历史。
- Qwen2-LC：用 LangChain Runnable 组织提示词与流式输出。
- Qwen2-RAG：本地 TXT 文档切分、嵌入、Chroma 检索和来源展示。
- Agent：聊天模型配合 DuckDuckGo 搜索工具。
- GraphRAG-latest-global / GraphRAG-latest-local：转发到已启动的 GraphRAG 服务。
- ImageGen：调用智谱图片生成。
- InternVL2：上传图片后调用视觉语言模型；该模式只接受图片文件。

RAG 模式会在首次打开该 Profile 时建立检索器。请先创建 Chainlit/data/ 并放入至少一个 TXT 文档；该数据目录被忽略，不会提交到 Git。

### 3. FastAPI 挂载的 Agent 示例

~~~
export OPENAI_API_KEY="你的密钥"
export OPENAI_BASE_URL="https://你的兼容服务/v1"
uvicorn main:app --reload
~~~

访问 http://127.0.0.1:8000/app 可查看 FastAPI 端点，访问 /chainlit 可打开 Agent。my_cl_app.py 会为每个会话分别创建对话记忆和 AgentExecutor，不会共享历史记录。该示例在启动会话时可能访问 LangChain Hub 和 DuckDuckGo。

### 4. 认证聊天示例

~~~
export CHAINLIT_AUTH_USERNAME="demo-user"
export CHAINLIT_AUTH_PASSWORD="强密码"
export OPENAI_API_KEY="你的密钥"
export OPENAI_BASE_URL="http://127.0.0.1:8080/v1"
chainlit run test.py -w
~~~

缺少用户名或密码时，示例会拒绝所有登录，而不会回退到仓库内的固定凭据。

## 本地演示安全提示

当前 .chainlit/config.toml 面向本地教学使用。若将服务暴露给局域网或公网，请至少：

1. 收紧 allow_origins，不要保留任意来源。
2. 根据实际功能收紧上传文件类型、数量和体积。
3. 使用真实身份提供方或安全存储的密码哈希，而非教学示例的环境变量认证。
4. 通过反向代理、TLS 和访问控制保护模型服务与 API Key。

## 常见问题

- 启动后提示缺少 config.json：复制 config.example.json，并填写服务地址与密钥。
- RAG 无法初始化：确认 data/ 中有 TXT 文档，嵌入服务地址可访问，且模型名与服务一致。
- GraphRAG 没有响应：此仓库不包含 GraphRAG Server；请先按 GraphRAG/README.md 启动或配置服务。
- InternVL2 提示文件不支持：该 Profile 只处理图片，上传 PNG、JPEG 等图片文件。
- Agent 初始化失败：检查模型 API、网络、LangChain Hub 和 DuckDuckGo 的可访问性。
