---
name: google-search-scrape
description: 使用 Playwright 从 Google 搜索结果中提取标题和链接。当需要验证 Google 搜索功能是否正常、获取特定关键词的搜索结果、或批量采集搜索结果时使用此技能。
---

# Google 搜索结果抓取

## Overview

通过 Playwright 连接已有的 headful 浏览器会话，访问 Google 搜索并提取指定数量的结果标题和 URL。

## 工作流程

1. **连接浏览器** - 通过 CDP 连接 `http://127.0.0.1:9222`
2. **获取页面** - 从 browser context 获取或创建 page
3. **导航搜索** - 访问 `https://www.google.com/search?q=关键词`
4. **等待加载** - 等待搜索结果区域加载
5. **提取数据** - 提取前 N 条结果的标题和链接
6. **输出退出** - 打印结果并正常退出

## 关键要点

- **选择器**: Google 搜索结果的选择器是 `.g`（不是 `div.g`），每条结果的标题在 `h3` 元素中
- **等待策略**: 先 `waitForSelector('.g')` 或使用固定延时 `waitForTimeout(3000)`
- **CDP 连接**: 必须使用 `chromium.connectOverCDP()`，不能使用 `browser.pages()`
- **退出**: 成功时 `process.exit(0)`，失败时 `process.exit(1)`

## 示例脚本

```javascript
const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.connectOverCDP('http://127.0.0.1:9222');
  const context = browser.contexts()[0] || await browser.newContext();
  const page = context.pages()[0] || await context.newPage();

  const query = '霍尔木兹';
  await page.goto(`https://www.google.com/search?q=${encodeURIComponent(query)}`, { timeout: 30000 });
  await page.waitForTimeout(3000);

  const results = await page.evaluate(() => {
    const items = document.querySelectorAll('.g');
    const data = [];
    for (let i = 0; i < Math.min(5, items.length); i++) {
      const item = items[i];
      const titleEl = item.querySelector('h3');
      const linkEl = item.querySelector('a');
      if (titleEl && linkEl) {
        data.push({
          title: titleEl.textContent,
          url: linkEl.href
        });
      }
    }
    return data;
  });

  console.log(`=== Google 搜索结果 (${query}) ===`);
  results.forEach((r, i) => {
    console.log(`${i + 1}. ${r.title}`);
    console.log(`   URL: ${r.url}`);
    console.log('');
  });

  process.exit(0);
})().catch(err => {
  console.error('Error:', err.message);
  process.exit(1);
});
```

## 常见问题

| 问题 | 解决方案 |
|------|----------|
| 结果为空 | 检查 `.g` 选择器数量，可能是页面未完全加载，增加 `waitForTimeout` |
| 连接失败 | 确认 headful 浏览器正在运行且端口 9222 可访问 |
| 选择器错误 | Google 使用 `.g` 类名（非 `div.g`），先检查 `document.querySelectorAll('.g').length` |
