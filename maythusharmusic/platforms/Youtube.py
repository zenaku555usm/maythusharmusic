import asyncio
import os
import re
import json
from typing import Union
import yt_dlp

from pyrogram.enums import MessageEntityType
from pyrogram.types import Message
from youtubesearchpython.__future__ import VideosSearch

from maythusharmusic.utils.database import is_on_off
from maythusharmusic.utils.formatters import time_to_seconds

import glob
import random
import logging
import requests
import time


# ✅ Configurable constants
API_KEY = "Rf1qda5gyCITj6VbrekzRxmR"
API_BASE_URL = "http://deadlinetech.site"

MIN_FILE_SIZE = 51200

def extract_video_id(link: str) -> str:
    patterns = [
        r'youtube\.com\/(?:embed\/|v\/|watch\?v=|watch\?.+&v=)([0-9A-Za-z_-]{11})',
        r'youtu\.be\/([0-9A-Za-z_-]{11})',
        r'youtube\.com\/(?:playlist\?list=[^&]+&v=|v\/)([0-9A-Za-z_-]{11})',
        r'youtube\.com\/(?:.*\?v=|.*\/)([0-9A-Za-z_-]{11})'
    ]

    for pattern in patterns:
        match = re.search(pattern, link)
        if match:
            return match.group(1)

    raise ValueError("Invalid YouTube link provided.")
    


def api_dl(video_id: str) -> str | None:
    api_url = f"{API_BASE_URL}/download/song/{video_id}?key={API_KEY}"
    file_path = os.path.join("downloads", f"{video_id}.mp3")

    # ✅ Check if already downloaded
    if os.path.exists(file_path):
        print(f"{file_path} already exists. Skipping download.")
        return file_path

    try:
        response = requests.get(api_url, stream=True, timeout=10)

        if response.status_code == 200:
            os.makedirs("downloads", exist_ok=True)
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

            # ✅ Check file size
            file_size = os.path.getsize(file_path)
            if file_size < MIN_FILE_SIZE:
                print(f"Downloaded file is too small ({file_size} bytes). Removing.")
                os.remove(file_path)
                return None

            print(f"Downloaded {file_path} ({file_size} bytes)")
            return file_path

        else:
            print(f"Failed to download {video_id}. Status: {response.status_code}")
            return None

    except requests.RequestException as e:
        print(f"Download error for {video_id}: {e}")
        return None

    except OSError as e:
        print(f"File error for {video_id}: {e}")
        return None





def cookie_txt_file():
    folder_path = f"{os.getcwd()}/cookies"
    filename = f"{os.getcwd()}/cookies/logs.csv"
    txt_files = glob.glob(os.path.join(folder_path, '*.txt'))
    if not txt_files:
        raise FileNotFoundError("No .txt files found in the specified folder.")
    cookie_txt_file = random.choice(txt_files)
    with open(filename, 'a') as file:
        file.write(f'Choosen File : {cookie_txt_file}\n')
    return f"""cookies/{str(cookie_txt_file).split("/")[-1]}"""



async def check_file_size(link):
    async def get_format_info(link):
        proc = await asyncio.create_subprocess_exec(
            "yt-dlp",
            "--cookies", cookie_txt_file(),
            "-J",
            link,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        return downloaded_file, direct
