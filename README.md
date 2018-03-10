# Imgur Web Scraper (Python 3.6.1)

### Introduction
This Python program will download the first `N` image galleries from https://imgur.com/ based on the user's input. When the program begins, the user is first asked to enter the desired search query. Then, the user is asked how many galleries they would like to download. The program will then use `selenium` to open Firefox, go to each gallery, and download all images in each gallery. A folder used to hold the galleries will be created in the same directory as `imgur_web_scraper.py`. Each gallery will have its own folder.

Warning: The program will overwrite any folder with the exact same name as the folder it’s trying to create. For instance, if your search query is “funny dogs”, then a folder called “funny_dogs_pics” will be saved in the module’s directory. If you have another folder called “funny_dogs_pics”, the the program will overwrite this folder. Inside the pics folder you will find a separate folder for each gallery.

I created this program on macOS 10.11.6.

### Requirements
In order to run this program, you must have `Python 3` (I used Python 3.6.1 to make this), `selenium`, `requests`, `beautifulsoup4`, and `os` (built in). You will also need `Firefox` and `geckodriver`, which can be found at https://github.com/mozilla/geckodriver/releases.

### Installation
Place `imgur_web_scraper.py` in your desired folder. Open an new Terminal window, and change to the directory holding `imgur_web_scraper.py`. The program can be run with the following Terminal command: `python3 imgur_web_scraper.py`.

Note: By default, the program looks for geckodriver in /usr/local/bin/geckodriver. If you have geckodriver in a different folder, then you can edit Line 170 of the code to change the path.

### Other Remarks
This program works well on my computer, but I am interested in knowing how it will work for others. I created it on macOS, so I'm curious about its compatibility with Linux and Windown systems. Therefore, I encourage you to try it out. Please let me know if you have any problems. Comments and suggestions are welcome.
