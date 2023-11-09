#!/home/pi/bricolage/wired_cleanup/venv/bin/python3
import re
import requests
from bs4 import BeautifulSoup
import textwrap
import sys
import argparse


def print_all_article_parts(r_text_list):
    for r_text in r_text_list:
        print_article(r_text)


def remove_asides(article):
    # remove all 'class="RecircMostPopularItems..." lists, a Wired inter-story
    # aside type
    try:
        for aside in article.css.select('ul[class^="RecircMostPopularItems"]'):
            aside.decompose()
        for aside in article.css.select(
                'div[class^="SummaryItemBylineWrapper"]'):
            aside.decompose()
        for aside in article.css.select(
                'div[class^="SavingsUnitedCouponsWrapper"]'):
            aside.decompose()
        for aside in article.css.select('p[class="c-read-next__title"]'):
            aside.decompose()
    except: # a site other than Wired
        pass


def remove_internal_promos(article):
    # remove strong and blockquotes tags that seem to only
    # be used for promotional links
    try:
        for p_link in article.css.select('strong'):
            p_link.decompose()
    except: # a site / story without strong tags
        pass

    try:
        for p_link in article.css.select('blockquote'):
            p_link.decompose()
    except: # a site / story without blockquote tags
        pass


def remove_ads(article):
    # remove div's with class AdWrapper
    try:
        for p_link in article.css.select('div[class^="AdWrapper"]'):
            p_link.decompose()
    except: # a site / story without AdWrapper class tags
        pass


def print_article(r_text):
    "The main processing routine"

    # parse the HTML in the text
    whole_page = BeautifulSoup(r_text, features="html.parser")

    # Pull out the <article> leaving behind headers, footer, side bars, etc.
    try:
        article = whole_page.body.article.extract()
    except AttributeError:
        print("Page has no 'article' tag")
        sys.exit(-1) 

    # print the article's title (if it has one)
    try:
        print(article.h1.text + '\n')
    except AttributeError:
        pass

    # filter out the internal junk
    remove_internal_promos(article)
    remove_ads(article)
    remove_asides(article)

    # Print out the text within the paragraphs, text wrapped to look nice.
    #peas = article.find_all(['li', 'h2', 'p', 'b', 'i', 'strong'])
    peas = article.find_all(['li', 'h2', 'p'])
    last_p_name = None
    for p in peas:
        if p.name == 'li':
            print('o   ', end='')
        elif last_p_name == 'li':
            print()
        if p.name != 'strong':
            print('\n'.join(textwrap.wrap(p.text)))
        if p.name == 'p':
            print()
        last_p_name = p.name


def read_file(fname):
    """ Read the HTML from a file.
    """ 
    # Print out which file this output comes from.
    print(f"From file {fname}\n")

    # Read the file
    with open(fname) as f:
        r_text = f.read()

    # Put it into a list like what we get when reading from a website
    r_text_list = []
    r_text_list.append(r_text)
    return r_text_list


def read_url(url):
    """ Read the HTML from a website page.
    """ 
    r = requests.get(url)
    if r.status_code != 200:
        print(f"Download failed: status code {r.status_code}")
        sys.exit(1)

    # Print out which URL this output comes from.
    print(f"Retrieved from {url}\n")
    return r.text


def read_all_urls(url):
    """ Handle pages from sites like arstechnica.com that deliver multiple
        pages for an article.
    """
    r_text_list = []
    r_text = read_url(url)
    r_text_list.append(r_text)
    pages_search = re.search(',"pages":(\d+),', r_text)
    if pages_search and pages_search[1] != '1':
        for addnl_pageno in range(2, int(pages_search[1])+1):
            next_page = read_url(url + str(addnl_pageno) + '/')
            r_text_list.append(next_page)
        print(f'The number of pages was {pages_search[1]}')
    elif not pages_search:
        pass # print('"pages:" was not found')
    return r_text_list


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
                    prog='WiredArticleCleanup',
                    description='Reads the html of an article on Wired.com '
                        'and extracts and prints only the text of the '
                        'article, leaving out all ads, promo links, and '
                        'pictures.')
    parser.add_argument('path',
                        help='URL of the article to download (starting '
                             'with http[s]?://), or the '
                             'filename of an already downloaded HTML file')
    parser.add_argument('-u', '--url', dest='url',
                        help='Alternative way to specify '
                             'the URL of the article to download')
    parser.add_argument('-f', '--file', dest='fname',
                        help='Alternative way to specify '
                             'the path to an already downloaded HTML file')
    args = parser.parse_args()
    if args.path:
        if re.search('^http[s]?://', args.path):
            r_text_list = read_all_urls(args.path)
        else:
            r_text_list = read_file(args.path)
    elif args.url:
        r_text_list = read_url(args.url)
    elif args.fname:
        r_text_list = read_file(args.fname)
    else:
        parser.print_help()
        sys.exit(0)

    print_all_article_parts(r_text_list)
