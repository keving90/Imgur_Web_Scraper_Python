#!/usr/bin/env python3

"""
This module goes to imgur.com, types a provided search query (user input), and downloads the first X
(user input) galleries.

Note 1: The requests.get() function will not load any javasript on a web page. This can lead to the loaded
page being different from what you're seeing in your browser window. Therefore, selenium is more useful for
downloading the galleries.

Note 2: In Imgur, gif animations are actually mp4 files. This is why an mp4 file is downloaded instead of
a gif.
"""

from selenium import webdriver
import os, requests, bs4


def get_search_tags():
    """Returns the search tag(s) entered by the user."""
    search = input("What are you searching for? (blank line to exit) ")
    if search == '':
        print('Goodbye!')
        exit()
    return search


def get_num_galleries():
    """Returns the number of galleries desired by the user. The user must enter an integer."""
    while True:
        try:
            num = input("How many galleries would you like to download? (0 or blank line to exit) ")
            if num == '' or int(num) == 0:
                print('Goodbye!')
                exit()
            break
        except ValueError:
            print("Please enter an integer.")
            continue
    return int(num)


def create_directory(tag):
    """Creates a directory for the image galleries."""
    dir_name = '_'.join(tag.split()) + '_galleries'
    os.makedirs(dir_name, exist_ok=True)
    os.chdir(dir_name)


def get_tag_search_url(tag):
    """Returns the URL for the tag search."""
    url = 'https://imgur.com/search/score?q='
    tag_list = tag.split()
    search_tags = '+'.join(tag_list)
    return url + search_tags


def get_gallery_links(search_page):
    """Returns a list of the gallery links."""
    res = requests.get(search_page) # Returns a response object
    res.raise_for_status()
    search_results_soup = bs4.BeautifulSoup(res.text, 'lxml')
    return search_results_soup.select('.image-list-link')


def get_search_element_ids(search_elem):
    """Returns a list of the 'id part' of each element."""
    return [element.attrs['href'].split('/')[2] for element in search_elem]


def download_galleries(driver, id_list, num_galleries):
    """Iterates through search results' galleries, downloads each gallery, and places it in its own folder."""
    for num, id in enumerate(id_list):
        if num >= num_galleries:
            return
        gallery_link = 'https://imgur.com/gallery/' + id
        driver.get(gallery_link)
        load_more_images_button = driver.find_elements_by_xpath("""//a[contains(@class, 'post-loadall')]""")

        # If there is a "Load More Images" button, then we must switch to the gallery's grid view.
        # Otherwise, we can use the default gallery view.
        if load_more_images_button != []:
            use_grid_view(driver, id, num)
        else:
            use_normal_view(driver, id, num)
        os.chdir('..')


def use_grid_view(driver, image_id, num):
    """
    Switches the gallery's web page to a grid view. If the gallery page has a "Load More Images" button, then page
    needs to be switched to "Grid View" so every image can be loaded.
    """
    gallery_link = 'https://imgur.com/a/' + image_id + '?grid'
    driver.get(gallery_link)
    gallery_soup = bs4.BeautifulSoup(driver.page_source, 'lxml')
    gallery_elem = gallery_soup.select('.post-grid-image')

    # Create a folder for the gallery
    new_dir = 'gallery' + str(num+1).zfill(3)
    os.makedirs(new_dir, exist_ok=True)
    os.chdir(new_dir)

    # Save image in the gallery folder
    for num, item in enumerate(gallery_elem):
        clean_url = item.attrs['data-href'].strip('/')
        image_res = requests.get('https://' + clean_url)
        image_res.raise_for_status()
        image_num = str(num+1).zfill(3)
        create_file(clean_url, image_num, image_res)


def use_normal_view(driver, num):
    """
    Uses the current gallery's web page. If the gallery page does not have a "Load More Images" button, then the page's
    normal view can be used because all images have been loaded.
    """
    images = driver.find_elements_by_xpath("""//*[@itemprop='contentURL']""")

    # Create a folder for the gallery
    new_dir = 'gallery' + str(num+1).zfill(3)
    os.makedirs(new_dir, exist_ok=True)
    os.chdir(new_dir)

    # Gather the necessary attributes for downloading the gallery and then download it
    for num, image in enumerate(images):
        if image.get_attribute('src'):
            image_url = image.get_attribute('src')
            image_res = requests.get(image.get_attribute('src'))
        elif image.get_attribute('content'):
            image_url = image.get_attribute('content')
            image_res = requests.get(image.get_attribute('content'))
        else:
            print("Error, could not find proper link to gallery number", num+1)

        image_res.raise_for_status()
        image_num = str(num+1).zfill(3)
        create_file(image_url, image_num, image_res)


def create_file(url, num, response_obj):
    """Creates a file based on the Imgur image's file type"""
    ext_list = ['jpg', 'png', 'jpeg', 'gif', 'mp4']
    split_url = url.split('.')
    if split_url[-1] in ext_list:
        file = open('image' + num + '.' + split_url[-1], 'wb')
        if file:
            for chunk in response_obj.iter_content(100000):
                file.write(chunk)
            file.close()
        else:
            print('Error creating image' + num)
    else:
        print('Error, cannot use file type', split_url[-1])


def main():
    """The main function."""
    search_tags = get_search_tags()
    num_galleries = get_num_galleries()
    try:
        print("Downloading...")
        create_directory(search_tags)
        search_page = get_tag_search_url(search_tags)
        search_elem = get_gallery_links(search_page)
        id_list = get_search_element_ids(search_elem)

        # Path to geckodriver
        # Download geckodriver at: https://github.com/mozilla/geckodriver/releases
        driver = webdriver.Firefox(executable_path='/usr/local/bin/geckodriver')
        driver.implicitly_wait(10)

        download_galleries(driver, id_list, num_galleries)
        driver.quit()
        print("Success!")
    except Exception:
        print("There was an error when downloading from Imgur.")


if __name__ == '__main__':
    main()