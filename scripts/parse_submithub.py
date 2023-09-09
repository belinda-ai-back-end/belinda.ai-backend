import re
import json

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
from time import sleep, time


class TaleoJobScraper(object):
    def __init__(self):
        self.driver = webdriver.Chrome()
        self.driver.set_window_size(1500, 1000)
        self.wait = WebDriverWait(self.driver, 10)
        try:
            with open("curators.json", "r") as f:
                self.json_dict = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.json_dict = {}
        self.link = 'https://www.submithub.com/curators'

    def parse_one_curator(self, curator_soup: BeautifulSoup):
        name = curator_soup.find("h5", class_="bold mrg-top-05").text
        links_el = curator_soup.find("div", class_="small blog-links inline-stats")
        facebookLink = re.findall(r'https?://.{0,5}facebook.com/[^"]{1,100}"', str(links_el))
        facebookLink = facebookLink[0][:-1] if len(facebookLink) > 0 else None
        spotifyLink = re.findall(r'https://open.spotify.com/user/[^"]{1,100}"', str(links_el))
        spotifyLink = spotifyLink[0][:-1] if len(spotifyLink) > 0 else None
        instagramLink = re.findall(r'https://.{0,5}instagram.com/[^"]{1,100}"', str(links_el))
        instagramLink = instagramLink[0][:-1] if len(instagramLink) > 0 else None
        tiktokLink = re.findall(r'https://.{0,5}tiktok.com/@[^"]{1,100}"', str(links_el))
        tiktokLink = tiktokLink[0][:-1] if len(tiktokLink) > 0 else None
        twitterLink = re.findall(r'https://.{0,5}twitter.com/[^"]{1,100}"', str(links_el))
        twitterLink = twitterLink[0][:-1] if len(twitterLink) > 0 else None
        youtubeLink = re.findall(r'https://.{0,5}youtube.com/[^"]{1,100}"', str(links_el))
        youtubeLink = youtubeLink[0][:-1] if len(youtubeLink) > 0 else None
        appleMusicLink = re.findall(r'https://music.apple.com/[^"]{1,100}"', str(links_el))
        appleMusicLink = appleMusicLink[0][:-1] if len(appleMusicLink) > 0 else None
        mixcloudLink = re.findall(r'https://.{0,5}mixcloud.com/[^"]{1,100}"', str(links_el))
        mixcloudLink = mixcloudLink[0][:-1] if len(mixcloudLink) > 0 else None
        twitchLink = re.findall(r'https://.{0,5}twitch.tv/[^"]{1,100}"', str(links_el))
        twitchLink = twitchLink[0][:-1] if len(twitchLink) > 0 else None
        hello_text = curator_soup.find("em", class_="mrg-right-05")
        hello_text = hello_text.text if hello_text is not None else None

        if name not in self.json_dict:
            self.json_dict[name] = {
                "name": name,
                "desc": hello_text,
                "facebookLink": facebookLink,
                "spotifyLink": spotifyLink,
                "instagramLink": instagramLink,
                "tiktokLink": tiktokLink,
                "twitterLink": twitterLink,
                "youtubeLink": youtubeLink,
                "appleMusicLink": appleMusicLink,
                "mixcloudLink": mixcloudLink,
                "twitchLink": twitchLink,
            }

    def scrape(self):
        self.driver.get(self.link)
        r = re.compile(r'\d+ - \d+ of \d+')
        f = lambda d: re.search(r, d.find_element_by_id('blog-item').text)
        sleep(10)
        SCROLL_PAUSE_TIME = 1
        last_height = self.driver.execute_script("return document.body.scrollHeight")

        while True:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            sleep(SCROLL_PAUSE_TIME)

            soup = BeautifulSoup(self.driver.page_source, "html.parser")
            curators = soup.find_all("div", class_="blog-item")
            for curator in curators:
                self.parse_one_curator(curator)

            with open("curators.json", "w") as f:
                json.dump(self.json_dict, f, indent=4)

            print(len(self.json_dict))

            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        self.driver.quit()


if __name__ == '__main__':
    scraper = TaleoJobScraper()
    start_time = time()
    scraper.scrape()
    end_time = time()
    execution_time = end_time - start_time
    print(f"Парсинг кураторов завершен за {execution_time:.2f} секунд.")
