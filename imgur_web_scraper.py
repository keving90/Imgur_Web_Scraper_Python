#!/usr/bin/env python3

"""
This Python program goes to imgur.com and downloads the first N galleries (up to 60) of a certain imgur search 
based on user input.

Usage: python3 imgur_web_scraper.py

User will be asked to enter their desired search query. They will then be asked how many galleries they would
like to download. The program will then start Firefox and begin downloading the galleries. Each gallery is
saved in its own folder. These folders are place in a main gallery folder that's created in the program's
current directory.

Warning: The folder holding all of the galleries will replace any existing folders with the same name. The
new gallery folder will have a name of the form: search_tags_galleries (where 'search_tag' is the user's input).

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
    # Get user input
    search = input("What are you searching for? (blank line to exit): ")

    # Exit if user enters blank line
    if search == '':
        print('Goodbye!')
        exit()

    return search


def get_num_galleries():
    """Returns the number of galleries desired by the user. The user must enter an integer."""
    while True:
        try:
            # Get user input
            num = input("How many galleries would you like to download? (0 or blank line to exit): ")

            # Exit if 0 or blank line
            if num == '' or int(num) == 0:
                print('Goodbye!')
                exit()

            # Number of galleries must be between 0 and 60
            if int(num) < 0 or int(num) > 60:
                print('\nPlease enter an integer between 0 and 60 (0 will exit the program).\n')
                continue

            break
        except ValueError:
            # User did not enter an integer for number of galleries
            print("Please enter an integer.")
            continue

    return int(num)


def create_directory(tag):
    """
    Creates a directory for the image galleries.

    tag - search tag string input by user

    Directory name of form: search_tags_galleries (where 'search_tag' is the user's input).

    New directory is placed in current working directory, and will replace any directory with
    the same name. The current working directory is then switched to the new directory.
    """
    dir_name = '_'.join(tag.split()) + '_galleries'
    os.makedirs(dir_name, exist_ok=True)
    os.chdir(dir_name)


def get_tag_search_url(tag):
    """
    Returns the imgur.com URL for the tag search based on the user's input.

    tag - search tag string input by user
    """
    url = 'https://imgur.com/search/score?q='
    tag_list = tag.split()
    search_tags = '+'.join(tag_list)

    return url + search_tags


def get_gallery_links(search_page):
    """Returns a list of the gallery links."""
    # Returns a response object
    res = requests.get(search_page)
    res.raise_for_status()

    # Returns a BeautifulSoup object
    search_results_soup = bs4.BeautifulSoup(res.text, 'lxml')

    # Return a CSS class selection list of galleries
    return search_results_soup.select('.image-list-link')


def get_search_element_ids(search_elem):
    """
    Returns a list of gallery IDs. These IDs are parsed from the CSS data
    from get_gallery_links().
    """
    return [element.attrs['href'].split('/')[2] for element in search_elem]


def download_galleries(driver, gallery_id_list, num_galleries):
    """
    Iterates through search results' galleries, downloads each gallery, and places it in its own folder.

    driver - the Firefox webdriver object

    gallery_id_list - list of IDs for each galley in the search results

    num_galleries - number of galleries desired by user
    """
    for num, id in enumerate(gallery_id_list, 1):
        # Only want the first N galleries specified by user
        if num > num_galleries:
            return

        # Make a direct link to the gallery
        gallery_link = 'https://imgur.com/gallery/' + id

        # Go to the gallery_link page
        driver.get(gallery_link)

        # Large galleries will have a "load more images" button
        load_more_images_button = driver.find_elements_by_xpath("""//a[contains(@class, 'post-loadall')]""")

        # If there is a "Load More Images" button, then we must switch to the gallery's grid view
        # so the entire gallery is loaded. Otherwise, we can use the default gallery view.
        if load_more_images_button:
            use_grid_view(driver, id, num)
        else:
            use_normal_view(driver, num)


def use_grid_view(driver, gallery_id, gallery_num):
    """
    Switches the gallery's web page to a grid view. If the gallery page has a "Load More Images" button, then page
    needs to be switched to "Grid View" so every image can be loaded.

    driver - the Firefox webdriver object

    gallery_id - list of IDs for each galley in the search results

    num - current gallery number
    """
    # Create a new gallery link
    gallery_link = 'https://imgur.com/a/' + gallery_id + '?grid'

    # Go to gallery link page
    driver.get(gallery_link)

    # Collect CSS data
    gallery_soup = bs4.BeautifulSoup(driver.page_source, 'lxml')
    gallery_elem = gallery_soup.select('.post-grid-image')

    # Create a folder for the gallery, and change current directory to the new one
    new_dir = 'gallery' + str(gallery_num).zfill(3)
    os.makedirs(new_dir, exist_ok=True)
    os.chdir(new_dir)

    # Save image in the gallery folder
    for i, item in enumerate(gallery_elem):
        # Parse the CSS data, and use requests to download the image
        clean_url = item.attrs['data-href'].strip('/')
        image_res = requests.get('https://' + clean_url)
        image_res.raise_for_status()
        image_num = str(i+1).zfill(3)
        create_file(clean_url, image_num, image_res, gallery_num)
    os.chdir('..')


def use_normal_view(driver, gallery_num):
    """
    Uses the current gallery's web page. If the gallery page does not have a "Load More Images" button, then the page's
    normal view can be used because all images have been loaded.

    driver - the Firefox webdriver object

    num - current gallery number
    """
    # Get the image elements
    images = driver.find_elements_by_xpath("""//*[@itemprop='contentURL']""")

    # Create a folder for the gallery, and change current directory to the new one
    new_dir = 'gallery' + str(gallery_num).zfill(3)
    os.makedirs(new_dir, exist_ok=True)
    os.chdir(new_dir)

    # Gather the necessary attributes for downloading the gallery and then download it
    for i, image in enumerate(images):
        if image.get_attribute('src'):
            image_url = image.get_attribute('src')
            image_res = requests.get(image.get_attribute('src'))
        elif image.get_attribute('content'):
            image_url = image.get_attribute('content')
            image_res = requests.get(image.get_attribute('content'))
        else:
            print("Error, could not find proper link to gallery number", i+1)
            continue

        image_res.raise_for_status()
        image_num = str(i+1).zfill(3)
        create_file(image_url, image_num, image_res, gallery_num)
    os.chdir('..')


def create_file(url, num, response_obj, gallery_num):
    """
    Creates a file based on the Imgur image's file type

    url - the image's URL

    num - the image number in the gallery

    response_obj - response object for image

    gallery_num - gallery number this image belongs to
    """
    # Allowed file extensions
    ext_list = ['jpg', 'png', 'jpeg', 'gif', 'mp4']

    # Get file type
    file_ext = url.split('.')[-1]

    # Write the image to a file
    if file_ext in ext_list:
        file = open('image' + num + '.' + file_ext, 'wb')
        if file:
            for chunk in response_obj.iter_content(100000):
                file.write(chunk)
            file.close()
        else:
            print('Error creating image' + str(num) + ' in gallery' + str(gallery_num) + '.')
    else:
        print('Error, cannot use file type', file_ext + '.')


def main():
    """The main function."""
    search_tags = get_search_tags()
    num_galleries = get_num_galleries()
    try:
        print("Downloading...")
        create_directory(search_tags)
        search_page = get_tag_search_url(search_tags)
        gallery_elems = get_gallery_links(search_page)
        gallery_id_list = get_search_element_ids(gallery_elems)

        # Path to geckodriver
        # Download geckodriver at: https://github.com/mozilla/geckodriver/releases
        driver = webdriver.Firefox(executable_path='/usr/local/bin/geckodriver') # CHANGE THIS PATH IF NEEDED
        driver.implicitly_wait(10)

        download_galleries(driver, gallery_id_list, num_galleries)
        driver.quit()
        print("Success!")
    except Exception:
        print("There was an error when downloading from Imgur.")


if __name__ == '__main__':
    main()