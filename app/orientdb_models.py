from pyorient.ogm import declarative
from pyorient.ogm.property import (String, Integer)
from passlib.hash import sha256_crypt
from .databases import OrientDataBase

Node = declarative.declarative_node()
Relationship = declarative.declarative_relationship()

client, graph = OrientDataBase.connect()


class User(Node):
    """Class for User node"""
    __primary_key__ = "username"
    element_plural = 'users'

    user_id = Integer()
    username = String()
    password = String()

    def find(self, username):
        query = "SELECT * FROM User WHERE username='%s'"
        record = client.command(query % username)
        return record

    def register(self, user_id, password, username):
        if not self.find(username):
            graph.users.create(user_id=user_id,
                               username=username,
                               password=sha256_crypt.encrypt(password)
                               )
            return True

        return False

    def verify_password(self, password, username):
        user = self.find(username)
        if not user:
            return False

        return sha256_crypt.verify(password, user[0].password)

    @staticmethod
    def users():
        """List of all users"""
        users = graph.users.query().all()
        return [user.username for user in users]

    @staticmethod
    def reads(user_id, book_id):
        """Create relationship (User)-[:READS]->(Book)"""
        user = graph.users.query(user_id=user_id).first()
        book = graph.books.query(book_id=book_id).first()
        graph.reads.create(user, book)
        return True

    @staticmethod
    def follows(user_id, friend_id):
        """Create relationship (User)-[:FOLLOWS]->(User)"""
        user = graph.users.query(user_id=user_id).first()
        friend = graph.books.query(friend_id=friend_id).first()
        graph.follows.create(user, friend)
        return True

    @staticmethod
    def likes(user_id, book_id):
        user = graph.users.query(user_id=user_id).first()
        book = graph.books.query(book_id=book_id).first()
        graph.likes.create(user, book)
        return True


class Book(Node):
    """Class for Book node"""
    element_plural = "books"
    registry_plural = "books"

    book_id = Integer()
    authors = String()
    publication = Integer()
    title = String()
    language = String()

    @staticmethod
    def add_book(book_id, authors, publication, title, language):
        graph.books.create(
                            book_id=book_id,
                            authors=authors,
                            publication=publication,
                            title=title,
                            language=language
                            )

        return True

    @staticmethod
    def books():
        """Returns list of all books"""
        books = graph.query(Book).all()
        return [book for book in books]

    @staticmethod
    def most_popular_books():
        """ Returns books which are read by most amount of users """
        query = """
                SELECT book_title, Count(tags)
                from (
                      MATCH {class: User, as: user}.in('reads') {as: book}
                      RETURN book.title, user
                )
                group by book_title
        """
        return graph.query(query)  # alright?

    @staticmethod
    def tags(book_id):
        """List of tags for specific book"""
        book = graph.books.query(book_id=book_id).first()
        tags = [tag.outV().tag_name for tag in book.inE()]
        return tags


class Tag(Node):
    """Class for Tag node"""
    element_plural = "tags"

    tag_id = Integer()
    tag_name = String()

    @staticmethod
    def add_tag(tag_id, tag_name):
        graph.tags.create(
            tag_id=tag_id,
            tag_name=tag_name
        )

        return True

    @staticmethod
    def tagged(book_id, tag_id):
        """Create relationship (Tag)-[:TAGGED_TO]->(Book)"""
        book = graph.books.query(book_id=book_id).first()
        tag = graph.tags.query(tag_id=tag_id).first()
        graph.tagged_to.create(tag, book)
        return True


class TaggedTo(Relationship):
    label = "tagged_to"


class Read(Relationship):
    label = "reads"


class Follows(Relationship):
    label = "follows"


class Likes(Relationship):
    label = "likes"


def clear_graph():
    graph.drop("books")
    return True


graph.include(Node.registry)
graph.include(Relationship.registry)
