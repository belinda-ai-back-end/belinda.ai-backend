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
        with open("curators.json", "r") as f:
            self.json_dict = json.load(f)
        self.link = 'https://www.submithub.com/curators'

    def parse_one_curator(self, curator_soup: BeautifulSoup):
        name = curator_soup.find("h5", class_="bold mrg-top-05").text
        links_el = curator_soup.find("div", class_="small blog-links inline-stats")
        facebook_link = re.findall(r'https?://.{0,5}facebook.com/[^"]{1,100}"', str(links_el))
        facebook_link = facebook_link[0][:-1] if len(facebook_link) > 0 else None
        spotify_link = re.findall(r'https://open.spotify.com/user/[^"]{1,100}"', str(links_el))
        spotify_link = spotify_link[0][:-1] if len(spotify_link) > 0 else None
        instagram_link = re.findall(r'https://.{0,5}instagram.com/[^"]{1,100}"', str(links_el))
        instagram_link = instagram_link[0][:-1] if len(instagram_link) > 0 else None
        tiktok_link = re.findall(r'https://.{0,5}tiktok.com/@[^"]{1,100}"', str(links_el))
        tiktok_link = tiktok_link[0][:-1] if len(tiktok_link) > 0 else None
        twitter_link = re.findall(r'https://.{0,5}twitter.com/[^"]{1,100}"', str(links_el))
        twitter_link = twitter_link[0][:-1] if len(twitter_link) > 0 else None
        youtube_link = re.findall(r'https://.{0,5}youtube.com/[^"]{1,100}"', str(links_el))
        youtube_link = youtube_link[0][:-1] if len(youtube_link) > 0 else None
        apple_music_link = re.findall(r'https://music.apple.com/[^"]{1,100}"', str(links_el))
        apple_music_link = apple_music_link[0][:-1] if len(apple_music_link) > 0 else None
        mixcloud_link = re.findall(r'https://.{0,5}mixcloud.com/[^"]{1,100}"', str(links_el))
        mixcloud_link = mixcloud_link[0][:-1] if len(mixcloud_link) > 0 else None
        twitch_link = re.findall(r'https://.{0,5}twitch.tv/[^"]{1,100}"', str(links_el))
        twitch_link = twitch_link[0][:-1] if len(twitch_link) > 0 else None
        hello_text = curator_soup.find("em", class_="mrg-right-05")
        hello_text = hello_text.text if hello_text is not None else None

        if name not in self.json_dict:
            self.json_dict[name] = {
                "name": name,
                "desc": hello_text,
                "facebook_link": facebook_link,
                "spotify_link": spotify_link,
                "instagram_link": instagram_link,
                "tiktok_link": tiktok_link,
                "twitter_link": twitter_link,
                "youtube_link": youtube_link,
                "apple_music_link": apple_music_link,
                "mixcloud_link": mixcloud_link,
                "twitch_link": twitch_link,
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
