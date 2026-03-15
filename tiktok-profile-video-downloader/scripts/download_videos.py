#!/usr/bin/env python3
"""
TikTok Profile Video Downloader
下载 TikTok 用户主页最新的 10 个视频。
使用 yt-dlp。
用法: python scripts/download_videos.py --username <用户名> 或 --url <主页URL>
"""

import argparse
import os
import subprocess

def download_videos(username=None, url=None):
    if not username and not url:
        raise ValueError("必须提供 username 或 url")
    if username:
        url = f"https://www.tiktok.com/@{username}/videos"
    os.makedirs("videos", exist_ok=True)
    cmd = [
        "yt-dlp",
        url,
        "--playlist-end", "10",
        "-o", "videos/%(uploader)s_%(upload_date)s_%(title)s.%(ext)s",
        "--write-thumbnail",
        "--embed-subs",
    ]
    subprocess.run(cmd, check=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="下载 TikTok 个人主页最新 10 视频")
    parser.add_argument("--username", help="TikTok 用户名")
    parser.add_argument("--url", help="TikTok 主页 URL")
    args = parser.parse_args()
    try:
        download_videos(args.username, args.url)
        print("下载完成！视频保存在 videos/ 文件夹。")
    except Exception as e:
        print(f"错误: {e}")
