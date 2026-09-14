# 新闻日报案例

本目录是一组彼此独立、可以组合运行的新闻爬虫教学案例。它们共同演示了：抓取公开新闻页面、清洗结构化内容、可选地调用兼容 OpenAI SDK 的大模型生成摘要，以及用静态网页读取当天生成的 JSON 数据。

> 这些示例用于学习与本地实验。请遵守目标网站的服务条款、robots 规则和访问频率限制；不要将 API 密钥提交到仓库。

## 案例地图

| 案例 | 新闻来源 | 主入口 | 静态阅读页 | 主要学习点 |
| --- | --- | --- | --- | --- |
| AI 日报 | AIbase AI 新闻 | `ai_daily_briefing/ai_daily_news.py` | `ai_daily_briefing/reading.html` | `crawl4ai` 异步抓取、按年月归档、摘要生成 |
| 汽车日报 | 汽车之家新闻 | `car_daily_briefing/car_news_crawler.py` | `car_daily_briefing/car_news_reader.html` | `requests` 抓取、重试与反爬延时、摘要生成 |
| 财经日报 | 新浪财经股票频道 | `finance_daily_briefing/financial_news_crawler.py` | `finance_daily_briefing/financial_news_reader.html` | 结构化新闻抓取、重试与摘要生成 |
| 统一调度与阅读 | 上述三个案例 | `run_all_news_crawlers.py` | `integrated_news_reader.html` | 串行调度多个任务、统一查看产物 |

`example.py`、`testllm.py` 和 Notebook 是补充实验材料，不是上述主流程的启动入口。

## 环境与安装

建议使用 Python 3.10 或更高版本，并在仓库根目录执行：

```bash
python3 -m venv .venv
source .venv/bin/activate  # Windows PowerShell: .venv\\Scripts\\Activate.ps1
python3 -m pip install -r "app case/requirements.txt"
```

AI 日报依赖 `crawl4ai` 的浏览器运行时。首次安装后，如该库提示缺少浏览器组件，按其安装提示运行 `crawl4ai-setup`（或该版本对应的浏览器安装命令）后再重试。汽车和财经案例不需要浏览器运行时。

## 外部服务与密钥

三个主爬虫都会访问各自源码中声明的公开新闻站点；网络不可用、页面结构变更、频率限制或站点反爬机制都可能导致抓取结果减少或失败。

摘要功能使用代码中配置的 OpenAI SDK 兼容服务：`https://api.longcat.chat/openai`，模型为 `LongCat-Flash-Chat`。运行时从环境变量 `MEITUAN_API_KEY` 读取密钥：

```bash
export MEITUAN_API_KEY="你的密钥"
```

也可以在**启动命令所在目录**创建 `.env`，内容如下：

```dotenv
MEITUAN_API_KEY=你的密钥
```

未设置该变量时，爬虫会跳过或降级摘要生成；抓取仍可能完成，但阅读页中的摘要不会是模型生成的结果。`testllm.py` 是单独的智谱 API 连通性实验，需要使用它时另行提供 `ZHIPU_API_KEY`。

## 独立运行三个案例

从仓库根目录执行以下命令。每个脚本都会把当天数据写入各自目录下的 `data/json/YYYY/MM/`；AI 日报还会写入 `data/txt/YYYY/MM/` 的摘要文本，汽车和财经日报会写入对应的 TXT 归档。

```bash
python3 "app case/ai_daily_briefing/ai_daily_news.py"
python3 "app case/car_daily_briefing/car_news_crawler.py"
python3 "app case/finance_daily_briefing/financial_news_crawler.py"
```

AI 日报也可使用便捷脚本：

```bash
cd "app case/ai_daily_briefing"
bash auto_run.sh
```

该脚本会检测当天的 `data/json/YYYY/MM/YYYY_MM_DD.json` 和 `data/txt/YYYY/MM/YYYY_MM_DD_news_data.txt`，需要时重新生成，然后尝试启动 `live-server`。若选择这条方式，请预先安装 Node.js，并提供 `live-server`（全局安装）或可用的 `npx`。不想安装 Node.js 时，使用下文的 Python HTTP 服务即可。

## 统一调度

下列脚本会按 AI、汽车、财经的顺序依次运行三个爬虫，并在任务之间等待 60 秒，以降低摘要 API 的并发压力：

```bash
python3 "app case/run_all_news_crawlers.py"
```

它会依次运行所有案例，因此耗时和外部请求量都会高于单独运行一个案例。首次学习建议先分别运行并查看单个输出。

## 在浏览器中查看结果

阅读页通过浏览器的 `fetch()` 读取 JSON，不能可靠地直接双击以 `file://` 方式打开；请从 `app case` 目录启动一个 HTTP 服务：

```bash
cd "app case"
python3 -m http.server 8000
```

然后在浏览器访问：

- `http://localhost:8000/ai_daily_briefing/reading.html`
- `http://localhost:8000/car_daily_briefing/car_news_reader.html`
- `http://localhost:8000/finance_daily_briefing/financial_news_reader.html`
- `http://localhost:8000/integrated_news_reader.html`

阅读页按本机当天日期推导路径。如果当天尚未生成数据、系统日期与数据日期不同，或 HTTP 服务不是从 `app case` 目录启动，页面会显示找不到数据。

## 推荐学习顺序

1. 先运行一个汽车或财经日报，观察抓取、JSON 输出和静态阅读页的关系。
2. 学习 AI 日报的 `asyncio` 与 `crawl4ai` 异步抓取流程。
3. 配置 `MEITUAN_API_KEY`，比较有无摘要服务时的输出。
4. 最后运行统一调度和综合阅读页，理解多个独立案例如何协作。
