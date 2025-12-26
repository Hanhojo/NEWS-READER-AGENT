import time
from typing import Type

from crewai_tools import SerperDevTool
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

from pydantic import BaseModel, Field

search_tool = SerperDevTool(n_results=30)


class ScrapeToolInput(BaseModel):
    url: str = Field(..., description="URL to scrape")



try:
    from crewai.tools import BaseTool
except Exception:
    # (혹시 crewai.tools에 없으면 이걸로 시도)
    from crewai_tools import BaseTool  # type: ignore


class ScrapeTool(BaseTool):
    name: str = "scrape_tool"
    description: str = (
        "Use this when you need to read the content of a website. "
        "Returns the cleaned text content, or 'No content' on failure."
    )
    args_schema: Type[BaseModel] = ScrapeToolInput

    def _run(self, url: str) -> str:
        print(f"Scraping URL: {url}")

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()

                page.goto(url, wait_until="domcontentloaded", timeout=30_000)
                page.wait_for_timeout(2000)

                html = page.content()
                browser.close()

            soup = BeautifulSoup(html, "html.parser")

            unwanted_tags = [
                "header", "footer", "nav", "aside", "script", "style", "noscript", "iframe",
                "form", "button", "input", "select", "textarea", "img", "svg", "canvas",
                "audio", "video", "embed", "object",
            ]
            for tag in soup.find_all(unwanted_tags):
                tag.decompose()

            content = " ".join(soup.get_text(separator=" ").split())
            return content if content else "No content"

        except Exception as e:
            print(f"Scrape failed: {e}")
            return "No content"



scrape_tool = ScrapeTool()