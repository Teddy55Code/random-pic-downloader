from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
import requests as req
import bs4
import unicodedata
import re
from tqdm import tqdm
import time
import os

def fileInPath(name, root):
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

if os.name == "nt":
    root = __file__[0:3]
    print("searching for chrome")
    if fileInPath("chrome.exe", root) is None:
        print("chrome wasn't found")
        print("searching for firefox")
        if fileInPath("firefox.exe", root) is None:
            print("firefox wasn't found")
            input("Please install a supported browser.\npress enter to exit.")
            exit()
        else:
            print("found firefox")
            installed_browser = "firefox"
    else:
        print("found chrome")
        installed_browser = "chrome"
else:
    input("sorry random pic downloader currently only supports windows.\npress enter to exit.")
    exit()

search = input("Please give a searchterm: ")

if installed_browser == "chrome":
    op = webdriver.ChromeOptions()
    op.add_argument('headless')

    ser = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=ser, options=op)

elif installed_browser == "firefox":
    op = webdriver.FirefoxOptions()
    op.add_argument('headless')

    ser = Service(GeckoDriverManager().install())
    driver = webdriver.Firefox(service=ser, options=op)

url = f"https://www.google.com/search?q={search}&source=lnms&tbm=isch"

driver.get(url)

html = driver.page_source

soup = bs4.BeautifulSoup(html, "html.parser")

img_urls = []
try:
    if not os.path.isdir("./output"):
        os.mkdir("./output")
    os.mkdir(f"./output/{slugify(search)}")

    img_divs = soup.find_all("img", {"class", "rg_i Q4LuWd"})

    img_divs_to_process = []

    for div in img_divs:
        if "data-src" in str(div):
            img_divs_to_process.append(div)


    for img in tqdm(img_divs_to_process, desc="fetching image url from google", unit =" req"):
        img_url_index = str(img).find("src=\"") + 5
        img_url = str(img)[img_url_index::].split("\"")[0]
        if img_url.startswith("http"):
            img_urls.append(img_url)

    for index, img in enumerate(tqdm(img_urls, desc="downloading images", unit =" images")):
        img_data = req.get(img).content
        with open(f"./output/{slugify(search)}/pic{index+1}.jpg", "wb") as local_file:
            local_file.write(img_data)
except FileExistsError:
    print(f"Please remove the directory {search} from the output folder")

print(f"downloaded {len(img_urls)} images")
