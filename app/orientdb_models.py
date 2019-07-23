from pyorient.ogm import declarative
from pyorient.ogm.property import (String, Integer)
from passlib.hash import sha256_crypt

from .databases import OrientDataBase

Node = declarative.declarative_node()
Relationship = declarative.declarative_relationship()


# OrientDataBase.create()
client, graph = OrientDataBase.connect()

graph.include(Node.registry)
graph.include(Relationship.registry)


class User(Node):
    """Class for User node"""

    __primary_key__ = "username"
    element_plural = 'users'
    registry_plural = "users"

    user_id = String()
    username = String()
    password = String()

    def __init__(self, **kwargs):
        self._props = kwargs

    def find(self):
        """ Return user in database by username """
        user = graph.query(User, username=self.username)
        print(user)
        return user

    def insert(self):
        """ Insert user node to graph """
        graph.include(Node.registry)
        if not self.find():
            graph.users.create(user_id=self.user_id,
                               username=self.username,
                               password=sha256_crypt.encrypt(self.password)
                               )

    def verify_password(self, password):
        """ Return if password is valid """
        user = self.find()
        if not user:
            return False
        return sha256_crypt.verify(password, self.password)

    def reads(self, book_id):
        """Create relationship (User)-[:READS]->(Book)"""
        user = graph.users.query(user_id=self.user_id).first()
        book = graph.books.query(book_id=book_id).first()
        graph.reads.create(user, book)

    def follows(self, friend_id):
        """Create relationship (User)-[:FOLLOWS]->(User)"""
        user = graph.users.query(user_id=self.user_id).first()
        friend = graph.books.query(friend_id=friend_id).first()
        graph.follows.create(user, friend)

    def likes(self, book_id):
        """ Create relationship (User)-[:LIKES]->(Book) """
        user = graph.users.query(user_id=self.user_id).first()
        book = graph.books.query(book_id=book_id).first()
        graph.likes.create(user, book)

    @staticmethod
    def users():
        """List of all users"""
        users = graph.users.query().all()
        return [user.username for user in users]


class Book(Node):
    """Class for Book node"""
    element_plural = "books"
    registry_plural = "books"

    book_id = String()
    authors = String()
    year = Integer()
    title = String()
    language = String()

    def __init__(self, **kwargs):
        self._props = kwargs

    def insert(self):
        """Inserting book node to graph"""
        graph.books.create(book_id=self.book_id,
                           authors=self.authors,
                           year=self.year,
                           title=self.title,
                           language=self.language)

    def linked_tags(self):
        """Return list of tags for specific book"""
        book = graph.books.query(book_id=self.book_id).first()
        tags = [tag.outV().tag_name for tag in book.inE()]
        return tags

    @staticmethod
    def books():
        """Return list of all books"""
        books = graph.query(Book).all()
        return [book for book in books]

    @staticmethod
    def most_popular_books():
        """ Return books which are read by most amount of users """
        query = """
                SELECT book_title, Count(tags)
                from (
                      MATCH {class: User, as: user}.in('reads') {as: book}
                      RETURN book.title, user
                )
                group by book_title
        """
        return graph.query(query)  # alright?


class Tag(Node):
    """Class for Tag node"""

    element_plural = "tags"

    tag_id = Integer()
    tag_name = String()

    def __init__(self, **kwargs):
        self._props = kwargs

    def insert(self):
        """ Insert tag to graph"""
        graph.tags.create(
            tag_id=self.tag_id,
            tag_name=self.tag_name
        )

    def link_to_book(self, book_id):
        """Create relationship (Tag)-[:TAGGED_TO]->(Book)"""
        book = graph.books.query(book_id=book_id).first()
        tag = graph.tags.query(tag_id=self.tag_id).first()
        graph.tagged_to.create(tag, book)


class TaggedTo(Relationship):
    label = "tagged_to"


class Read(Relationship):
    label = "reads"


class Follows(Relationship):
    label = "follows"


class Likes(Relationship):
    label = "likes"


def clear_graph():
    """ Clear all nodes and relationships """
    graph.drop("books")



