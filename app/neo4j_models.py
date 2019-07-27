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

    tagged_to = RelatedTo("Tag")

    reader = RelatedFrom("User", "READS")
    likes = RelatedFrom("User", "LIKES")

    def __init__(self, book_id=None, authors=None, year=None, title=None, language=None):
        self.book_id = book_id
        self.authors = authors
        self.year = year
        self.title = title
        self.language = language

    def insert(self):
        """Inserting book node to graph"""
        graph.push(self)

    def find_by_id(self):
        book = Book.match(graph, self.book_id).first()
        return book

    def linked_tags(self):
        """Return list of tags for specific book"""
        book = Book.match(graph, self.book_id).first()
        tags = [tag.tag_name for tag in book.tags]
        return tags

    def link_to_tag(self, tag_id):
        """ Create relationship (Book)-[:TAGGED_TO]->(Tag) """
        tag = Tag.match(graph, int(tag_id)).first()
        graph.create(Relationship(self.__node__, "TAGGED_TO", tag.__node__))

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

    __primarykey__ = "user_id"

    user_id = Property()
    username = Property()
    password = Property()

    books = RelatedTo("Book")
    liked_books = RelatedTo("Book")
    friends = RelatedTo("User")

    followers = RelatedFrom("User", "FOLLOWS")

    def __init__(self, user_id=None, username=None, password=None):
        self.user_id = user_id
        self.username = username
        self.password = password

    def find(self):
        """ Return user in database by username """
        user = User.match(graph, self.username).first()
        return user

    def insert(self):
        """ Insert user node to graph """
        # TODO password encryption in routes
        #if not self.find():
        graph.push(self)

    def verify_password(self, password):
        """ Return if password is valid """
        user = self.find()
        if not user:
            return False
        return sha256_crypt.verify(password, self.password)

    def reads(self, book_id):
        """ Create relationship (User)-[:READS]->(Book) """
        book = Book.match(graph, int(book_id)).first()
        graph.create(Relationship(self.__node__, "READS", book.__node__))

    def follows(self, friend_id):
        """ Create relationship (User)-[:FOLLOWS]->(User) """
        friend = User.match(graph, int(friend_id)).first()
        graph.create(Relationship(self.__node__, "FOLLOWS", friend.__node__))

    def likes(self, book_id):
        """ Create relationship (User)-[:LIKES]->(Book) """
        book = Book.match(graph, int(book_id)).first()
        graph.create(Relationship(self.__node__, "LIKES", book.__node__))

    @staticmethod
    def users():
        """ Return list of all users """
        return graph.run("MATCH (u:User) RETURN u.username").data()


class Tag(GraphObject):
    """ Class for Tag node """

    __primarykey__ = "tag_id"

    tag_id = Property()
    tag_name = Property()

    books = RelatedFrom("Book", "TAGGED_TO")

    def __init__(self, tag_id, tag_name=None):
        self.tag_id = tag_id
        self.tag_name = tag_name

    def insert(self):
        """ Insert tag to graph"""
        graph.push(self)


def clear_graph():
    """ Clear all nodes and relationships """
    graph.delete_all()
