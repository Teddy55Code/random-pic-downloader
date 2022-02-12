import requests as req
import bs4
import os
import unicodedata
import re

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


search = input("Please give a searchterm: ")

url = f"https://www.google.com/search?q={search}&source=lnms&tbm=isch&num=30"

req_result = req.get(url)

soup = bs4.BeautifulSoup(req_result.text,
                         "html.parser")

img_divs = soup.find_all("img")

img_urls = []
try:
    os.mkdir(f"./output/{slugify(search)}")

    for img in img_divs:
        img_url_index = str(img).find("src=\"") + 5
        img_url = str(img)[img_url_index::].split("\"")[0]
        if img_url.startswith("http"):
            img_urls.append(img_url)

    for index, img in enumerate(img_urls):
        img_data = req.get(img).content
        with open(f"./output/{slugify(search)}/pic{index+1}.jpg", "wb") as local_file:
            local_file.write(img_data)
except FileExistsError:
    print(f"Please remove the directory {search} from the output folder")

print(f"downloaded {len(img_urls)} images")
