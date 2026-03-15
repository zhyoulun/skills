import os
import sys
import re
import httpx
from bs4 import BeautifulSoup
from markdownify import markdownify as md

def download_image(url, folder):
    if not os.path.exists(folder):
        os.makedirs(folder, exist_ok=True)
    
    # 获取图片后缀或默认png
    ext = ".png"
    if "wx_fmt=" in url:
        ext = "." + url.split("wx_fmt=")[1].split("&")[0]

    name = "img_" + str(abs(hash(url))) + ext
    path = os.path.join(folder, name)
    
    try:
        resp = httpx.get(url, follow_redirects=True)
        if resp.status_code == 200:
            with open(path, "wb") as f:
                f.write(resp.content)
            return path
    except Exception as e:
        print(f"Failed to download {url}: {e}")
    return url

def convert_wechat_to_md(url, output_dir="output"):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    }
    resp = httpx.get(url, headers=headers)
    soup = BeautifulSoup(resp.text, 'html.parser')
    
    # 获取标题
    title_tag = soup.find('h1', class_='rich_media_title')
    title = title_tag.get_text(strip=True) if title_tag else "untitled"
    
    content = soup.find('div', id='js_content')
    
    # 提取并替换图片
    img_dir = os.path.join(output_dir, "images")
    if content:
        for img in content.find_all('img'):
            src = img.get('data-src') or img.get('src')
            if src:
                local_path = download_image(src, img_dir)
                if local_path.startswith(output_dir):
                    img['src'] = os.path.relpath(local_path, output_dir)
    
    markdown_text = md(str(content)) if content else ""
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    safe_title = re.sub(r'[\\/:*?"<>|]', '_', title)
    filename = os.path.join(output_dir, f"{safe_title}.md")
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"# {title}\n\n")
        f.write(markdown_text)
    
    return filename

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python convert.py <url>")
    else:
        file = convert_wechat_to_md(sys.argv[1])
        print(f"Markdown created: {file}")
