import requests
import bs4
import pandas as pd
import re
from requests import get
from bs4 import BeautifulSoup
import acquire
import numpy as np
from sklearn.model_selection import train_test_split

import unicodedata
import re
import json

import nltk
from nltk.tokenize.toktok import ToktokTokenizer
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
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

def make_prepped_columns(df, column):
    df['clean'] = df[column].apply(lambda x: basic_clean(x))
    df['lemmatized'] = df['clean'].apply(lambda x: tokenize(x))
    df['stemmed'] = df['lemmatized'].apply(lambda x: stem(x))
    df['lemmatized'] = df['lemmatized'].apply(lambda x: lemmatize(x))
    return df

''' 
Takes in readme contents and applies the make_prepped_columns() function. Drops altered readme 
columns with the exception of the lemmatized one (as that's what I'll be working with) and the original.
Also gets rid of rows containing null readme or null language columns. Drops rows if their respective language 
appears less than twice (can't split it). Removes stopwords.
'''

def prep_repos(df):
    
    # Converts readme into a string

    df['readme_contents'] = df['readme_contents'].apply(lambda x: str(x))

    # Applying make_prepped_columns function

    df = make_prepped_columns(df, 'readme_contents')

    # Clears out text that is in foreign characters

    df = df[df['readme_contents'].map(lambda x: x.isascii())]

    # Drops unnecessary columns

    df.drop(columns = ['Unnamed: 0', 'clean', 'stemmed'], inplace = True)

    # Renames the lemmatized column to "readme_contents_clean"

    df.rename(columns = {'lemmatized': 'readme_contents_clean'}, inplace = True)

    # Removes rows with nan values in readme_contents_clean column

    df = df[(~df['readme_contents_clean'].str.contains("nan")) & (df['readme_contents_clean'].str.len() > 20)]

    # Drops any rows with null values in language column

    df.dropna(how = 'any', inplace = True)

    # Drops any row that's respective language only appears once in the data set (This prevents me from being able to split it)

    df = df.groupby('language').filter(lambda x : len(x)>2)

    # Resets the index to standard numerical

    df = df.reset_index()

    # A list of additional stopwords 

    remove_words = ["'", '&#9;', 'repository', 'file', 'use', 'build', 'version', 'using']

    # Applying the removal of stopwords

    df['readme_contents_clean'] = df['readme_contents_clean'].apply(lambda x: remove_stopwords(x, extra_words = remove_words))
    return df

'''
Adds a feature that searches the readme for mentions of a specific coding language and extracts it, then puts that language into the 
"languages_in_readme" column. Also adds a feature for "readme_length"
'''

def add_language_dummies_and_length_feature(df):

    # List of languages to pick up if found in the readme

    languages = [' Python ', ' python ', ' java ', ' Java ', ' C++ ', ' c++ ', ' c# ', ' C# ' ' PHP ',  ' php ', ' Javascript ', 
             'JavaScript', ' javascript ', ' Shell ', ' shell ', ' HTML ', ' html ', ' Ruby ', ' ruby ',
             ' Jupyter Notebook', ' jupyter notebook', ' Typescript', ' TypeScript ', ' typescript ', ' Go ']

    # Container for the found languages of all readme's

    the_languages = []

    # Iterating over each row

    for index, row in df.iterrows():

    # Container for found languages of each readme

        holder = []

    # Iterating over the list of languages
        for word in languages:

    # Setting if statement for when a word is found in the readme but not already in the "holder" container

            if word in row['readme_contents'] and word not in holder:

    # If a word in the list languages is found in the readme, put it in the "holder" container

                holder.append(word.lower())

    # Once all the languages have been extracted from a single readme, put that list into the "the_languages" container

        the_languages.append(holder)

    # Putting "the_languages" container into a pandas dataframe in a column titled "languages_in_readme"

    df2 = pd.DataFrame({'languages_in_readme': the_languages})

    # Normalizing the languages found in the readme by making each character lowercase after converting each element into a string

    df2['languages_in_readme'] = df2['languages_in_readme'].apply(lambda x: str(x).lower())

    # Removes list brackets from the now string

    df2['languages_in_readme'] = df2['languages_in_readme'].apply(lambda x: x[1:-1])

    # Puts a NaN value into empty values for "languages_in_readme"

    df2 = df2.replace('', np.nan)

    # Drops original (uncleaned) readme data from the original dataframe

    df.drop(columns = ['readme_contents'], inplace = True)

    # Creates a column in the original dataframe for length of the readme 

    df['readme_length'] = df['readme_contents_clean'].apply(lambda x: len(x))

    # Concatenates original and new dataframe together

    df = pd.concat([df, df2], axis =1)

    # Creates dummies for each language found to be in the readmes

    df['has_python'] = df.languages_in_readme.str.contains('python')
    df['has_php'] = df.languages_in_readme.str.contains('php')
    df['has_html'] = df.languages_in_readme.str.contains('html')
    df['has_typescript'] = df.languages_in_readme.str.contains('typescript')
    df['has_ruby'] = df.languages_in_readme.str.contains('ruby')
    df['has_shell'] = df.languages_in_readme.str.contains('shell')
    df['has_c++'] = df.languages_in_readme.str.contains(r'c\+\+')
    df['has_java'] = df.languages_in_readme.str.contains(r'java ')
    df['has_javascript'] = df.languages_in_readme.str.contains('javascript')
    df['has_go'] = df.languages_in_readme.str.contains('go')
    df["has_python"] = df["has_python"].fillna(0)
    df["has_python"] = df["has_python"].astype(int)
    df['has_php'] = df['has_php'].fillna(0)
    df['has_php'] = df['has_php'].astype(int)
    df['has_html'] = df['has_html'].fillna(0)
    df['has_html'] = df['has_html'].astype(int)
    df['has_typescript'] = df['has_typescript'].fillna(0)
    df['has_typescript'] = df['has_typescript'].astype(int)
    df['has_ruby'] = df['has_ruby'].fillna(0)
    df['has_ruby'] = df['has_ruby'].astype(int)
    df['has_shell'] = df['has_shell'].fillna(0)
    df['has_shell'] = df['has_shell'].astype(int)
    df['has_c++'] = df['has_c++'].fillna(0)
    df['has_c++'] = df['has_c++'].astype(int)
    df['has_java'] = df['has_java'].fillna(0)
    df['has_java'] = df['has_java'].astype(int)
    df['has_javascript'] = df['has_javascript'].fillna(0)
    df['has_javascript'] = df['has_javascript'].astype(int)
    df['has_go'] = df['has_go'].fillna(0)
    df['has_go'] = df['has_go'].astype(int)

    return df

'''
Splits the data into train, validate, and test
'''

def split(df, stratify_by=None):
    train, test = train_test_split(df, test_size=.2, random_state=123, stratify=df[stratify_by])
    
    train, validate = train_test_split(train, test_size=.3, random_state=123, stratify=train[stratify_by])
    
    return train, validate, test