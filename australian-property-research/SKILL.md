---
name: australian-property-research
description: 使用浏览器自动化调研澳大利亚房产信息。当你需要查找房产地址、房价、历史成交、区域信息、周边设施时使用此技能。适用场景包括：用户提供具体地址要查询房产详情、查找房产在realestate.com.au或domain.com.au的挂牌信息、验证地址是否存在于Google Maps。
---

# Australian Property Research

## Overview

此技能通过浏览器自动化调研澳大利亚房产信息，完成地址验证、房产挂牌查询、区域信息收集等任务。

## Workflow Decision Tree

```
用户请求调研房产
        │
        ▼
是否提供具体地址？
        │
   YES  │  NO
    │   │   └── 请求提供具体地址
    ▼
Google Maps 验证地址
        │
        ▼
地址存在？
        │
   YES  │  NO
    │   │   └── 报告地址无法验证
    ▼
搜索 realestate.com.au
        │
        ▼
找到挂牌信息？
        │
   YES  │  NO
    │   │   └── 尝试 domain.com.au
    ▼   ▼
报告调研结果
```

## Step 1: 地址验证 (Google Maps)

使用 Playwright 连接到 `http://127.0.0.1:9222` 的共享浏览器会话：

```javascript
const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.connectOverCDP('http://127.0.0.1:9222');
  const context = browser.contexts()[0] || await browser.newContext();
  const page = context.pages()[0] || await context.newPage();
  
  // 格式化地址用于搜索
  const address = '26A Yattenden Crescent, Baulkham Hills NSW 2153';
  const encodedAddress = encodeURIComponent(address);
  
  await page.goto(`https://www.google.com/maps/search/${encodedAddress}`);
  await page.waitForTimeout(2000);
  
  console.log('URL:', page.url());
  console.log('Title:', page.title());
  
  const bodyText = await page.evaluate(() => document.body.innerText);
  console.log('Content preview:', bodyText.substring(0, 500));
  
  process.exit(0);
})().catch(err => { console.error(err); process.exit(1); });
```

**验证要点**：
- 检查页面 URL 是否包含原始搜索词
- 从页面文本中提取地址显示结果
- 确认 "100 米" 或类似距离比例尺出现表示地图已加载

## Step 2: 搜索 RealEstate.com.au

```javascript
const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.connectOverCDP('http://127.0.0.1:9222');
  const context = browser.contexts()[0] || await browser.newContext();
  const page = context.pages()[0] || await context.newPage();
  
  // 格式化地址为 realestate.com.au URL 格式
  const address = '26a-yattenden-crescent-baulkham-hills-nsw-2153';
  
  await page.goto(`https://www.realestate.com.au/property/${address}`);
  await page.waitForTimeout(3000);
  
  console.log('URL:', page.url());
  console.log('Title:', await page.title());
  
  const bodyText = await page.evaluate(() => document.body.innerText);
  
  // 检查是否 404
  if (bodyText.includes('off the market') || bodyText.includes('404')) {
    console.log('STATUS: Property may be off market');
  } else {
    console.log('Content:', bodyText.substring(0, 2000));
  }
  
  process.exit(0);
})().catch(err => { console.error(err); process.exit(1); });
```

**URL 格式化规则**：
- 全小写
- 空格用连字符替换
- 街道类型完整拼写 (Crescent → Crescent, Street → Street)
- 删除所有标点符号

## Step 3: 备选 Domain.com.au

如果 realestate.com.au 未找到，尝试 domain.com.au：

```javascript
const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.connectOverCDP('http://127.0.0.1:9222');
  const context = browser.contexts()[0] || await browser.newContext();
  const page = context.pages()[0] || await context.newPage();
  
  const address = '26a-yattenden-crescent-baulkham-hills-nsw-2153';
  
  await page.goto(`https://www.domain.com.au/property/${address}`);
  await page.waitForTimeout(3000);
  
  console.log('URL:', page.url());
  console.log('Title:', await page.title());
  
  const bodyText = await page.evaluate(() => document.body.innerText);
  console.log('Content:', bodyText.substring(0, 2000));
  
  process.exit(0);
})().catch(err => { console.error(err); process.exit(1); });
```

## 调研报告模板

完成调研后，按以下结构整理信息：

```markdown
## 房产调研报告

### 地址信息
- **街道地址**: [完整地址]
- ** suburb **: [区]
- **州/邮编**: NSW [邮编]

### Google Maps 验证
- 状态: [验证通过/无法验证]
- 位置截图: [如有]

### 挂牌信息 (RealEstate.com.au)
- 状态: [在售/已售/已下架/未找到]
- 价格: [如有]
- 房型: [如有]
- 其他信息: [如有]

### 备选来源 (Domain.com.au)
- 状态: [找到/未找到]

### 周边设施
- [从 Google Maps 提取的附近设施信息]

### 注意事项
- 该房产可能已下架或成交
- 建议联系当地房产中介获取更多信息
```

## 常见问题

**Q: 页面返回 404 怎么办？**
A: 尝试 domain.com.au 或在 realestate.com.au 使用搜索功能

**Q: 如何获取历史成交价？**
A: 房产已下架后历史数据可能无法在线查询，建议使用 Domain 的成交历史或联系中介

**Q: 页面加载超时？**
A: 增加 waitForTimeout 时间，或先检查网络连接

## Resources

此技能主要依赖浏览器自动化，无需额外的 scripts/references/assets 目录结构。
