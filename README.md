# LLM Application 教学案例集

这是一个围绕主流大模型应用的教学与实验仓库。每个目录都尽量保持为**独立案例**：它们可以使用不同的模型、服务地址、依赖版本和数据集，不需要也不应被强行合并成一个单体应用。

仓库内容覆盖 RAG、GraphRAG、Agent、多模态对话、文生图和新闻日报自动化。部分示例依赖本地 GPU、OpenAI 兼容服务或第三方 API；请先阅读对应目录的 README，再安装环境或运行代码。

## 从哪里开始

1. 根据下方学习地图选择一个案例。
2. 为该案例单独创建虚拟环境，避免旧版 LangChain、AutoGen 或 GraphRAG 互相影响。
3. 复制案例提供的配置模板，填写自己的服务地址和密钥；不要提交真实配置、模型或运行数据。
4. 先运行最小入口，再扩展到 RAG、Agent 或批量任务。

仓库自身不托管大模型权重，也不自动启动 vLLM、FastChat、GraphRAG Server 或 Neo4j。

## 学习地图

| 推荐顺序 | 目录 | 学习主题 | 主要入口 | 外部条件 | 状态 |
| --- | --- | --- | --- | --- | --- |
| 1 | [Chainlit/](Chainlit/README.md) | OpenAI 兼容聊天、流式输出、RAG、Agent、多模态 UI | app.py、multi_chat.py | 本地/远端模型服务；部分模式还需向量、GraphRAG 或视觉服务 | 综合教学案例 |
| 2 | [langchain_QA/](langchain_QA/README.md) | 本地模型 + Chroma 的 RAG 问答 | Qwen_QA_Stream.py | Qwen、bge-m3、法规/自有文本、通常需要 CUDA | 版本敏感 |
| 3 | [AutoGen/](AutoGen/README.md) | 多 Agent、工具调用、代码执行与 AutoGen RAG | Jupyter Notebooks | OpenAI 兼容模型服务；代码执行需受控环境 | 包含 legacy 与 0.4 两条路径 |
| 4 | [GraphRAG/](GraphRAG/README.md) | 图谱构建、全局/局部检索、Neo4j 可视化 | GraphRAG CLI 与 Notebooks | 聊天/嵌入服务，索引通常需要较高显存 | 实验性、版本敏感 |
| 5 | [app case/](app%20case/README.md) | 新闻抓取、LLM 摘要、静态日报阅读 | 三个爬虫与 run_all_news_crawlers.py | 网络访问与 MEITUAN_API_KEY（摘要可选） | 可独立运行的应用案例 |
| - | [debug/](debug/README.md) | 调试草稿与历史验证 | 无固定入口 | 作者机路径/旧依赖可能需要替换 | 参考材料 |

## 案例之间的关系

- Chainlit/ 是 UI 与交互案例集，目录内有多个独立示例；根目录推荐的主展示入口是 multi_chat.py。
- langchain_QA/ 是单独的 Gradio RAG 教程，并不依赖 Chainlit。
- GraphRAG/ 保存索引数据、Notebook 与 Neo4j 展示说明；服务端与模型需由学习者自行启动。
- AutoGen/ 以 Notebook 为主，legacy PyAutoGen 与 AutoGen 0.4 使用不同包结构，应隔离环境。
- app case/ 的 AI、汽车、财经日报可以分别运行，也可以由统一调度脚本串行执行。
- debug/ 和 assets/ 不是正式应用入口。

## 推荐的环境习惯

~~~
python3 -m venv .venv
source .venv/bin/activate
~~~

Windows PowerShell 可使用 .venv\Scripts\Activate.ps1。随后只安装当前案例 README 指定的依赖，而不是一次性安装整个仓库。

配置文件、.env、爬取数据和向量库均被忽略。示例配置中的地址、模型名和 token 只是占位符；请替换为自己的服务。运行涉及网络搜索、网页抓取或代码执行的案例前，请确认目标网站规则、密钥权限和隔离策略。

## 快速入口

### Chainlit 多模式聊天

~~~
cd Chainlit
python3 -m pip install -r requirements-minimal.txt
cp config.example.json config.json
chainlit run multi_chat.py -w
~~~

随后按 Chainlit/README.md 配置所需的模型服务。只想体验基础流式聊天时运行 chainlit run app.py -w。

多模式聊天界面与功能演示：

![Chainlit 多模式聊天界面](/assets/multi_chat1.png)

![Chainlit 多模式聊天功能演示](/assets/multi_chat1.gif)

图文对话示例：

![Chainlit 图文对话演示](/assets/multi_chat2.gif)

### 新闻日报

~~~
python3 -m pip install -r "app case/requirements.txt"
export MEITUAN_API_KEY="你的密钥"
python3 "app case/ai_daily_briefing/ai_daily_news.py"
~~~

完整说明、HTTP 阅读页和统一调度命令见 [app case/README.md](app%20case/README.md)。

AI 日报阅读器演示：

![AI 日报阅读器演示](/assets/ai_info_show.gif.gif)

## 静态检查

不启动模型、不访问 API 的情况下，可运行：

~~~
python3 scripts/check_examples.py
~~~

该脚本验证教学文档、Chainlit 配置模板以及 Python 文件的语法。它不替代对真实模型服务、网页来源或 GPU 环境的端到端测试。

## 约定与贡献

- 新增案例请优先提供：学习目标、前置条件、最小依赖、配置模板、运行命令和预期效果。
- 不要提交 API Key、真实配置、模型权重、爬取产物或本机路径。
- 如示例依赖特定历史版本，请在该目录 README 中注明，并标记为“版本敏感”。
- 保持案例独立；复用文档模板和检查脚本即可，不要求共享运行环境。
