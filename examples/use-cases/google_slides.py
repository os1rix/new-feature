import os
import sys

from browser_use.browser.context import BrowserContext
from pydantic import SecretStr

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import asyncio

import pyperclip
from dotenv import load_dotenv
# from langchain_openai import ChatOpenAI
from langchain_deepseek import ChatDeepSeek

from browser_use import ActionResult, Agent, Controller
from browser_use.browser.browser import Browser, BrowserConfig

browser = Browser(
	config=BrowserConfig(
		browser_binary_path="C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
	),
)

load_dotenv()
api_key = os.getenv('DEEPSEEK_API_KEY', '')
if not api_key:
	raise ValueError('DEEPSEEK_API_KEY is not set')


controller = Controller()


def is_google_slide(page) -> bool:
	return page.url.startswith('https://docs.google.com/presentation/')


@controller.registry.action('Google Slides: Open a slides presentation')
async def open_google_slide(browser: BrowserContext, google_slide_url: str):
	page = await browser.get_current_page()
	if page.url != google_slide_url:
		await page.goto(google_slide_url)
		await page.wait_for_load_state()
	if not is_google_slide(page):
		return ActionResult(error='Failed to open Google Slides, are you sure you have permissions to access this presenation?')
	return ActionResult(extracted_content=f'Opened Google Slides {google_slide_url}', include_in_memory=False)

async def main():
		model = ChatDeepSeek(
			model='deepseek-chat',
			api_key=SecretStr(api_key),
		)

		agent = Agent(
			task="""
				go to google slides: https://docs.google.com/presentation/d/1hUeZ-tsSRbi4bTu0f9ZcrRF-rzMp599FJ9rL91XdOEI/edit?slide=id.p#slide=id.p
			""",
			llm=model,
			browser=browser,
			controller=controller,
			use_vision=False,
			enable_memory=False
		)
		await agent.run()

if __name__ == '__main__':
	asyncio.run(main())
