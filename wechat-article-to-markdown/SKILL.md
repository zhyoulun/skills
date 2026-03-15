---
name: wechat-article-to-markdown
description: 下载微信公众号文章并将其转换为清洁的 Markdown 格式。该技能会自动处理微信的懒加载图片（data-src 转换为 src），模拟浏览器请求以绕过简单的反爬虫机制，并提取文章正文内容。
---

# WeChat Article to Markdown

## Overview
此技能用于将微信公众号文章网页转换为标准的 Markdown 文件。它解决了直接抓取微信文章时常见的图片不显示（由于 `data-src` 懒加载）和反爬拦截问题。

## Workflow Decision Tree

1. **确认链接**：确保 URL 是以 `mp.weixin.qq.com` 开头的微信公众号文章。
2. **下载与解析**：
   - 使用 `scripts/download_as_md.py` 执行下载任务。
   - 脚本会模拟常用的 `User-Agent`，并设置 `Referer`。
3. **内容转换**：
   - 定位 `js_content`（文章主体）。
   - 将 `<img>` 标签中的 `data-src` 替换为 `src`。
   - 使用 `markdownify` 将 HTML 转换为 Markdown。
4. **保存结果**：将内容保存为 `.md` 文件。

## Usage Example

```bash
# 示例：通过调用脚本下载并转换
python3 scripts/download_as_md.py "https://mp.weixin.qq.com/s/xxxxxx" "output.md"
```

## Resources

### scripts/
- `download_as_md.py`: 核心转换逻辑脚本。

### references/
- `selectors.md`: 记录微信文章常用的 HTML 选择器（如 `#js_content`, `.rich_media_content`）。
