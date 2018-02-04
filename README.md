Imgur Web Scraper by Kevin Geiszler (Python 3.6.1)

This module goes to imgur.com, types a provided search query (user input), and downloads the first X (user input) galleries. Animations in an Imgur gallery are saved as mp4 files. The program uses the selenium, os, requests, and bs4 libraries. It also uses the Firefox browser to access Imgur. I created this program on Mac OS 10.11.6.

You will need geckodriver in order to run this program. It can be found at: https://github.com/mozilla/geckodriver/releases

By default, the program looks for geckodriver in /usr/local/bin/geckodriver. If you have geckodriver in a different folder, then you can edit Line 42 of the code to change the path.

Upon running the program, the user is prompted for a search query. They are then asked to enter how many galleries they would like to download. The galleries are saved to a folder in the the same directory as imgur_web_scraper.py.

Warning: The program will overwrite any folder with the exact same name as the folder it’s trying to create. For instance, if your search query is “funny dogs”, then a folder called “funny_dogs_pics” will be saved in the module’s directory. If you have another folder called “funny_dogs_pics”, the the program will overwrite this folder. Inside the pics folder you will find a separate folder for each gallery.

This program works well on my computer, but I’m not sure how it will work for others. Therefore, I encourage you to try it out. Please let me know if you have any problems. Comments and suggestions are welcome.
