import pkg_resources
from pkg_resources import DistributionNotFound, VersionConflict
import os

requirements = []
with open("requirements.txt") as f:
    lines = f.readlines()
    for line in lines:
        requirements.append(line)

# checking if all requirements are already satisfied
try:
    try:
        pkg_resources.require(requirements)
    except DistributionNotFound:
        os.system("pip install -r requirements.txt")
    except VersionConflict:
        os.system("pip install -r requirements.txt")
except Exception:
    input("an error occurred while installing requirements, please install them manually.\npress enter to exit.")
    exit()

# clearing screen
try:
    print("\n" * os.get_terminal_size().lines)
except AttributeError:
    print("\n" * 100)
except OSError:
    print("\n" * 100)

import selenium.common
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.by import By
import requests as req
import bs4
import unicodedata
import re
from rich.console import Console
from tqdm import tqdm
import itertools
import threading
import time
import sys

console = Console()

exited = False


def loading_animation():
    for cycle in itertools.cycle(["|", "/", "-", "\\"]):
        if finished:
            break
        else:
            sys.stdout.write(f"\rcollecting images {cycle}")
            sys.stdout.flush()
            time.sleep(0.3)
    sys.stdout.write("\rcollected images   \n     ")


def file_in_path(name, root):
    for count, (base, dirs, files) in enumerate(os.walk(root)):
        if name in files:
            return os.path.join(base, name)
        elif count >= 10000:
            return None


def slugify(value, allow_unicode=False):
    """
    Taken from https://github.com/django/django/blob/master/django/utils/text.py
    Convert to ASCII if 'allow_unicode' is False. Convert spaces or repeated
    dashes to single dashes. Remove characters that aren't alphanumerics,
    underscores, or hyphens. Convert to lowercase. Also strip leading and
    trailing whitespace, dashes, and underscores.
    """
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize('NFKC', value)
    else:
        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value.lower())
    return re.sub(r'[-\s]+', '-', value).strip('-_')


def load_browser():
    if os.name != "nt":
        input("sorry random pic downloader currently only supports windows.\npress enter to exit.")
        exit()

    root = __file__[0:3]
    print("searching for chrome...")
    if file_in_path("chrome.exe", root) is not None:
        console.print("[bold]found chrome[/]")
        return "chrome"

    console.print("[red]chrome wasn't found[/]")
    print("searching for firefox...")
    if file_in_path("firefox.exe", root) is not None:
        console.print("[bold]found firefox[/]")
        return "firefox"

    console.print("[red]firefox wasn't found[/]")
    input("Please install a supported browser.\npress enter to exit.")
    exit()


installed_browser = load_browser()

if installed_browser == "chrome":
    op = webdriver.ChromeOptions()
    op.add_argument('headless')

    ser = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=ser, options=op)

elif installed_browser == "firefox":
    op = webdriver.FirefoxOptions()
    op.headless = True

    ser = Service(GeckoDriverManager().install())
    driver = webdriver.Firefox(service=ser, options=op)

time.sleep(0.2)

while not exited:
    search = input("Please give a searchterm: ")

    amount_to_download = int(input("Please enter how many images you want: "))

    url = f"https://www.google.com/search?q={search}&source=lnms&tbm=isch"

    driver.get(url)

    time.sleep(0.5)

    finished = False
    thread = threading.Thread(target=loading_animation)
    thread.start()

    # the while loop loads alle available images by scrolling until "Looks like you've reached the end" is displayed
    while not driver.find_element(by=By.XPATH,
                                  value='//*[@id="islmp"]/div/div/div/div[1]/div[2]/div[1]/div[2]/div[1]').is_displayed():
        driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")

        # trying to click on "see more images"
        try:
            driver.find_element(by=By.XPATH, value='//*[@id="islmp"]/div/div/div/div[1]/div[2]/div[2]/input').click()
        except selenium.common.exceptions.ElementNotInteractableException:
            pass
        except selenium.common.exceptions.NoSuchElementException:
            pass

        # trying to click on "see more anyway" this is necessary because google sometimes shows
        # "The rest of the results might not be what you're looking for. See more anyway" instead of "see more images"
        try:
            driver.find_element(by=By.XPATH, value='//*[@id="islmp"]/div/div/div/div[2]/span').click()
        except selenium.common.exceptions.ElementNotInteractableException:
            pass
        except selenium.common.exceptions.NoSuchElementException:
            pass

    finished = True

    html = driver.page_source

    soup = bs4.BeautifulSoup(html, "html.parser")

    img_urls = []
    try:
        if not os.path.isdir("./output"):
            os.mkdir("./output")
        os.mkdir(f"./output/{slugify(search)}")

        # filtering out everything that isn't a search results image
        img_divs = soup.find_all("img", {"class", "rg_i Q4LuWd"})

        img_divs_to_process = []

        for div in img_divs:
            if "data-src" in str(div):
                img_divs_to_process.append(div)

        # isolating the src of the img tag
        for img in tqdm(img_divs_to_process[:amount_to_download], desc="fetching image url from google", unit=" req"):
            img_url_index = str(img).find("src=\"") + 5
            img_url = str(img)[img_url_index::].split("\"")[0]
            if img_url.startswith("http"):
                img_urls.append(img_url)

        # fetching all images and saving them to the correct output folder
        for index, img in enumerate(tqdm(img_urls, desc="downloading images", unit=" images")):
            img_data = req.get(img).content
            with open(f"./output/{slugify(search)}/pic{index + 1}.png", "wb") as local_file:
                local_file.write(img_data)
    except FileExistsError:
        print(f"Please remove the directory {slugify(search)} from the output folder.")

    print(f"Downloaded {len(img_urls)} images.")

    repeat = input("Do you want to download more images (y/N): ")

    if repeat != "y":
        exited = True
