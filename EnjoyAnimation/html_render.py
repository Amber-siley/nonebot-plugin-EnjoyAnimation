import re
from playwright.async_api import async_playwright
from os import path
from .variable import(
    animation_pic_path
)

async def text_to_img(text: str):
    '''html文字转图片
    - text：html文本或者字符串'''
    text=re.sub(r"\n","<br>",text)
    async with async_playwright() as p:
        browser =await p.chromium.launch()
        context =await browser.new_context(viewport=p.devices['iPhone 12']['viewport'], user_agent=p.devices['iPhone 12']['user_agent'])
        page =await context.new_page()
        content =f'<div id="capture">' + text + '</div>'
        await page.set_content(content)
        ele =await page.query_selector("#capture")
        box =await  ele.bounding_box()
        await page.screenshot(path=path.join(animation_pic_path,"text_pic.jpg"), clip=box,full_page=True)
        await browser.close()