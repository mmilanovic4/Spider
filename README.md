# Overview

Educational, open-source and multi-threaded website crawler written in Python, inspired by [thenewboston](https://github.com/buckyroberts/Spider). It looks for internal links only - subdomains are excluded. However, this and number of threads could be tweaked easily.

## Usage

Simply run **spider.py** using Python 3.x. Script takes target URL as a required argument:
```
python3 spider.py https://xkcd.com
```

You can also give script execute permission and execute it directly:
```
sudo chmod +x spider.py
clear && ./spider.py https://xkcd.com
```

Once done, all crawled links will be saved in a file. For checking number of crawled links I like to use GNU **wc** utility:
```
wc --lines xkcd_com.txt
```

## Links

- Ryan Mitchell, Web Scraping with Python - O'Reilly Media, 2015.
- [Python Web Crawler Tutorials](https://www.youtube.com/playlist?list=PL6gx4Cwl9DGA8Vys-f48mAH9OKSUyav0q)
