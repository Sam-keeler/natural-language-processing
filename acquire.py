import requests
import bs4
import pandas as pd
import re

'''
This function takes a url from blog posts on the codeup website and returns the title, date, and content
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

def acquire_all_blogs():
    blog_list = ['https://codeup.com/codeups-data-science-career-accelerator-is-here/',
                'https://codeup.com/data-science-myths/',
                'https://codeup.com/data-science-vs-data-analytics-whats-the-difference/',
                'https://codeup.com/10-tips-to-crush-it-at-the-sa-tech-job-fair/',
                'https://codeup.com/competitor-bootcamps-are-closing-is-the-model-in-danger/']
    return pd.DataFrame([acquire_codeup_blog(blog) for blog in blog_list])

