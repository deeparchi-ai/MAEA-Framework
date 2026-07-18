#!/usr/bin/env python3
"""Record animation.html at 1080x1920, 30fps, 25 seconds."""
from playwright.sync_api import sync_playwright
import os

HTML_PATH = os.path.expanduser("~/projects/MAEA-Framework/demo/animation.html")
OUTPUT = os.path.expanduser("~/projects/MAEA-Framework/demo/animation-video.mp4")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(
        viewport={"width": 1080, "height": 1920},
        record_video_dir=os.path.dirname(OUTPUT),
        record_video_size={"width": 1080, "height": 1920},
    )
    page = context.new_page()
    
    # Remove the __timelines mock so CSS animations run freely
    page.goto(f"file://{HTML_PATH}")
    page.evaluate("delete window.__timelines")
    
    # Wait for full animation (25s)
    page.wait_for_timeout(26000)  # 26s with buffer
    
    video_path = page.video.path()
    page.close()
    context.close()
    browser.close()
    
    # Rename to target
    os.rename(video_path, OUTPUT)
    print(f"Done: {OUTPUT}")
