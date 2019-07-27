"""Experiments for comparison of databases """
from time import time

import csv
import pandas as pd

#from app.neo4j_models import User, Book, Tag, clear_graph

from app.orientdb_models import User, Book, Tag, clear_graph
#from app.arango_models import User, Book, Tag, clear_graph

# nodes
tags = pd.read_csv('datasets/tags.csv')  # 34252
books = pd.read_csv('datasets/diploma_books_final.csv')  # 10000
users = pd.read_csv('datasets/users.csv')  # 1000
# relationships
books_of_users = pd.read_csv('datasets/to_read1000.csv')  # 11849
tags_to_books = pd.read_csv('datasets/tags_to_book.csv')  # 50000
followers = pd.read_csv('datasets/friends.csv')  # 20317
likes = pd.read_csv('datasets/likes.csv')  # 40466


def save_time(test_name, time):
    with open('results.csv', mode='a') as csv_file:
        fieldnames = ['test', 'orientdb', 'neo4j', 'arangodb']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writerow({'test': test_name, 'orientdb': time, 'neo4j': None, 'arangodb': None})


def timing(func):
    def timed(*args, **kw):
        time_start = time()
        result = func(*args, **kw)
        time_end = time()
        running_time = time_end - time_start
        save_time(func.__name__, running_time)
        return result

    return timed


@timing
def insert_books():
    """Insert books from dataset to graph"""
    for _, row in books.iterrows():
        book = Book(book_id=row['book_id'],
                    authors=row['authors'],
                    year=row['original_publication_year'],
                    title=row['title'],
                    language=row['language_code'])
        book.insert()



@timing
def insert_users():
    """Insert users from dataset to graph"""
    for index, row in users.iterrows():
        user = User(user_id=index, username=row['username'], password=row['password'])
        user.insert()



@timing
def insert_tags():
    """Insert users from dataset to graph"""
    for _, row in tags.iterrows():
        tag = Tag(tag_id=row['tag_id'], tag_name=row['tag_name'])
        tag.insert()



@timing
def insert_reads():
    """Insert books read by users from dataset to graph"""
    for _, row in books_of_users.iterrows():
        user = User(user_id=str(row['user_id']))
        user.reads(str(row['book_id']))



@timing
def insert_tagged_to():
    for _, row in tags_to_books.iterrows():
        book = Book(book_id=str(row['book_id']))
        book.link_to_tag(str(row['tag_id']))


@timing
def insert_follows():
    for _, row in followers.iterrows():
        user = User(user_id=str(row['user']))
        user.follows(str(row['friend']))


@timing
def insert_likes():
    for _, row in likes.iterrows():
        user = User(user_id=str(row['user_id']))
        user.likes(str(row['book_id']))


#insert_likes()
#insert_reads()
#insert_tagged_to()
insert_follows()
