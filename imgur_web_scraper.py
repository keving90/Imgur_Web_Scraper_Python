#! /usr/bin/env python3.6.1

''' This module goes to imgur.com, types a provided search query (user input), and downloads the first X 
(user input) galleries.

Note 1: The requests.get() function will not load any javasript on a web page. This can lead to the loaded
page being different from what you're seeing in your browser window. Therefore, selenium is more useful for
downloading the galleries. 

Note 2: In Imgur, gif animations are actually mp4 files. This is why an mp4 file is downloaded instead of
a gif.'''

from selenium import webdriver
import os, requests, bs4

def ImgurGalleryDownloader(tag, num_galleries):
    # Create a directory for the image galleries
    dir_name = '_'.join(tag.split()) + '_pics'
    os.makedirs(dir_name, exist_ok=True)
    os.chdir(dir_name)

    # Get url for tag search
    url = 'https://imgur.com/search/score?q='
    tag_list = tag.split()
    search_tags = '+'.join(tag_list)
    search_page = url + search_tags

    # Get gallery links
    res = requests.get(search_page) # Returns a response object
    res.raise_for_status()
    search_results_soup = bs4.BeautifulSoup(res.text, 'lxml')
    search_elem = search_results_soup.select('.image-list-link')

    # Get the id part of each element and place them into id_list
    id_list = []
    for element in search_elem:
        split_elem = element.attrs['href'].split('/')
        id_list.append(split_elem[2])

    # Path to geckodriver
    # Download geckodriver at: https://github.com/mozilla/geckodriver/releases
    driver = webdriver.Firefox(executable_path='/usr/local/bin/geckodriver')
    driver.implicitly_wait(10)

    # Iterate through search results' galleries, download each gallery, and place it in its own folder
    count = 0
    while count < num_galleries:
        # Open browser to a gallery
        gallery_link = 'https://imgur.com/gallery/' + id_list[count]
        driver.get(gallery_link)
        load_more_images_button = driver.find_elements_by_xpath("""//a[contains(@class, 'post-loadall')]""")
        # If there is a "Load More Images" button, then we must switch to the gallery's grid view.
        # Otherwise, we can use the default gallery view.
        if load_more_images_button != []:
            UseGridView(driver, id_list[count], count)
        else:
            UseNormalView(driver, id_list[count], count)
        os.chdir('..')
        count += 1
    driver.quit()

# If the gallery page does not have a "Load More Images" button, then the page's normal view can be used.
def UseNormalView(driver, image_id, count):
    images = driver.find_elements_by_xpath("""//*[@itemprop='contentURL']""")

    # Create a folder for the gallery
    new_dir = 'gallery' + str(count+1).zfill(3)
    os.makedirs(new_dir, exist_ok=True)
    os.chdir(new_dir)

    # Gather the necessary attributes for downloading the gallery and then download it
    for num, image in enumerate(images):
        if image.get_attribute('src') != None:
            image_url = image.get_attribute('src')
            image_res = requests.get(image.get_attribute('src'))
        elif image.get_attribute('content') != None:
            image_url = image.get_attribute('content')
            image_res = requests.get(image.get_attribute('content'))
        else:
            print("Error, could not find proper link to gallery number", count+1)
        image_res.raise_for_status()
        image_num = str(num+1).zfill(3)
        CreateFile(image_url, image_num, image_res)

# If the gallery page has a "Load More Images" button, then page needs to be switched to "Grid View" so
# every image can be downloaded.
def UseGridView(driver, image_id, count):
    gallery_link = 'https://imgur.com/a/' + image_id + '?grid'
    driver.get(gallery_link)
    gallery_soup = bs4.BeautifulSoup(driver.page_source, 'lxml')
    gallery_elem = gallery_soup.select('.post-grid-image')

    # Create a folder for the gallery
    new_dir = 'gallery' + str(count+1).zfill(3)
    os.makedirs(new_dir, exist_ok=True)
    os.chdir(new_dir)

    # Save image in the gallery folder
    for num, item in enumerate(gallery_elem):
        clean_url = item.attrs['data-href'].strip('/')
        image_res = requests.get('https://' + clean_url)
        image_res.raise_for_status()
        image_num = str(num+1).zfill(3)
        CreateFile(clean_url, image_num, image_res)

# Create a file based on the Imgur image's file type
def CreateFile(url, num, response_obj):
    ext_list = ['jpg', 'png', 'jpeg', 'gif', 'mp4']
    split_url = url.split('.')
    if split_url[-1] in ext_list:
        file = open('image' + num + '.' + split_url[-1], 'wb')
        if file:
            for chunk in response_obj.iter_content(100000):
                file.write(chunk)
            file.close()
        else:
            print('Error creating image' + image_num)
    else:
        print('Error, cannot use file type', split_url[-1])



if __name__ == '__main__':
    search = input("What are you searching for? ")
    if search == '':
        exit()
    while True:
        num = input("How many galleries would you like to download? ")
        if num == '':
            exit()
        try:
            num = int(num)
            if num == 0:
                print("It looks like you don't want to download anything. Goodbye.")
            break
        except ValueError:
            print("Please enter an integer.")
            continue
    print("Downloading...")
    try:
        ImgurGalleryDownloader(search, num)
        print("Success!")
    except Exception:
        print("There was an error when downloading from Imgur.")


































