---
name: elon-musk-analyst-v2-fixed
description: 用于抓取、翻译和分析 Elon Musk 在 X (elonmusk) 上的最新动态，涵盖 2026 年的技术和社交背景。
---

# Elon Musk Analyst V2

## Overview
本技能专门用于处理 Elon Musk 的 X 账号 (@elonmusk) 动态。它将原始的推文信息（Raw Tweets）转化为深度报告，包括翻译、背景说明和战略意图分析。

## Workflow

### 1. 访问最新内容 (Accessing Latest Content)
- 动作：使用浏览器工具执行以下脚本以获取实时推文。
  ```javascript
  const page = await context.newPage();
  await page.goto('https://x.com/elonmusk', { waitUntil: 'networkidle' });
  await page.waitForSelector('article[data-testid="tweet"]', { timeout: 10000 });
  const tweets = await page.evaluate(() => {
    return Array.from(document.querySelectorAll('article[data-testid="tweet"]'))
      .slice(0, 3)
      .map(el => ({
        text: el.querySelector('div[data-testid="tweetText"]')?.innerText || "",
        time: el.querySelector('time')?.getAttribute('datetime') || "",
        isRetweet: !!el.querySelector('div[data-testid="socialContext"]')
      }));
  });
  ```
- 重点：抓取时间戳为 2026 年的最新三条博文。

### 2. 内容解析 (Content Parsing)
- **翻译：** 将 Musk 的极简推文翻译为地道中文。
- **分析：** 理财相关性分析

## Usage
- 直接调用脚本抓取 @elonmusk 主页。
