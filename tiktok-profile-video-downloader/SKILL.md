---
name: tiktok-profile-video-downloader
description: 从 TikTok 个人主页下载最新的 10 条视频。输入用户名或主页 URL，自动下载 MP4 视频和缩略图到 videos/ 文件夹。依赖 yt-dlp 和 ffmpeg。
---

# TikTok 个人主页视频下载器

## 概述

从指定 TikTok 用户的主页下载最新的 10 个视频，支持无水印下载（如果可用）。视频保存为 MP4，带缩略图。

## 快速开始

1. 确保安装 yt-dlp: `pip install yt-dlp`
2. 安装 ffmpeg（用于视频处理）
3. 运行: `python scripts/download_videos.py --username <用户名>`
   示例: `python scripts/download_videos.py --username jarvisai`

## 参数
- `--username`: TikTok 用户名 (e.g. jarvisai)
- `--url`: 完整主页 URL (e.g. https://www.tiktok.com/@jarvisai)

## 输出
- videos/ 文件夹中: 用户名_日期_标题.mp4
- 对应的 .jpg 缩略图

## 注意
- yt-dlp 会自动处理播放列表，按最新排序。
- 如遇限速，使用 `--limit-rate` 等 yt-dlp 参数自定义。
- 无需登录，支持公开主页。

## 故障排除
- 更新 yt-dlp: `yt-dlp -U`
- 如失败，检查网络或用户名拼写。

## 资源
- [yt-dlp GitHub](https://github.com/yt-dlp/yt-dlp)
- scripts/download_videos.py
