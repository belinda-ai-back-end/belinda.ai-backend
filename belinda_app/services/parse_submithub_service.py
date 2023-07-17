import asyncio
import re
import json
import logging
from time import sleep
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class TaleoJobScraper:
    def __init__(self):
        self.driver = webdriver.Chrome()
        self.driver.set_window_size(1500, 1000)
        self.wait = WebDriverWait(self.driver, 10)
        self.json_dict = {}
        self.link = "https://www.submithub.com/curators"

    async def parse_one_curator(self, curator_soup):
        name = curator_soup.find("h5", class_="bold mrg-top-05").text

        links_el = curator_soup.find("div", class_="small blog-links inline-stats")
        links = links_el.find_all("a")
        social_links = {}

        for link in links:
            href = link.get("href", "")
            social_media = link.text.lower().replace(" ", "_")
            social_links[social_media] = href

        hello_text = curator_soup.find("em", class_="mrg-right-05")
        hello_text = hello_text.text if hello_text else None

        if name not in self.json_dict:
            self.json_dict[name] = {"name": name, "desc": hello_text, **social_links}

    async def scrape(self):
        try:
            self.driver.get(self.link)
            r = re.compile(r"\d+ - \d+ of \d+")
            f = lambda d: re.search(r, d.find_element_by_id("blog-item").text)

            SCROLL_PAUSE_TIME = 1
            last_height = self.driver.execute_script(
                "return document.body.scrollHeight"
            )

            while True:
                self.driver.execute_script(
                    "window.scrollTo(0, document.body.scrollHeight);"
                )
                sleep(SCROLL_PAUSE_TIME)

                soup = BeautifulSoup(self.driver.page_source, "html.parser")
                curators = soup.find_all("div", class_="blog-item")

                for curator in curators:
                    await self.parse_one_curator(curator)

                with open("curators.json", "w") as f:
                    json.dump(self.json_dict, f, indent=4)

                logger.info(f"Total curators scraped: {len(self.json_dict)}")

                new_height = self.driver.execute_script(
                    "return document.body.scrollHeight"
                )
                if new_height == last_height:
                    break
                last_height = new_height

        except Exception as e:
            logger.error(f"An error occurred while scraping: {str(e)}")

        finally:
            self.driver.quit()


async def parse_submithub():
    scraper = TaleoJobScraper()
    await scraper.scrape()


if __name__ == "__main__":
    asyncio.run(parse_submithub())
