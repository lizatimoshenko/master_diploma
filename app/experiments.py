from app.neo4j_models import User, Book, Tag, add_tag_to_book, add_read_books
from app.orientdb_models import User, Book, Tag, add_tag_to_book, add_read_books
from app.arango_models import User, Book, Tag, add_tag_to_book, add_read_books
from time import time
import pandas as pd
import csv

# nodes
tags = pd.read_csv('/home/liza/PycharmProjects/diploma/tags.csv')                    # 34252
books = pd.read_csv('/home/liza/PycharmProjects/diploma/diploma_books_final.csv')    # 10000
users = pd.read_csv('/home/liza/PycharmProjects/diploma/users.csv')                  # 1000
# relationships
books_of_users = pd.read_csv('/home/liza/PycharmProjects/diploma/to_read1000.csv')   # 11849
tags_to_books = pd.read_csv('/home/liza/PycharmProjects/diploma/book_tags_cut.csv')  # 50000
followers = pd.read_csv('/home/liza/PycharmProjects/diploma/friends.csv')            # 20317
likes = pd.read_csv('/home/liza/PycharmProjects/diploma/likes.csv')                  # 40466


def timing(f):

    def timed(*args, **kw):
        ts = time()
        result = f(*args, **kw)
        te = time()
        print(te-ts)
        return result

    return timed


@timing
def add_books_read_by_users():
    for _, row in books_of_users.iterrows():
        add_read_books(
            row['user_id'],
            row['book_id'],
        )
    return True


@timing
def add_users():
    for _, row in users.iterrows():
        user = User()
        user.register(row['password'], row['username'])

    return True


@timing
def add_tags_to_book():
    for _, row in tags_to_books.iterrows():
        add_tag_to_book(
            int(row['goodreads_book_id']),
            int(row['tag_id']),
        )

    return True


@timing
def add_tags():
    for _, row in tags.iterrows():
        Tag.add_tag(
            row['tag_id'],
            row['tag_name'],
        )

    return True


@timing
def add_books():
    book = Book()
    for _, row in books.iterrows():
        book.add_book(
                      row['book_id'],
                      row['authors'],
                      row['original_publication_year'],
                      row['title'],
                      row['language_code']
            )

    return True


