from pathlib import Path
from typing import List

from conf import BASE_DIR, LOCAL_CHROME_HEADLESS, LOCAL_CHROME_PATH

SOCIAL_MEDIA_DOUYIN = "douyin"
SOCIAL_MEDIA_TENCENT = "tencent"
SOCIAL_MEDIA_TIKTOK = "tiktok"
SOCIAL_MEDIA_BILIBILI = "bilibili"
SOCIAL_MEDIA_KUAISHOU = "kuaishou"


def get_supported_social_media() -> List[str]:
    return [SOCIAL_MEDIA_DOUYIN, SOCIAL_MEDIA_TENCENT, SOCIAL_MEDIA_TIKTOK, SOCIAL_MEDIA_KUAISHOU]


def get_cli_action() -> List[str]:
    return ["upload", "login", "watch"]


# 统一获取浏览器启动配置（防风控+引入本地浏览器）
def get_browser_options(headless=None):
    args = [
        '--disable-blink-features=AutomationControlled',
        '--lang=zh-CN',
        '--disable-infobars',
    ]
    if headless or (headless is None and LOCAL_CHROME_HEADLESS):
        args.append('--headless=new')
        headless = True
    else:
        args.append('--start-maximized')
        headless = False

    options = {
        'headless': headless,
        'args': args
    }
    # headless 模式用自带 Chromium（彻底无窗口），可见模式用系统 Chrome
    if not headless and LOCAL_CHROME_PATH:
        options['executable_path'] = LOCAL_CHROME_PATH
    return options


async def set_init_script(context):
    stealth_js_path = Path(BASE_DIR / "utils/stealth.min.js")
    await context.add_init_script(path=stealth_js_path)
    return context
