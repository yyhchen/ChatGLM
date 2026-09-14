# LangChain RAG 问答案例

本目录聚焦“本地模型 + 文档检索 + 向量库”的 RAG 教学。不同文件记录了 ChatGLM 历史实验、Qwen2 问答、流式 Gradio UI、对话式 RAG 和 Agent 尝试；它们是相互独立的实验入口。

## 案例地图

| 文件 | 内容 | 是否推荐作为首入口 |
| --- | --- | --- |
| Qwen_QA_Stream.py | Qwen2、本地法规文本、bge-m3、Chroma 和 Gradio 的完整 RAG UI | 是 |
| Qwen_QA_demo.ipynb | Qwen RAG 的 Notebook 演示 | 可作为 Qwen_QA_Stream.py 的配套阅读 |
| QA.ipynb | ChatGLM 时代的历史问答实验 | 参考 |
| conversation_rag.ipynb | 带对话上下文的 RAG 尝试 | 进阶 |
| Qwen_agent.ipynb、Qwen_agent_demo.ipynb | Agent 相关实验 | 进阶、版本敏感 |
| custom_llm.py | 自定义 LangChain LLM 类示例 | 不建议直接运行；文件末尾会发起请求 |

## 环境

这是一个依赖 PyTorch、CUDA、Transformers 与 LangChain 版本组合的本地实验。建议使用 Python 3.10 或更新版本，并单独创建环境：

~~~
cd langchain_QA
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
~~~

请根据显卡、CUDA 和操作系统安装合适的 PyTorch 版本。requirements.txt 只描述 Python 包，不包含模型权重、数据集或 GPU 驱动。

## 运行 Qwen Gradio 示例

Qwen_QA_Stream.py 是最完整的独立入口，但其中包含作者机器上的路径。运行前请修改这些变量：

| 变量 | 原用途 | 需要替换为 |
| --- | --- | --- |
| llm_model_path | Qwen2 模型目录 | 本机或挂载的 Qwen Instruct 模型目录 |
| dataset_path | CHLAWS 文本目录 | 自己的 TXT 文档目录 |
| embed_model_path | bge-m3 模型目录 | 本机的嵌入模型目录 |
| device | CUDA 设备 | cuda、cpu 或你的设备策略 |
| persist_directory | Chroma 本地持久化目录 | 可写、可忽略的本地目录 |

准备完成后：

~~~
python3 Qwen_QA_Stream.py
~~~

脚本会加载模型、读取文档、建立 ParentDocumentRetriever，并启动 Gradio 服务。首次建立检索库会占用显存和磁盘；示例会在导入/运行时直接启动 UI，因此不适合作为可复用 Python 模块导入。

## RAG 数据流

Qwen_QA_Stream.py 的关键流程是：

1. 读取法规或自定义 TXT 文档。
2. 同时按父块和子块切分文本。
3. 用 bge-m3 建立 Chroma 向量库。
4. 通过 ParentDocumentRetriever 取回更完整的上下文。
5. 将上下文和问题交给本地 Qwen2。
6. 由 Gradio 流式显示回答。

可先将少量、版权和权限明确的文本放入独立目录验证链路，再扩展到更大数据集。

## 版本与常见问题

- LangChain 0.2 系列：源码使用了该时期的导入路径。若安装最新版后 ImportError，请优先按 requirements.txt 创建隔离环境，而不是与其他案例共用环境。
- 模型路径错误：确认模型目录含有 tokenizer 与权重文件，并检查读权限。
- CUDA 内存不足：缩小模型、降低生成长度、使用量化模型或改为 CPU 进行小样本验证。
- 检索为空：确认 DirectoryLoader 的 glob 与文档扩展名匹配，且数据目录确实含文本。
- Chroma 状态异常：删除自己的 persist_directory 后重新建库；不要删除仓库中已有教学数据。
- Agent 格式报错：custom_llm.py 是协议实验，不保证能直接适配新版 Agent。

## 学习建议

先运行少量文本的 Qwen_QA_Stream.py，理解检索和回答的闭环；再阅读 Notebook 比较不同切分、记忆和 Agent 方案。需要把模型改为远端 OpenAI 兼容服务时，可参考 Chainlit/ 中的配置方式，但请保持两个案例的 Python 环境独立。
