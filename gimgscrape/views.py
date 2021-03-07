from django.shortcuts import render

# Create your views here.

import os
import time
import requests
import logging
from selenium import webdriver

logging.basicConfig(filename='std.log', filemode='a',
                    format='%(name)s - %(levelname)s - %(message)s'
                    )
logger = logging.getLogger()


def fetch_image_urls(query, max_links_to_fetch, wd, sleep_between_interactions=1):

    def scroll_to_end(wd):
        wd.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(sleep_between_interactions)

        # build the google query

    search_url = f"https://www.google.com/search?safe=off&site=&tbm=isch&source=hp&q={query}&oq={query}&gs_l=img"

    # load the page
    wd.get(search_url)

    image_urls = set()
    image_count = 0
    results_start = 0
    while image_count < max_links_to_fetch:
        scroll_to_end(wd)

        # get all image thumbnail results
        thumbnail_results = wd.find_elements_by_css_selector("img.Q4LuWd")
        number_results = len(thumbnail_results)

        logger.warning(f"Found: {number_results} search results. Extracting "
                     f"links from {results_start}:{number_results}"
                     )

        for img in thumbnail_results[results_start:number_results]:
            # try to click every thumbnail such that we can get the real
            # image behind it
            try:
                img.click()
                time.sleep(sleep_between_interactions)
            except Exception:
                continue

            # extract image urls
            actual_images = wd.find_elements_by_css_selector('img.n3VNCb')
            for actual_image in actual_images:
                if actual_image.get_attribute('src') and 'http' in actual_image.get_attribute('src'):
                    image_urls.add(actual_image.get_attribute('src'))

            image_count = len(image_urls)

            if len(image_urls) >= max_links_to_fetch:
                logging.warning(f"Found: {len(image_urls)} image links, done!")
                break
        else:
            logging.warning("Found:", len(image_urls), "image links, "
                                                    "looking for more ...")
            time.sleep(30)
            load_more_button = wd.find_element_by_css_selector(".mye4qd")
            if load_more_button:
                wd.execute_script("document.querySelector('.mye4qd').click();")

        # move the result startpoint further down
        results_start = len(thumbnail_results)

    return image_urls


def persist_image(folder_path, url, counter):
    try:
        image_content = requests.get(url).content

    except Exception as e:
        logging.warning(f"ERROR - Could not download {url} - {e}")

    try:
        f = open(os.path.join(folder_path, 'jpg' + "_" + str(counter) + ".jpg"), 'wb')
        f.write(image_content)
        f.close()
        logging.info(f"SUCCESS - saved {url} - as {folder_path}")
    except Exception as e:
        logging.warning(f"ERROR - Could not save {url} - {e}")


def search_and_download(request):
    logging.warning("Image Scraper Started")
    # import pdb
    # pdb.set_trace()
    search_term = request.POST.get("item_name")
    driver_path = 'chromedriver'
    target_path = './images'
    number_images = 15
    target_folder = os.path.join(target_path, '_'.join(search_term.lower().split(' ')))

    if not os.path.exists(target_folder):
        os.makedirs(target_folder)

    with webdriver.Chrome(executable_path=driver_path) as wd:
        res = fetch_image_urls(search_term, number_images, wd=wd, sleep_between_interactions=1)

    counter = 0
    for elem in res:
        persist_image(target_folder, elem, counter)
        counter += 1

    return render(request, "gimgscrape/thanks.html")


def index(request):
    return render(request, 'gimgscrape/index.html')
