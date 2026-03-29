#!/usr/bin/env python3

import html
import json
import re
import subprocess
import sys

HOME_URL = "https://www.abc.net.au/news/"
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0 Safari/537.36"
MAX_ITEMS = 10


def fetch_text(url):
    result = subprocess.run(
        [
            "curl",
            "-fsSL",
            "-A",
            USER_AGENT,
            "-H",
            "Accept-Language: en-AU,en;q=0.9",
            url,
        ],
        capture_output=True,
        text=True,
        timeout=20,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError("curl failed for %s: %s" % (url, result.stderr.strip()))
    return result.stdout


def extract_json_ld_objects(raw_html):
    blocks = re.findall(
        r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
        raw_html,
        flags=re.IGNORECASE | re.DOTALL,
    )
    objects = []
    for block in blocks:
        text = html.unescape(block).strip()
        if not text:
            continue
        try:
            objects.append(json.loads(text))
        except json.JSONDecodeError:
            continue
    return objects


def collect_item_list_urls(node):
    urls = []
    if isinstance(node, dict):
        items = node.get("itemListElement")
        if isinstance(items, list):
            for item in items:
                if not isinstance(item, dict):
                    continue
                url = item.get("url")
                if isinstance(url, str) and "/news/" in url:
                    urls.append(url)
        for value in node.values():
            urls.extend(collect_item_list_urls(value))
    elif isinstance(node, list):
        for item in node:
            urls.extend(collect_item_list_urls(item))
    return urls


def collect_article_urls(home_html):
    urls = []
    for obj in extract_json_ld_objects(home_html):
        urls.extend(collect_item_list_urls(obj))

    if not urls:
        urls = re.findall(
            r'https://www\.abc\.net\.au/news/\d{4}-\d{2}-\d{2}/[^"\']+/\d+',
            home_html,
        )

    filtered = []
    seen = set()
    for url in urls:
        if "/live-updates-" in url:
            continue
        if "/live-blog" in url:
            continue
        if url in seen:
            continue
        seen.add(url)
        filtered.append(url)
        if len(filtered) >= MAX_ITEMS:
            break
    return filtered


def find_article_object(node):
    if isinstance(node, dict):
        node_type = node.get("@type")
        if node_type == "NewsArticle":
            return node
        if isinstance(node_type, list) and "NewsArticle" in node_type:
            return node
        for value in node.values():
            found = find_article_object(value)
            if found is not None:
                return found
    elif isinstance(node, list):
        for item in node:
            found = find_article_object(item)
            if found is not None:
                return found
    return None


def first_meta(raw_html, pattern):
    match = re.search(pattern, raw_html, flags=re.IGNORECASE)
    if not match:
        return ""
    return html.unescape(match.group(1)).strip()


def normalize_title(title):
    title = re.sub(r"\s*[-|]\s*ABC News.*$", "", title).strip()
    return title


def extract_article_summary(url):
    raw_html = fetch_text(url)

    for obj in extract_json_ld_objects(raw_html):
        article = find_article_object(obj)
        if article is None:
            continue
        title = normalize_title(str(article.get("headline", "")).strip())
        description = str(article.get("description", "")).strip()
        if title:
            return {
                "title": title,
                "description": description,
                "url": url,
            }

    title = normalize_title(
        first_meta(raw_html, r'<meta[^>]+property=["\']og:title["\'][^>]+content=["\']([^"\']+)["\']')
        or first_meta(raw_html, r"<title>([^<]+)</title>")
    )
    description = first_meta(
        raw_html,
        r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']+)["\']',
    ) or first_meta(
        raw_html,
        r'<meta[^>]+property=["\']og:description["\'][^>]+content=["\']([^"\']+)["\']',
    )
    return {
        "title": title,
        "description": description,
        "url": url,
    }


def main():
    home_html = fetch_text(HOME_URL)
    article_urls = collect_article_urls(home_html)
    articles = []
    for url in article_urls[:MAX_ITEMS]:
        try:
            article = extract_article_summary(url)
        except Exception as err:  # noqa: BLE001
            article = {
                "title": "",
                "description": "failed to fetch article: %s" % err,
                "url": url,
            }
        if article.get("title") or article.get("description"):
            articles.append(article)

    payload = {
        "source": HOME_URL,
        "articles": articles[:MAX_ITEMS],
    }
    json.dump(payload, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
