import asyncio
import sqlite3
import traceback

from patchright.async_api import async_playwright

from myUtils.auth import check_cookie
from utils.base_social_media import set_init_script, get_browser_options
import uuid
from pathlib import Path
from conf import BASE_DIR


# 抖音登录
async def douyin_cookie_gen(id, status_queue):
    url_changed_event = asyncio.Event()
    async def on_url_change():
        if page.url != original_url:
            url_changed_event.set()
    async with async_playwright() as playwright:
        options = get_browser_options()
        browser = await playwright.chromium.launch(**options)
        context = await browser.new_context()
        context = await set_init_script(context)
        page = await context.new_page()
        try:
            await page.goto("https://creator.douyin.com/")
            original_url = page.url
            img_locator = page.get_by_role("img", name="二维码")
            src = await img_locator.get_attribute("src")
            print("✅ 图片地址:", src)
            status_queue.put(src)

            page.on('framenavigated',
                    lambda frame: asyncio.create_task(on_url_change()) if frame == page.main_frame else None)

            try:
                await asyncio.wait_for(url_changed_event.wait(), timeout=200)
                print("监听页面跳转成功")
            except asyncio.TimeoutError:
                print("监听页面跳转超时")
                status_queue.put("500")
                return

            uuid_v1 = uuid.uuid1()
            print(f"UUID v1: {uuid_v1}")
            cookies_dir = Path(BASE_DIR / "cookiesFile")
            cookies_dir.mkdir(exist_ok=True)
            await context.storage_state(path=cookies_dir / f"{uuid_v1}.json")
            result = await check_cookie(3, f"{uuid_v1}.json")
            if not result:
                status_queue.put("500")
                return

            with sqlite3.connect(Path(BASE_DIR / "db" / "database.db")) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO user_info (type, filePath, userName, status)
                    VALUES (?, ?, ?, ?)
                ''', (3, f"{uuid_v1}.json", id, 1))
                conn.commit()
                print("✅ 用户状态已记录")
            status_queue.put("200")
        except Exception as e:
            print(f"❌ 抖音登录异常: {e}")
            traceback.print_exc()
            status_queue.put("500")
        finally:
            await page.close()
            await context.close()
            await browser.close()


# 视频号登录
async def get_tencent_cookie(id, status_queue):
    url_changed_event = asyncio.Event()
    async def on_url_change():
        if page.url != original_url:
            url_changed_event.set()

    async with async_playwright() as playwright:
        options = get_browser_options()
        browser = await playwright.chromium.launch(**options)
        context = await browser.new_context()
        context = await set_init_script(context)
        page = await context.new_page()
        try:
            await page.goto("https://channels.weixin.qq.com")
            original_url = page.url

            page.on('framenavigated',
                    lambda frame: asyncio.create_task(on_url_change()) if frame == page.main_frame else None)

            # 等待 iframe 出现（最多等 60 秒）
            iframe_locator = page.frame_locator("iframe").first
            img_locator = iframe_locator.get_by_role("img").first
            src = await img_locator.get_attribute("src")
            print("✅ 图片地址:", src)
            status_queue.put(src)

            try:
                await asyncio.wait_for(url_changed_event.wait(), timeout=200)
                print("监听页面跳转成功")
            except asyncio.TimeoutError:
                status_queue.put("500")
                print("监听页面跳转超时")
                return

            uuid_v1 = uuid.uuid1()
            print(f"UUID v1: {uuid_v1}")
            cookies_dir = Path(BASE_DIR / "cookiesFile")
            cookies_dir.mkdir(exist_ok=True)
            await context.storage_state(path=cookies_dir / f"{uuid_v1}.json")
            result = await check_cookie(2, f"{uuid_v1}.json")
            if not result:
                status_queue.put("500")
                return

            with sqlite3.connect(Path(BASE_DIR / "db" / "database.db")) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO user_info (type, filePath, userName, status)
                    VALUES (?, ?, ?, ?)
                ''', (2, f"{uuid_v1}.json", id, 1))
                conn.commit()
                print("✅ 用户状态已记录")
            status_queue.put("200")
        except Exception as e:
            print(f"❌ 视频号登录异常: {e}")
            traceback.print_exc()
            status_queue.put("500")
        finally:
            await page.close()
            await context.close()
            await browser.close()


# 快手登录
async def get_ks_cookie(id, status_queue):
    url_changed_event = asyncio.Event()
    async def on_url_change():
        if page.url != original_url:
            url_changed_event.set()
    async with async_playwright() as playwright:
        options = get_browser_options()
        browser = await playwright.chromium.launch(**options)
        context = await browser.new_context()
        context = await set_init_script(context)
        page = await context.new_page()
        try:
            await page.goto("https://cp.kuaishou.com")
            await page.get_by_role("link", name="立即登录").click()
            await page.get_by_text("扫码登录").click()
            img_locator = page.get_by_role("img", name="qrcode")
            src = await img_locator.get_attribute("src")
            original_url = page.url
            print("✅ 图片地址:", src)
            status_queue.put(src)

            page.on('framenavigated',
                    lambda frame: asyncio.create_task(on_url_change()) if frame == page.main_frame else None)

            try:
                await asyncio.wait_for(url_changed_event.wait(), timeout=200)
                print("监听页面跳转成功")
            except asyncio.TimeoutError:
                status_queue.put("500")
                print("监听页面跳转超时")
                return

            uuid_v1 = uuid.uuid1()
            print(f"UUID v1: {uuid_v1}")
            cookies_dir = Path(BASE_DIR / "cookiesFile")
            cookies_dir.mkdir(exist_ok=True)
            await context.storage_state(path=cookies_dir / f"{uuid_v1}.json")
            result = await check_cookie(4, f"{uuid_v1}.json")
            if not result:
                status_queue.put("500")
                return

            with sqlite3.connect(Path(BASE_DIR / "db" / "database.db")) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO user_info (type, filePath, userName, status)
                    VALUES (?, ?, ?, ?)
                ''', (4, f"{uuid_v1}.json", id, 1))
                conn.commit()
                print("✅ 用户状态已记录")
            status_queue.put("200")
        except Exception as e:
            print(f"❌ 快手登录异常: {e}")
            traceback.print_exc()
            status_queue.put("500")
        finally:
            await page.close()
            await context.close()
            await browser.close()


# 小红书登录
async def xiaohongshu_cookie_gen(id, status_queue):
    url_changed_event = asyncio.Event()

    async def on_url_change():
        if page.url != original_url:
            url_changed_event.set()

    async with async_playwright() as playwright:
        options = get_browser_options()
        browser = await playwright.chromium.launch(**options)
        context = await browser.new_context()
        context = await set_init_script(context)
        page = await context.new_page()
        try:
            await page.goto("https://creator.xiaohongshu.com/")
            await page.locator('img.css-wemwzq').click()

            img_locator = page.get_by_role("img").nth(2)
            src = await img_locator.get_attribute("src")
            original_url = page.url
            print("✅ 图片地址:", src)
            status_queue.put(src)

            page.on('framenavigated',
                    lambda frame: asyncio.create_task(on_url_change()) if frame == page.main_frame else None)

            try:
                await asyncio.wait_for(url_changed_event.wait(), timeout=200)
                print("监听页面跳转成功")
            except asyncio.TimeoutError:
                status_queue.put("500")
                print("监听页面跳转超时")
                return

            uuid_v1 = uuid.uuid1()
            print(f"UUID v1: {uuid_v1}")
            cookies_dir = Path(BASE_DIR / "cookiesFile")
            cookies_dir.mkdir(exist_ok=True)
            await context.storage_state(path=cookies_dir / f"{uuid_v1}.json")
            result = await check_cookie(1, f"{uuid_v1}.json")
            if not result:
                status_queue.put("500")
                return

            with sqlite3.connect(Path(BASE_DIR / "db" / "database.db")) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO user_info (type, filePath, userName, status)
                    VALUES (?, ?, ?, ?)
                ''', (1, f"{uuid_v1}.json", id, 1))
                conn.commit()
                print("✅ 用户状态已记录")
            status_queue.put("200")
        except Exception as e:
            print(f"❌ 小红书登录异常: {e}")
            traceback.print_exc()
            status_queue.put("500")
        finally:
            await page.close()
            await context.close()
            await browser.close()
