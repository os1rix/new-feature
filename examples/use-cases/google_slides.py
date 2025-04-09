import os
import sys

from browser_use.browser.context import BrowserContext

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import asyncio

import pyperclip
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

from browser_use import ActionResult, Agent, Controller
from browser_use.browser.browser import Browser, BrowserConfig

browser = Browser(
	config=BrowserConfig(
		browser_binary_path='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
	),
)

# Load environment variables
load_dotenv()
if not os.getenv('OPENAI_API_KEY'):
	raise ValueError('OPENAI_API_KEY is not set. Please add it to your environment variables.')


controller = Controller()


def is_google_slide(page) -> bool:
	return page.url.startswith('https://docs.google.com/presentation/')


@controller.registry.action('Google Slides: Open a slides presentation')
async def open_google_slide(browser: BrowserContext, google_sheet_url: str):
	page = await browser.get_current_page()
	if page.url != google_sheet_url:
		await page.goto(google_sheet_url)
		await page.wait_for_load_state()
	if not is_google_slide(page):
		return ActionResult(error='Failed to open Google Slides, are you sure you have permissions to access this presenation?')
	return ActionResult(extracted_content=f'Opened Google Slides {google_sheet_url}', include_in_memory=False)

async def main():
	async with await browser.new_context() as context:
		model = ChatOpenAI(model='gpt-4o')

		agent = Agent(
			task="""
				task placeholder
			""",
			llm=model,
			browser_context=context,
			controller=controller,
		)
		await agent.run()

if __name__ == '__main__':
	asyncio.run(main())
