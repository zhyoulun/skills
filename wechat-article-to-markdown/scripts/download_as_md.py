import requests
from bs4 import BeautifulSoup
import markdownify
import sys
import re

def download_wechat_article(url, output_file):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
        'Referer': 'https://mp.weixin.qq.com/'
    }
    
    try:
        # 1. 获取 HTML
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        html = response.text
        
        # 2. 解析 HTML
        soup = BeautifulSoup(html, 'html.parser')
        
        # 定位正文容器
        content_div = soup.find('div', id='js_content')
        if not content_div:
            # 备用选择器
            content_div = soup.find('div', class_='rich_media_content')
        
        if not content_div:
            print("错误：未能找到文章正文内容 (#js_content)。")
            return

        # 3. 处理图片懒加载 (data-src -> src)
        for img in content_div.find_all('img'):
            if img.get('data-src'):
                img['src'] = img['data-src']
            # 微信图片通常带有额外样式或固定宽度，可以在这里根据需要过滤
            
        # 4. 获取标题
        title_tag = soup.find('h1', class_='rich_media_title')
        title = title_tag.get_text(strip=True) if title_tag else "WeChat Article"
        
        # 5. 转换为 Markdown
        # 移除不需要的脚本和样式标签
        for s in content_div(['script', 'style']):
            s.decompose()
            
        md_content = markdownify.markdownify(str(content_div), heading_style="ATX")
        
        # 组装最终结果
        final_md = f"# {title}\n\n{md_content}"
        
        # 6. 写入文件
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(final_md)
            
        print(f"成功导出: {output_file}")
        
    except Exception as e:
        print(f"转换失败: {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python download_as_md.py <url> <output_file>")
    else:
        download_wechat_article(sys.argv[1], sys.argv[2])
