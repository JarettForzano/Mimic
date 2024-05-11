import asyncio
from playwright.async_api import async_playwright, Playwright
from playwright._impl._errors import TimeoutError

async def run(playwright: Playwright, search):
    chromium = playwright.chromium
    browser = await chromium.launch()
    page = await browser.new_page()
    await page.goto("https://www.google.com")
    
    try:
        # Wait for the search input field to appear
        await page.get_by_title('Search').fill(search)  # Fill the search input with the query
        await page.get_by_role("button", name="Google Search").press("Enter")  # Press Enter to initiate the search
        
        # Wait for the search results to load
        await page.wait_for_load_state("networkidle")
        await page.screenshot(path="screenshot.png", full_page=True)

        search_results = await page.query_selector_all('div#search div.g a')
        links = []
        for result in search_results[:10]:
            href = await result.get_attribute("href")
            links.append(href)
            print(href)
    except TimeoutError:
        print("Timeout occurred while waiting for the search input field.")


    await browser.close()

async def main():
    async with async_playwright() as playwright:
        await run(playwright, "What are the top 10 healthiest foods?")

asyncio.run(main())
