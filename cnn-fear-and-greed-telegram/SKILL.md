---
name: cnn-fear-and-greed-telegram
description: 获取 CNN Fear & Greed Index 最新值。优先使用 CNN 的数据接口 https://production.dataviz.cnn.io/index/fearandgreed/graphdata，而不是解析页面 DOM。最终输出适合直接发送到 Telegram 的简洁中文正文。
---

# CNN Fear & Greed Telegram

## Workflow

1. 请求 `https://production.dataviz.cnn.io/index/fearandgreed/graphdata`。
2. 使用浏览器风格请求头；必要时带上：
   - `Referer: https://edition.cnn.com/markets/fear-and-greed`
   - `Origin: https://edition.cnn.com`
   - 常见桌面浏览器 `User-Agent`
3. 读取 JSON 中 `fear_and_greed` 对象的这些字段：
   - `score`
   - `rating`
   - `timestamp`
   - `previous_close`
   - `previous_1_week`
   - `previous_1_month`
   - `previous_1_year`
4. 将 `score` 四舍五入为整数；将 `rating` 整理成自然可读文本。
5. 最终只输出适合发 Telegram 的简洁中文正文，不解释过程，不输出代码块。

## Output Rules

- 第一行直接给出 Fear & Greed Index 数值和 rating。
- 包含更新时间。
- 包含 `previous_close`、`1w`、`1m`、`1y`。
- 最后一行附上来源页面：`https://edition.cnn.com/markets/fear-and-greed`
