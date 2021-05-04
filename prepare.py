import requests
import bs4
import pandas as pd
import re
from requests import get
from bs4 import BeautifulSoup
import acquire

import unicodedata
import re
import json

import nltk
from nltk.tokenize.toktok import ToktokTokenizer
from nltk.corpus import stopwords
nltk.download('wordnet')
nltk.download('stopwords')

import warnings
warnings.filterwarnings("ignore")

'''
Takes in a string and lowercase everything, normalize unicode characters, replace anything that is not a letter, number, whitespace or a 
single quote.
'''

def basic_clean(original):
    blog_normalized = original.lower()
    blog_normalized = unicodedata.normalize('NFKD', blog_normalized)\
        .encode('ascii', 'ignore')\
        .decode('utf-8', 'ignore')
    blog_normalized = re.sub(r"[^a-z0-9'\s]", '', blog_normalized)
    blog_normalized = blog_normalized.replace('\n', '')
    return blog_normalized

'''
Takes in a string and tokenize all the words in the string.
'''

def tokenize(text):
    tokenizer = nltk.tokenize.ToktokTokenizer()
    return tokenizer.tokenize(text, return_str=True)

'''
Accepts some text and returns the text after applying stemming to all the words.
'''

def stem(text):
    ps = nltk.porter.PorterStemmer()
    stems = [ps.stem(word) for word in text.split()]
    text_stemmed = ' '.join(stems)
    return text_stemmed

'''
Accepts some text and returns the text after applying lemmatization to each word.
'''

def lemmatize(text):
    wnl = nltk.stem.WordNetLemmatizer()
    lemmas = [wnl.lemmatize(word) for word in text.split()]
    text_lemmatized = ' '.join(lemmas)
    return text_lemmatized

'''
Accepts some text and returns the text after removing all the stopwords. Contains optional arguments to remove or add words to the stop list.
'''

def remove_stopwords(text, extra_words=[], exclude_words=[]):
    stopword_list = stopwords.words('english')
    for word in exclude_words:
        stopword_list.remove(word)
    for word in extra_words:
        stopword_list.append(word)
    words = text.split()
    filtered_words = [w for w in words if w not in stopword_list]
    text_without_stopwords = ' '.join(filtered_words)
    return text_without_stopwords

'''
Takes in a dataframe with original text and produces columns for each of the functions above applied
'''

def make_prepped_columns(df):
    df.rename(columns = {'content': 'original'}, inplace = True)
    df['clean'] = df['original'].apply(lambda x: basic_clean(x))
    df['lemmatized'] = df['clean'].apply(lambda x: tokenize(x))
    df['stemmed'] = df['lemmatized'].apply(lambda x: stem(x))
    df['lemmatized'] = df['lemmatized'].apply(lambda x: lemmatize(x))
    return df