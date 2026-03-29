const { chromium } = require('playwright');

/**
 * Google 搜索结果抓取脚本
 * 用法: node google_search.js "关键词" [数量]
 * 默认返回 5 条结果
 */

const query = process.argv[2] || '霍尔木兹';
const limit = parseInt(process.argv[3]) || 5;

(async () => {
  const browser = await chromium.connectOverCDP('http://127.0.0.1:9222');
  const context = browser.contexts()[0] || await browser.newContext();
  const page = context.pages()[0] || await context.newPage();

  console.log(`正在搜索: ${query}`);
  await page.goto(`https://www.google.com/search?q=${encodeURIComponent(query)}`, { timeout: 30000 });
  await page.waitForTimeout(3000);

  const results = await page.evaluate((n) => {
    const items = document.querySelectorAll('.g');
    const data = [];
    for (let i = 0; i < Math.min(n, items.length); i++) {
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
  }, limit);

  console.log(`\n=== Google 搜索结果 (${query}) ===`);
  if (results.length === 0) {
    console.log('未找到结果或页面加载失败');
  } else {
    results.forEach((r, i) => {
      console.log(`${i + 1}. ${r.title}`);
      console.log(`   URL: ${r.url}`);
      console.log('');
    });
  }

  process.exit(0);
})().catch(err => {
  console.error('Error:', err.message);
  process.exit(1);
});
