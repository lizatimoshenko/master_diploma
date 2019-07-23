"""Implementation of models for Neo4J"""
from passlib.hash import sha256_crypt
from py2neo import Relationship
from py2neo.ogm import GraphObject, Property, RelatedTo, RelatedFrom

from app.databases import Neo4JDataBase

graph = Neo4JDataBase.connect()


class Book(GraphObject):
    """ Class for Book node """

    __primarykey__ = "book_id"

    book_id = Property()
    authors = Property()
    year = Property()
    title = Property()
    language = Property()

    tags = RelatedFrom("Tag", "TAGGED_TO")
    reader = RelatedFrom("User", "READS")
    likes = RelatedFrom("User", "LIKES")

    def __init__(self, book_id, authors, year, title, language):
        self.book_id = book_id
        self.authors = authors
        self.year = year
        self.title = title
        self.language = language

    def insert(self):
        """Inserting book node to graph"""
        graph.push(self)

    def linked_tags(self):
        """Return list of tags for specific book"""
        book = Book.match(graph, self.book_id).first()
        tags = [tag.tag_name for tag in book.tags]
        return tags

    @staticmethod
    def books():
        """ Return list of all books """
        books = graph.run("MATCH (b:Book) RETURN b.username").data()
        return books

    @staticmethod
    def most_popular_books():
        """ Return books which are read by most amount of users """
        query = """
                MATCH (book:Book)<-[reads:READS]-(u:User)
                WITH book, count(reads) AS readers
                RETURN book 
                ORDER BY readers  LIMIT 16
                """
        # TODO use run instead of cypher
        return graph.cypher.execute(query)


class User(GraphObject):
    """ Class for User node """

    __primarykey__ = "username"

    user_id = Property()
    username = Property()
    password = Property()

    books = RelatedTo("Book")
    liked_books = RelatedTo("Book")
    friends = RelatedTo("User")

    followers = RelatedFrom("User", "FOLLOWS")

    def __init__(self, username, password=None, user_id=None):
        self.user_id = user_id
        self.username = username
        self.password = password

    def find(self):
        """ Return user in database by username """
        user = User.match(graph, self.username).first()
        return user

    def insert(self, username, password, user_id):
        """ Insert user node to graph """
        if not self.find():
            self.username = username
            self.password = sha256_crypt.encrypt(password)
            self.user_id = user_id
            graph.push(self)
            return True

        return False

    def verify_password(self, password):
        """ Return if password is valid """
        user = self.find()
        if not user:
            return False
        return sha256_crypt.verify(password, self.password)

    def reads(self, book_id):
        """ Create relationship (User)-[:READS]->(Book) """
        book = Book.match(graph, int(book_id)).first()
        user = User.match(graph, self.user_id).first()
        graph.create(Relationship(user.__node__, "READS", book.__node__))

    def follows(self, friend_id):
        """ Create relationship (User)-[:FOLLOWS]->(User) """
        user = User.match(graph, self.user_id).first()
        friend = User.match(graph, int(friend_id)).first()
        graph.create(Relationship(user.__node__, "FOLLOWS", friend.__node__))

    def likes(self, book_id):
        """ Create relationship (User)-[:LIKES]->(Book) """
        user = User.match(graph, self.user_id).first()
        book = Book.match(graph, int(book_id)).first()
        graph.create(Relationship(user.__node__, "LIKES", book.__node__))

    @staticmethod
    def users():
        """ Return list of all users """
        return graph.run("MATCH (u:User) RETURN u.username").data()


class Tag(GraphObject):
    """ Class for Tag node """

    __primarykey__ = "tag_id"

    tag_id = Property()
    tag_name = Property()

    tagged_to = RelatedTo("Book")

    def __init__(self, tag_id, tag_name):
        self.tag_id = tag_id
        self.tag_name = tag_name

    def insert(self):
        """ Insert tag to graph"""
        graph.push(self)

    def link_to_book(self, book_id):
        """ Create relationship (Tag)-[:TAGGED_TO]->(Book) """
        book = Book.match(graph, int(book_id)).first()
        tag = Tag.match(graph, self.tag_id).first()
        graph.create(Relationship(tag.__node__, "TAGGED_TO", book.__node__))


def clear_graph():
    """ Clear all nodes and relationships """
    graph.delete_all()
