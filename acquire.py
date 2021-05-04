import requests
import bs4
import pandas as pd
import re
from requests import get
from bs4 import BeautifulSoup

'''
Takes a url from blog posts on the codeup website and returns the title, date, and content
posted on that blog
'''

def acquire_codeup_blog(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
    response = requests.get(url, headers=headers)
    html = response.text
    soup = bs4.BeautifulSoup(html)
    title = soup.find('title').text
    content = soup.find(class_ = 'jupiterx-post-content').text
    date = soup.find(itemprop="datePublished").text
    return {
        "title": title,
        "date": date,
        "content": content}

'''
Has multiple urls for blog posts on the codeup website and extracts the title, date, and content from all of them
'''

def acquire_all_blogs():
    blog_list = ['https://codeup.com/codeups-data-science-career-accelerator-is-here/',
                'https://codeup.com/data-science-myths/',
                'https://codeup.com/data-science-vs-data-analytics-whats-the-difference/',
                'https://codeup.com/10-tips-to-crush-it-at-the-sa-tech-job-fair/',
                'https://codeup.com/competitor-bootcamps-are-closing-is-the-model-in-danger/']
    return pd.DataFrame([acquire_codeup_blog(blog) for blog in blog_list])

'''
Takes in a soup created from an article url and extracts the title, content, and category from that article
'''

def get_article(soup, category):
    title = soup.find(itemprop="headline").text
    content = soup.find(itemprop="articleBody").text
    return {
        "title": title,
        "content": content,
        "category": category}

'''
Takes in a specified category and extracts the title, content, and category from each article falling under that category
'''

def get_articles(category):
    base = "https://inshorts.com/en/read/"
    url = base + category
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
    response = get(url, headers=headers)
    soup = BeautifulSoup(response.text)
    articles = soup.select(".news-card")
    output = []
    for article in articles:
        article_data = get_article(article, category) 
        output.append(article_data)
    return output

'''
Takes in a list of categories and extracts the title, content, and category from each article falling under a category in the the category list
'''

def get_all_inshorts(category_list):

    all_inshorts = []

    for category in category_list:
        all_category_articles = get_articles(category)
        all_inshorts = all_inshorts + all_category_articles
    
    df = pd.DataFrame(all_inshorts)
    return df
