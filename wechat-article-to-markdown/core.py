from __future__ import annotations

import asyncio
import re
import sys
import os
from pathlib import Path
from datetime import datetime, timezone, timedelta

import httpx
import markdownify
from bs4 import BeautifulSoup
from camoufox.async_api import AsyncCamoufox

# Output configuration
OUTPUT_DIR = Path.cwd() / "output"
IMAGE_CONCURRENCY = 5

def format_timestamp(ts: int) -> str:
    tz = timezone(timedelta(hours=8))
    dt = datetime.fromtimestamp(ts, tz=tz)
    return dt.strftime("%Y-%m-%d %H:%M:%S")

def extract_metadata(soup: BeautifulSoup, html: str) -> dict:
    title_node = soup.select_one("h1.rich_media_title")
    title = title_node.get_text(strip=True) if title_node else ""
    if not title:
        m = re.search(r'var msg_title = "(.*?)"', html)
        if m: title = m.group(1)
    
    author_node = soup.select_one("#js_name")
    author = author_node.get_text(strip=True) if author_node else ""
    
    publish_time = ""
    m = re.search(r'create_time\s*[:=]\s*["\']?(\d+)["\']?', html)
    if m:
        try:
            publish_time = format_timestamp(int(m.group(1)))
        except:
            pass
            
    return {"title": title, "author": author, "publish_time": publish_time}

async def download_image(client: httpx.AsyncClient, img_url: str, img_dir: Path, index: int, semaphore: asyncio.Semaphore) -> tuple[str, str | None]:
    async with semaphore:
        try:
            url = img_url if not img_url.startswith("//") else f"https:{img_url}"
            ext_match = re.search(r"wx_fmt=(\w+)", url) or re.search(r"\.(\w{3,4})(?:\?|$)", url)
            ext = ext_match.group(1) if ext_match else "png"
            filename = f"img_{index:03d}.{ext}"
            filepath = img_dir / filename
            resp = await client.get(url, headers={"Referer": "https://mp.weixin.qq.com/"}, timeout=15.0)
            resp.raise_for_status()
            filepath.write_bytes(resp.content)
            return img_url, f"images/{filename}"
        except Exception:
            return img_url, None

async def download_all_images(img_urls: list[str], img_dir: Path) -> dict[str, str]:
    if not img_urls: return {}
    semaphore = asyncio.Semaphore(IMAGE_CONCURRENCY)
    async with httpx.AsyncClient() as client:
        tasks = [download_image(client, url, img_dir, i + 1, semaphore) for i, url in enumerate(img_urls)]
        results = await asyncio.gather(*tasks)
    return {remote_url: local_path for remote_url, local_path in results if local_path}

def process_content(soup: BeautifulSoup):
    content = soup.select_one("#js_content")
    if not content: return None, [], []
    
    img_urls = []
    for img in content.find_all("img"):
        src = img.get("data-src") or img.get("src")
        if src:
            img_urls.append(src)
            img["src"] = src

    return str(content), [], img_urls

async def convert_article(url: str):
    print(f"Fetching: {url}")
    async with AsyncCamoufox(headless=True) as browser:
        page = await browser.new_page()
        # Set a common User-Agent to further reduce detection
        await page.set_extra_http_headers({"Accept-Language": "zh-CN,zh;q=0.9"})
        await page.goto(url, wait_until="domcontentloaded")
        await asyncio.sleep(3)
        html = await page.content()

    soup = BeautifulSoup(html, "html.parser")
    meta = extract_metadata(soup, html)
    if not meta["title"]:
        print("Failed to extract title. Saving debug HTML.")
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        (OUTPUT_DIR / "debug.html").write_text(html, encoding="utf-8")
        return

    content_html, _, img_urls = process_content(soup)
    md = markdownify.markdownify(content_html)
    
    safe_title = re.sub(r'[/\\?%*:|"<>]', "_", meta["title"])[:80]
    article_dir = OUTPUT_DIR / safe_title
    img_dir = article_dir / "images"
    img_dir.mkdir(parents=True, exist_ok=True)

    url_map = await download_all_images(img_urls, img_dir)
    for remote_url, local_path in url_map.items():
        md = md.replace(remote_url, local_path)

    result = f"# {meta['title']}\n\n> Author: {meta['author']}\n> Time: {meta['publish_time']}\n> Source: {url}\n\n---\n\n{md}"
    (article_dir / f"{safe_title}.md").write_text(result, encoding="utf-8")
    print(f"✅ Saved to: {article_dir / f'{safe_title}.md'}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        asyncio.run(convert_article(sys.argv[1]))
