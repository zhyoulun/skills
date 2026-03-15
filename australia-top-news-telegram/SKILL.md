---
name: australia-top-news-telegram
description: 获取澳大利亚头部热门新闻，优先使用 ABC News Top Stories，按首页排序选择最多 10 条，写成适合直接发送到 Telegram 的中文摘要，并附上每条新闻的原文链接。
---

# Australia Top News Telegram

## Workflow

1. 请求 `https://www.abc.net.au/news/`，优先把它当作 `ABC News: Top Stories` 首页源。
2. 优先从页面中的 `application/ld+json` 里读取 `CollectionPage` / `ItemList`，按顺序提取最多 10 条新闻链接；如果这个结构不可用，再从页面内的同等首页数据中提取头条列表。
3. 如果 ABC 首页暂时不可用或无法提取出足够的头条，再回退到 `https://news.google.com/rss?hl=en-AU&gl=AU&ceid=AU:en`，并尽量解析到原始媒体链接后再输出。
4. 对每条新闻，读取原文页面，至少拿到：
   - 英文标题
   - 核心摘要或导语
   - 原文链接
5. 按首页顺序保留最多 10 条，写成简洁中文；不要虚构未核实细节。
6. 最终只输出适合发 Telegram 的中文正文，不解释过程，不输出代码块。

## Output Rules

- 开头给一个总标题，例如“澳大利亚热门新闻速览”。
- 每条新闻单独成行或成段，带序号。
- 每条包含：
  - 中文标题或一句话摘要
  - 原文链接
- 总数最多 10 条；如果有效头条不足 10 条，就按实际条数输出。
- 保持简洁，适合手机端阅读。
- 最后一行附来源页：`https://www.abc.net.au/news/`
